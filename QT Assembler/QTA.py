# An assembler for a small computer
# A bit different from my previous TASL assembler
#
# First it cleans the whitespace and comments from around each line
# Next, it builds the label table using the non-empty lines
# Then, it creates the machine code output
# Finally, it formats the machine code into the .hex file format


import sys  # For taking user input from command line
from os.path import exists  # For checking if the input exists
from enum import Enum  # For line types
from random import choice  # For printing random output


# Input/output constants
EXPECTED_ARG_COUNT = 2
INPUT_FILE_ARG     = 1
FILE_INPUT_EXTENSIONS  = [".qta"]
FILE_OUTPUT_EXTENSION = ".hex"
HEX_FILE_HEADER = "v2.0 raw\n"

# Assembly dictionaries
reads_dict = {
    "a": 0,
    "b": 1,
    "in": 2,
    "io": 2,
    "[a]": 3,
    "pc": 4,
    "a+b": 5,
    "a-b": 6,
    "ram": 7,
    "mem": 7,
    "next": 7,
}
writes_dict = {
    "a": 0,
    "b": 1,
    "out": 2,
    "io": 2,
    "[a]": 3,
    "pc": 4,
    "pcif0": 5,
    "pcifz": 5,
    "pcif-": 6,
    "pcifn": 6,
    "pcifr": 7
}
special_lines_dict = {
    "hlt": 0x80,
    "swp": 0b11001100,

    "za":  0b11000000,
    "-a":  0b11000001,
    "a++": 0b11000010,
    "a--": 0b11000011,

    "zb":  0b11000100,
    "-b":  0b11000101,
    "b++": 0b11000110,
    "b--": 0b11000111,

    "zf":      0b11001000,
    "cmp a-b": 0b11001001,
    "cmp a+b": 0b11001010,
    "cmp b-a": 0b11001011
}

# Assembly Patterns
COMMENT_CHAR = '#'
CHARACTER_CHAR = "'"
BINARY_PREFIX = "0b"
HEX_PREFIX = "0x"
OP_CHAR = '>'
LABEL_CHAR = ':'
REFERENCE_CHAR = '$'
SET_FLAG_SUFFIX = "+cmp"
CONST_CHAR = '='
EMPTY_SPACE_PREFIX = "0*"
NEGATIVE_SIGN = '-'

INPUT_OP_SHIFT = 4
SET_FLAGS_MASK = 0b1000
HEX_PREFIX_SIZE = 2
NaN = 0x100
BITS_PER_WORD = 8

# Strings to print while running
CLEANING_QUIPS = ["Cleaning the input...", "Reticulating splines...", "Input being sanitized...",
                  "Sweeping the floors...", "House cleaning...", "Brushing off the strings..."]
BUILDING_QUIPS = ["Putting labels in the table...", "Building the table...", "Baking a pie...",
                  "Preparing for references...", "Enable stable label table...", "Collecting the labels..."]
ASSEMBLE_QUIPS = ["Assembling the output...", "Assembler time!...", "Who assembles the assembler?...",
                  "Translating code...", "Creating the machine code...", "Crunching the 1's and 0's..."]
FILE_OUT_QUIPS = ["Writing to output...", "Let's hope this works...", "Creating the output file...",
                  "It's the OS's turn now...", "Almost done...", "If it breaks its not my fault..."]
DONE_END_QUIPS = ["Done!", "Now you have TWO files!!", "So long and thanks for all the fish!",
                  "DFTBA!", "It worked!", "No errors! ...yet"]


# Types of lines for get_line_type
class LineType(Enum):
    VAL = 0
    OP = 1
    SPECIAL = 2
    REF = 3
    LABEL = 4
    CONST = 5
    SPACE = 6
    UNKNOWN = -1
    EMPTY = -2


def main() -> None:
    """The main function of the program."""

    # Get args
    args = sys.argv
    if len(args) != EXPECTED_ARG_COUNT:
        error("Expected " + str(EXPECTED_ARG_COUNT) + " args but got " + str(len(args)))

    # Check if input file is OK
    input_file_path = args[INPUT_FILE_ARG]
    extension = list(filter(input_file_path.endswith, FILE_INPUT_EXTENSIONS))
    if not extension:
        error("Bad input extension. Supported extensions: " + str(FILE_INPUT_EXTENSIONS))
    extension = extension[0]  # Redefine extension as the only file extension left (only one will match)
    if not exists(input_file_path):
        error("Input file not found.")

    # Do the assembling
    with open(input_file_path, 'r') as input_file:
        # Get the input lines
        lines = input_file.readlines()
        print(choice(CLEANING_QUIPS))
        cleaned_lines = clean_lines(lines)

        # Do the two passes and make the output lines
        print(choice(BUILDING_QUIPS))
        label_table = build_table(cleaned_lines)
        print(choice(ASSEMBLE_QUIPS))
        machine_code = assemble(cleaned_lines, label_table)
        print(choice(FILE_OUT_QUIPS))
        output_lines = hex_file_format(machine_code)

        # Write the output lines to the output file
        file_name = input_file_path[:-len(extension)]  # Remove the (only) file extension from the end
        output_file_path = file_name + FILE_OUTPUT_EXTENSION
        with open(output_file_path, 'w') as output_file:
            output_file.writelines(output_lines)

        # We're done!
        print(choice(DONE_END_QUIPS))


def build_table(input_lines: list[str]) -> dict:
    """Returns the label table for the given lines."""

    # Create the table and set the current address to 0
    table = {}
    address = 0

    # Loop through all the lines
    for line in input_lines:
        # Get the line's type
        line_type = get_line_type(line)

        match line_type:
            case LineType.LABEL:
                # If it's a label, add it to the table
                label = line[1:-1]
                table[label] = address

            case LineType.CONST:
                # If it's a constant, try to add its definition to the table
                parts = line.split('=')
                if len(parts) != 2:
                    error("Bad constant definition in line: " + line)

                label = parts[0].strip()
                value = get_value(parts[1].strip())
                if value is NaN:
                    error("Bad value in line: " + line)
                table[label] = value

            case LineType.SPACE:
                # If it's an empty space indicator, add its size to the address
                val = line[2:]
                value = get_value(val)
                if value is NaN:
                    error("Bad value for empty space indicator in line: " + line)
                address += value

            case LineType.UNKNOWN:
                # All lines should be of a known type, so error
                error("Unknown line type: " + line)

            case _:
                # Note: we are assuming here that any other line is 1 word. This might change!
                address += 1

    # Return the complete table once we're done
    return table


def assemble(input_lines: list[str], table: dict) -> list:
    """Returns the machine code for the given input lines, using the given label table."""

    # Create the output list
    output = []

    # Loop through each line
    for line in input_lines:
        # Check what the line type is
        line_type = get_line_type(line)

        match line_type:
            case LineType.VAL:
                # If it's a value line, get and append its value
                value = get_value(line)
                if value is NaN:
                    error("Not a valid value: " + line)
                output.append(value)

            case LineType.OP:
                # If it's an operation, get and append the machine code for the operation
                machine_code = translate_instruction(line)
                output.append(machine_code)

            case LineType.SPECIAL:
                # If it's special, append what the line translates to
                output.append(special_lines_dict[line.lower()])

            case LineType.REF:
                # If it's a reference, get and append the label's value from the table
                label = line[1:]
                if label not in table:
                    error("Reference label not found in line: " + line)
                output.append(table[label])

            case LineType.SPACE:
                # If it's empty space, make space by adding 0's to the output
                val = line[2:]
                value = get_value(val)
                if not value:
                    error("Bad value for array in line: " + line)
                zeros = [0 for _ in range(0, value)]
                output = output + zeros

            case LineType.UNKNOWN:
                # All lines should be of a known type, so error
                error("Unknown line type: " + line)

    return output


def hex_file_format(input_data: list[int]) -> list[str]:
    """Returns the .hex drive formatted version of the given data."""
    return [HEX_FILE_HEADER] + \
           [(hex(2 ** BITS_PER_WORD + line)[-2:] + '\n')
            for line in input_data]


def clean_lines(input_lines: list[str]) -> list[str]:
    """Removes all unimportant information from the given list of lines (comments, whitespace, etc.)."""

    # First, we make a function that defines what we mean by "clean lines."
    def line_cleaner(input_line: str) -> str:
        """Returns a clean version of the input line."""
        return input_line.split(COMMENT_CHAR)[0].strip()
    # Then, use map to get an iterator where each line has been ran through line_cleaner()
    # After that, filter returns an iterator containing only the lines where bool(line) == True (len(line) != 0)
    # Finally, we construct a list out of these non-empty, cleaned lines, and return that.
    return list(
        filter(bool,
               map(line_cleaner, input_lines)))


def get_line_type(line: str) -> LineType:
    """Returns the type of the given line."""

    if len(line) == 0:
        return LineType.EMPTY
    elif line.lower() in special_lines_dict:
        return LineType.SPECIAL
    elif OP_CHAR in line:
        return LineType.OP
    elif get_value(line) is not NaN:
        return LineType.VAL
    elif line[0] == REFERENCE_CHAR:
        return LineType.REF
    elif line[0] == line[-1] == LABEL_CHAR:
        return LineType.LABEL
    elif CONST_CHAR in line:
        return LineType.CONST
    elif line.startswith(EMPTY_SPACE_PREFIX):
        return LineType.SPACE

    else:
        return LineType.UNKNOWN


def get_value(value_lexeme: str) -> int:
    """Returns NaN if not a value lexeme, else returns its value."""
    is_negative = value_lexeme.startswith(NEGATIVE_SIGN)
    if is_negative:
        value_lexeme = value_lexeme[1:]

    if value_lexeme[0] == value_lexeme[-1] == CHARACTER_CHAR and len(value_lexeme) == 3:
        out = ord(value_lexeme[1])
    elif value_lexeme.startswith(HEX_PREFIX):
        out = int(value_lexeme, 16)
    elif value_lexeme.startswith(BINARY_PREFIX):
        out = int(value_lexeme, 2)
    elif value_lexeme.isnumeric():
        out = int(value_lexeme)

    else:
        return NaN

    if is_negative:
        return -out
    return out


def translate_instruction(instruction_line: str) -> int:
    """Returns the machine code for the given instruction line."""

    # Get the parameters for the operation
    raw_params = instruction_line.split(OP_CHAR)
    if len(raw_params) != 2:
        error("Bad operation in line: " + instruction_line)
    set_flags = raw_params[1].endswith(SET_FLAG_SUFFIX)
    if set_flags:
        raw_params[1] = raw_params[1][:-len(SET_FLAG_SUFFIX)]

    # Filter the two parameters
    in_part = raw_params[0].strip().lower()
    out_part = raw_params[1].strip().lower()

    # Make sure they actually exist before getting their values
    if in_part not in reads_dict:
        error("Bad input operand: " + instruction_line)
    if out_part not in writes_dict:
        error("Bad output operand: " + instruction_line)
    input_num = reads_dict[in_part]
    output_num = writes_dict[out_part]

    # Create & return the machine code given the two parameters' values
    machine_code = input_num << INPUT_OP_SHIFT | output_num
    if set_flags:
        machine_code = machine_code | SET_FLAGS_MASK
    return machine_code


def error(msg: str) -> None:
    """Prints the message and stops the program."""
    print(msg)
    exit(0)


main()

# An assembler for a small computer
#
# Does 2 passes on the file:
#   First pass builds the label table
#   Second pass builds the output
#
#


import sys  # For taking user input from command line
from os.path import exists
from enum import Enum


# Input constants
EXPECTED_ARG_COUNT = 2
INPUT_FILE_ARG     = 1

FILE_INPUT_EXTENSIONS  = [".qta"]
FILE_OUTPUT_EXTENSION = ".hex"

# Assembly dictionaries
inputs_dict = {
    "a": 0,
    "b": 4,
    "[a]": 1,
    "a+b": 2,
    "a-b": 3,
    "pc": 5,
    "in": 6,
    "ram": 7
}

outputs_dict = {
    "a": 0,
    "b": 1,
    "out": 2,
    "[a]": 3,
    "pc": 4,
    "pcif0": 5,
    "pcif-": 6,
    "pcifr": 7
}

special_lines_dict = {
    "hlt": 0x80
}


# Types of lines for get_line_type
class LineType(Enum):
    VAL = 0
    OP = 1
    SPECIAL = 2
    REF = 3
    LABEL = 4
    CONST = 5
    UNKNOWN = -1
    EMPTY = -2


# Assembly Patterns
COMMENT_CHAR = '#'
CHARACTER_CHAR = "'"
BINARY_SUFFIX = "0b"
HEX_SUFFIX = "0x"
OP_CHAR = '>'
LABEL_CHAR = ':'
REFERENCE_CHAR = '$'
HALT_LINE = "halt"
SET_FLAG_SUFFIX = "+f"
CONST_CHAR = '='

IN_OP_SHIFT = 4
SET_FLAGS_MASK = 0b1000

# Error messages
ERROR_SEPERATOR = "\n"

INIT_ERROR = 2
TABLE_ERROR = 3
ASSEMBLE_ERROR = 4
OTHER_ERROR = 5

BAD_ARG_COUNT_MSG = "Invalid number of arguments."
BAD_FILE_INPUT_MSG = "Invalid file input."
BAD_OP_COUNT_MSG = "Bad number of operands."
BAD_INPUT_OP_MSG = "Bad input operand."
BAD_OUTPUT_OP_MSG = "Bad output operand."
UNKNOWN_LINE_MSG = "Unintelligible line of code."
UNKNOWN_LABEL_MSG = "Label not found in table."


def init():
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
        cleaned_lines = clean_lines(lines)

        # Do the two passes and make the output lines
        label_table = build_table(cleaned_lines)
        machine_code = assemble(cleaned_lines, label_table)
        output_lines = hex_file_format(machine_code)

        # Write the output lines to the output file
        file_name = input_file_path[:-len(extension)]  # Remove the (only) file extension from the end
        output_file_path = file_name + FILE_OUTPUT_EXTENSION
        with open(output_file_path, 'w') as output_file:
            output_file.writelines(output_lines)


def build_table(input_lines):
    """Returns the label table for the given lines."""

    # Create the table and set the current address to 0
    table = {}
    address = 0

    # Loop through all the lines
    for line in input_lines:
        # Get the line's type
        line_type = get_line_type(line)

        # If it's a label, add it to the table
        if line_type == LineType.LABEL:
            label = line[1:]
            table[label] = address

        # If it's a constant, try to add its definition to the table
        elif line_type == LineType.CONST:
            parts = line.split('=')
            if len(parts) != 2:
                error("Bad constant definition in line: " + line)

            label = parts[0].strip()
            value = get_value_if_value(parts[1].strip())
            if value:
                table[label] = value
            else:
                error("Bad value in line: " + line)

        else:
            # Note: we are assuming here that any other line is 1 word. This might change!
            address += 1

    return table


def assemble(input_lines, table):
    """Returns the machine code for the given input lines, using the given label table."""

    output = []

    # code here pls :)

    return output


def hex_file_format(input_data):
    """Returns the .hex drive formatted version of the given data."""

    lines = []

    # code here pls :)

    return lines


def clean_lines(input_lines):
    """Returns a cleaner set of lines to work with."""

    return list(
        filter(bool,
               map(line_cleaner, input_lines)))


def line_cleaner(input_line):
    """Returns a clean version of the input line, or returns false if cleaned line is empty."""

    out_line = input_line.split(COMMENT_CHAR)[0].strip()
    if len(out_line) == 0:
        return False
    else:
        return out_line


def get_line_type(line):
    """Returns the type of the line"""

    if len(line) == 0:
        return LineType.EMPTY
    elif OP_CHAR in line:
        return LineType.OP
    elif get_value_if_value(line):
        return LineType.VAL
    elif line[0] == REFERENCE_CHAR:
        return LineType.REF
    elif line[0] == line[-1] == LABEL_CHAR:
        return LineType.LABEL
    elif line in special_lines_dict:
        return LineType.SPECIAL
    elif CONST_CHAR in line:
        return LineType.CONST
    else:
        return LineType.UNKNOWN


def get_value_if_value(value_lexeme):
    """Returns False if not a value lexeme, else returns its value"""

    if value_lexeme[0] == value_lexeme[-1] == CHARACTER_CHAR and len(value_lexeme) == 3:
        return ord(value_lexeme[1])
    elif value_lexeme.startswith(HEX_SUFFIX):
        return int(value_lexeme, 16)
    elif value_lexeme.startswith(BINARY_SUFFIX):
        return int(value_lexeme, 2)
    elif value_lexeme.isnumeric():
        return int(value_lexeme)
    else:
        return False


def translate_instruction(instruction_line):
    """Returns the machine code for the given instruction line."""

    raw_args = instruction_line.split(OP_CHAR)

    if len(raw_args) != 2:
        error("Bad operation in line: " + instruction_line)

    args = []
    args[0] = raw_args[0].strip().lower()
    args[1] = raw_args[1].strip().lower()

    if args[0] not in inputs_dict:
        error("Bad input operand: " + instruction_line)

    if args[1] not in outputs_dict:
        error("Bad output operand: " + instruction_line)

    input_num = inputs_dict[args[0]]
    output_num = outputs_dict[args[1]]

    machine_code = input_num << IN_OP_SHIFT | output_num
    if args[1].endswith(SET_FLAG_SUFFIX):
        machine_code = machine_code | SET_FLAGS_MASK

    return machine_code


def label_lookup(reference, table):
    """Returns the value of the given reference."""

    label = reference[1:]
    if label in table:
        return table[label]
    else:
        error("Label for reference not found: " + reference)


def error(msg):
    """Prints the message and stops the program."""

    print(msg)
    exit(0)


init()

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


class LineType(Enum):
    VAL = 0
    OP = 1
    SPECIAL = 2
    REF = 3
    LABEL = 4
    CONST = 5
    UNKNOWN = -1


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

IN_OP_SHIFT = 4
SET_FLAGS_MASK = 0b1000


# For get_line_info
MACHINE_CODE = 1
WORD_COUNT = 0

BAD_LINE_WORD = -1
MULTI_MC = -3
UNKNOWN_MC = -2
EMPTY_MC = -1


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
    args = sys.argv
    if len(args) != EXPECTED_ARG_COUNT:
        specific_msg = "Expected args: " + str(EXPECTED_ARG_COUNT)
        error(BAD_ARG_COUNT_MSG, specific_msg, INIT_ERROR)

    input_file_path = args[INPUT_FILE_ARG]
    # Genius solution by https://www.geeksforgeeks.org/python-check-if-string-ends-with-any-string-in-given-list/
    # Does maybe_file_path.endswith() using all elements of FILE_INPUT_EXTENSIONS
    # If it doesn't find anything, the list will (somehow) be/return false.
    extension = list(filter(input_file_path.endswith, FILE_INPUT_EXTENSIONS))
    if not extension:
        specific_msg = "Supported extensions: " + str(FILE_INPUT_EXTENSIONS)
        error(BAD_FILE_INPUT_MSG, specific_msg, INIT_ERROR)

    if not exists(input_file_path):
        specific_msg = "File not found."
        error(BAD_FILE_INPUT_MSG, specific_msg, INIT_ERROR)

    with open(input_file_path, 'r') as input_file:
        lines = input_file.readlines()

        label_table = build_table(lines)
        machine_code = assemble(lines, label_table)
        output_lines = hex_file_format(machine_code)

        file_name = input_file_path[:-len(extension[0])]  # Remove the (only) file extension from the end
        output_file_path = file_name + FILE_OUTPUT_EXTENSION
        with open(output_file_path, 'w') as output_file:
            output_file.writelines(output_lines)


def build_table(input_lines):
    """Builds and returns the label table for the given lines."""
    table = {}

    for line in input_lines:
        get_line_info(line)

    return table


def assemble(input_lines, table):
    """Returns the machine code for the given input lines, using the given label table"""
    output = []


def get_line_type(line):
    """Returns the type of the line"""
    real_line = line.split(COMMENT_CHAR)[0].strip()  # Remove comments & whitespace
    if len(real_line) != 0:
        if OP_CHAR in real_line:
            # Is an operation
            args = real_line.split(OP_CHAR)
            if len(args) != 2:
                specific_msg = "Bad operation in line: " + line
                error(BAD_OP_COUNT_MSG, specific_msg, ASSEMBLE_ERROR)

            if args[0] not in inputs_dict:
                specific_msg = "Bad input operand: " + line
                error(BAD_INPUT_OP_MSG, specific_msg, ASSEMBLE_ERROR)

            if args[1] not in outputs_dict:
                specific_msg = "Bad output operand: " + line
                error(BAD_OUTPUT_OP_MSG, specific_msg, ASSEMBLE_ERROR)

            input_num = inputs_dict[args[0]]
            output_num = outputs_dict[args[1]]

            machine_code = input_num << IN_OP_SHIFT | output_num
            if args[1].endswith(SET_FLAG_SUFFIX):
                machine_code = machine_code | SET_FLAGS_MASK

            out = (1, machine_code)

        elif real_line[0] == real_line[-1] == CHARACTER_CHAR and len(real_line) == 3:
            # Is character
            out = (1, ord(real_line[1]))

        elif real_line.startswith(HEX_SUFFIX):
            # Is hex number
            out = (1, int(real_line, 16))

        elif real_line.startswith(BINARY_SUFFIX):
            # Is binary number
            out = (1, int(real_line, 2))

        elif real_line.isnumeric():
            # Is decimal number
            out = (1, int(real_line))

        elif real_line[0] == REFERENCE_CHAR:
            # Is a reference
            out = (1, UNKNOWN_MC)

        elif real_line[0] == real_line[-1] == LABEL_CHAR:
            # Is a label, do nothing
            out = (0, EMPTY_MC)

        elif real_line in special_lines_dict:
            # Is a special line
            out = (1, special_lines_dict[real_line])

        else:
            # Unknown line of code
            out = (BAD_LINE_WORD,EMPTY_MC)
    return out


def hex_file_format(input_data):
    """Returns the .hex drive formatted version of the given data"""
    lines = []
    # code here pls :)

    return lines


def label_lookup(reference, table):
    label = reference[1:]
    if label in table:
        return table[label]
    else:
        error(UNKNOWN_LABEL_MSG, reference, OTHER_ERROR)


def error(generic_message, specific_message, exit_code):
    print(generic_message + ERROR_SEPERATOR + specific_message)
    exit(exit_code)


init()

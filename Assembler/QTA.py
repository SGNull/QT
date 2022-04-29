# An assembler for a small computer
#
# Does 2 passes on the file:
#   First pass builds the label table
#   Second pass builds the output
#
#


import sys  # For taking user input from command line


# Input constants
EXPECTED_ARG_COUNT = 2
INPUT_FILE_ARG     = 1

FILE_INPUT_EXTENSIONS  = [".qta"]
FILE_OUTPUT_EXTENSION = ".hex"

# Assembly Patterns
COMMENT_CHAR = '#'
CHARACTER_CHAR = "'"
BINARY_SUFFIX = "0b"
HEX_SUFFIX = "0x"
OP_CHAR = ">"

# Error messages
MSG  = 0
CODE = 1

BAD_ARG_COUNT = ("Invalid number of arguments. Expected number of arguments:" + str(EXPECTED_ARG_COUNT - 1), 2)
BAD_FILE_INPUT = ("Invalid file input. Supported file extensions:" + str(FILE_INPUT_EXTENSIONS), 2)


def init():
    args = sys.argv
    if len(args) != EXPECTED_ARG_COUNT:
        error(BAD_ARG_COUNT)

    input_file_path = args[INPUT_FILE_ARG]
    # Genius solution by https://www.geeksforgeeks.org/python-check-if-string-ends-with-any-string-in-given-list/
    # Does maybe_file_path.endswith() using all elements of FILE_INPUT_EXTENSIONS
    # If it doesn't find anything, the list will (somehow) be/return false.
    extension = list(filter(input_file_path.endswith, FILE_INPUT_EXTENSIONS))
    if not extension:
        error(BAD_FILE_INPUT)

    with open(input_file_path, 'r') as input_file:
        file_name = input_file_path[:-len(extension[0])]  # Remove the (only) file extension from the end
        output_file_path = file_name + FILE_OUTPUT_EXTENSION

        with open(output_file_path, 'w') as output_file:
            lines = input_file.readlines()

            label_table = build_table(lines)
            machine_code = assemble(label_table, lines)
            output_lines = hex_file_format(machine_code)

            output_file.writelines(output_lines)


def build_table(input_lines):
    table = {}

    # code here pls :)

    return table


def assemble(table, input_lines):
    output = []

    for line in input_lines:
        real_line = line.split(COMMENT_CHAR)[0].strip()  # Remove comments & whitespace
        if len(real_line) != 0:

            if OP_CHAR in real_line:
                # Is an operation
                args = real_line.split(OP_CHAR)
                if len(args) != 2:
                    error(("Bad operation:" + line, 3))

            elif real_line[0] == CHARACTER_CHAR:
                # Is character

            elif real_line.startswith(HEX_SUFFIX):
                # Is hex number

            elif real_line.startswith(BINARY_SUFFIX):
                # Is binary number

            elif int(real_line):
                # Is decimal number

            elif real_line[0] == REFERENCE_CHAR:
                # Is a reference

            elif real_line[0] == LABEL_CHAR:
                # Is a label

            elif real_line[0] == HALT_CHAR:
                # Halt
                output.append(0x80)

            else:
                error(("Unintelligible line of code:" + line, 4))

    return output


def hex_file_format(input_data):
    lines = []

    # code here pls :)

    return lines


def error(error_tuple):
    print(error_tuple[MSG])
    exit(error_tuple[CODE])


init()

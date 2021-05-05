import datetime
import pytz
import sys
import os

#
# Zepto Linker
#
# @author  Rafael Campos Nunes
# @date    29/04/2021
# @version 0.7
#
# Reads a .z file and outputs a .dsr file that is compatible with Deeds ROM
# software module. The zepto processor reads from a ROM that has a capacity of
# 128 bytes only (4096 instructions of 32 bits each)
#

# These opcodes are written in hexadecimal
opcodes = {
    "addi": '0000',
    "subi": '0001',
    "andi": '0002',
    "ori":  '0003',
    "xori": '0004',
    "beq":  '0005',
    "bleu": '0006',
    "bles": '0007',
}

_registers_name = ['R' + str(number) for number in range(15)]
_registers_addr = [bin(number)[2:].zfill(4) for number in range(15)]

registers = dict(zip(_registers_name, _registers_addr))


def main():
    # The file used to read instructions from the Zepto assembly language.
    input_name = sys.argv[1]

    # contains the instructions of the program that will be transformed
    output_content = ""
    output_name = input_name.split(".")[0] + ".dsr"

    with open(input_name, 'r') as fd:
        for line in fd:
            output_content += parse(line)

    print(output_content)

    # create read/write only and trunc the file if it already exists.
    with open(output_name, 'w+') as fd:
        fd.write(output_content)


def parse(line):
    parsed = ""

    if not (line.startswith('#') or line.startswith('\n')):
        data = line.split(" ")

        opcode = data[0]
        operands = data[1].split(",")

        print('opcode % -> operands %', opcode, operands)

        parsed += opcodes[opcode]

        for operand in operands:
            try:
                parsed += " " + registers[operand]
            except KeyError:
                if operand.isnumeric():
                    parsed += " " + hex(int(operand))[2:].zfill(4)

    if len(parsed) > 0:
        return parsed + "\n"

    return parsed


def header(size):
    tz = pytz.timezone('Brazil/East')
    date = datetime.datetime.now(tz)

    now = date.strftime("%D %H:%M:%S")

    data = '''
        # Zepto Linker
        #
        # program created at ''' + now + '''
        # program has ''' + size + ''' bytes
        #
        #
        #
    '''

    return data


if __name__ == "__main__":
    main()

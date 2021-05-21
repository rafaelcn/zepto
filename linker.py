import datetime
import pytz
import sys

#
# Zepto Linker
#
# @author  Rafael Campos Nunes
# @date    29/04/2021
# @version 1.0
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
_registers_addr = [hex(number)[2:].zfill(4) for number in range(15)]

registers = dict(zip(_registers_name, _registers_addr))


def main():
    # The file used to read instructions from the Zepto assembly language.
    input_name = sys.argv[1]

    zepto_instructions = []
    zepto_immediate = []
    zepto_instructions_size = 0

    with open(input_name, 'r') as fd:
        for line in fd:
            # filtering parseable lines
            if not (line.startswith('#') or line.startswith('\n')):
                zins, zimm = zepto_parse(line)

                zepto_instructions += zins
                zepto_immediate += zimm

    build(input_name, zepto_instructions)
    build(input_name, zepto_immediate, True)


def zepto_parse(line):
    '''
    Parses a line of instructions into the .DRS format.
    '''

    parsed = []
    data = line.strip('\n').split(' ')

    opcode_mnemonic = data[0]
    operands_mnemonic = data[1].split(",")

    # The immediate is the last argument of a call, but some instructions
    # doesn't have any.
    immediate = []
    if len(operands_mnemonic) > 0:
        number = int(operands_mnemonic[-1])
        if number < 0:
            # convert the immediate as a two's complement
            number = (1 << 16) + number
        hex_number = f'{int(number):X}'.zfill(8)
        immediate.append(hex_number[0:4])
        immediate.append(hex_number[4:8])

    opcode = opcodes[opcode_mnemonic]
    parsed.append(opcode)

    for operand in operands_mnemonic[:-1]:
        parsed.append(registers[operand])

    # reversing the list so the generated assembly language code can be
    # understood by the processor as specified in the documentation.
    parsed.reverse()

    padd = ' '*(25-pad(operands_mnemonic))
    formatted = 'opcode {:4} -> operands {}{} -> {}'.format(opcode_mnemonic,
                                                            operands_mnemonic,
                                                            padd,
                                                            parsed)
    print(formatted, immediate)

    return parsed, immediate


def zepto_header(size):
    tz = pytz.timezone('Brazil/East')
    date = datetime.datetime.now(tz)

    now = date.strftime("%D %H:%M:%S")

    data = '''
#- Zepto Linker
#-
#- Program created at ''' + now + '''
#- Program has ''' + str(size) + ''' bytes (program without ROM padding)
#-
#- ROM 4Kx16
#-\n
'''

    return data


def build(name, instructions, is_immediate=False):
    '''
    Constructs a working program to the Zepto processor. It takes an input and
    writes that output according to the specified ROM format of Deeds
    '''
    file_name = name.split(".")[0]

    if is_immediate:
        file_name += "_immediate.drs"
    else:
        file_name += ".drs"

    output_program = ""
    output_program += zepto_header(len(instructions)*2)

    j = 1
    for i in range(0, len(instructions)):
        output_program += instructions[i] + " "

        if j % 8 == 0:
            output_program += "\n"
            j = 0
        j += 1

    # create read/write only and trunc the file if it already exists.
    with open(file_name, 'w+') as fd:
        fd.write(output_program)


def pad(list):
    '''
    Return a number representing the amount of padding necessary to format
    '''

    # [] + ''*len(list)
    n = 2 + 2*len(list)

    if len(list) > 0:
        # spaces + commas
        n += 2*(len(list)-1)

    for e in list:
        if e.isnumeric():
            if e == 0:
                size = 1
            else:
                size = len(e)
        else:
            # assume it is a string list
            size = len(e)

        n += size

    return n


if __name__ == "__main__":
    main()

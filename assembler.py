import datetime
import pytz
import sys

#
# Zepto Assembler
#
# @author  Rafael Campos Nunes
# @date    29/04/2021
# @version 1.1
#
# Reads a .z file and outputs a .dsr file that is compatible with Deeds ROM
# software module. The zepto processor reads from a ROM that has a capacity of
# 128 bytes only (4096 instructions of 32 bits each)
#

# These opcodes are written in hexadecimal
opcodes = {
    "addi": '0',
    "subi": '1',
    "andi": '2',
    "ori":  '3',
    "xori": '4',
    "beq":  '5',
    "bleu": '6',
    "bles": '7',
}

_registers_name = ['R' + str(number) for number in range(16)]
_registers_addr = [f'{number:X}' for number in range(16)]

registers = dict(zip(_registers_name, _registers_addr))


def main():
    # The file used to read instructions from the Zepto assembly language.
    input_name = sys.argv[1]

    zepto_instructions = []
    zepto_immediate = []

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

    addi Rd, Ra, Rb, Imm -> Rd = Ra + Rb + Imm

    subi R1, R0, R0, 16
    addi R2,R0,R0,16

    Imm  Rd Ra Rb Opcode
    0010 1  0  0  1      -> 0x0010 0x1001
    0010 2  0  0  0      -> 0x0010 0x2000
    '''
    parsed = []
    data = line.strip('\n').split(' ')

    opcode_mnemonic = data[0]
    registers_mnemonic = data[1].split(",")[:-1]
    immediate_mnemonic = data[1].split(",")[-1]

    # The immediate is the last argument of a call, but some instructions
    # doesn't have any.
    immediate = []
    number = int(immediate_mnemonic)
    if number < 0:
        # convert the immediate as a two's complement
        number = (1 << 16) + number
    immediate.append(f'{int(number):X}'.zfill(4))

    if len(registers_mnemonic) > 2:
        parsed.append(registers[registers_mnemonic[0]])
        parsed.append(registers[registers_mnemonic[1]])
        parsed.append(registers[registers_mnemonic[2]])
    else:
        parsed.append('0')
        parsed.append(registers[registers_mnemonic[0]])
        parsed.append(registers[registers_mnemonic[1]])

    opcode = opcodes[opcode_mnemonic]
    parsed.append(opcode)

    parsed = [str.join('', parsed)]

    padd = ' '*(25-pad(registers_mnemonic))
    formatted = 'opcode {:4} -> operands {}{} -> {}'.format(opcode_mnemonic,
                                                            registers_mnemonic,
                                                            padd,
                                                            parsed)
    print(formatted, immediate)

    return parsed, immediate


def zepto_header(size):
    tz = pytz.timezone('Brazil/East')
    date = datetime.datetime.now(tz)

    now = date.strftime("%D %H:%M:%S")

    data = '''#- Zepto Assembler
#-
#- Program created at ''' + now + '''
#- Program has ''' + str(size) + ''' bytes (program without ROM padding)
#-
#- ROM 4Kx16
#-\n\n
#A 0000h
#H\n\n
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

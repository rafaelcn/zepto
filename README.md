# The Zepto

The zepto processor is a small 16 bit educational processor that is implemented using Deeds software.

# Circuitry

The circuits of the processor can be open using the Deeds DcS (Digital Circuit
Simulator). If you want to execute a specific program you will have to modify
the ROM (the memory.cbe block) input data in order to have the right program
loaded.

# The assembly language

Zepto is powered by a small assembly language. All available opcodes are listed
in the table below.


| opcode | Description                  |
| ------ | ---------------------------  |
| addi   | Add with immediate           |
| subi   | Subtract with immediate      |
| andi   | And bitwise with immediate   |
| ori    | Or bitwise with immediate    |
| xori   | Xor bitwise with immediate   |
| beq    | Conditional jump             |
| bleu   | Conditional jump (Unsigned)  |
| bles   | Unconditional jump (Signed)  |

There's a collection of programs inside the `programs` folder. Zepto programs
(in its own assembly language) are sufixed with the `.z` extension, you can open
them in any text editor of your choice to read its content. Note that the linker
is in its **early stages** of development and it might not be fully compliant,
yet.

# Linking

The linker provides easy creation of compliant zepto programs with the Deeds
ROM specific format (.dsr). If you want to link some program all you have to do
is to execute the linker with Python (>= 3.6) as shown below.

```
python3 linker.py ./programs/sum.z
```

After the execution you will be able to the see the generated ROM file inside
the programs folter with the right format (`sum.dsr`).





# ECE554 (Digital Engineering Laboratory) Assembler

Mason Berres, Moubarak Jeje, Anna Iwanski, Andrew Janssen, Braydon Friar, Charles Stock

This is our assembler used to compile assembly programs for our audio processor.

## Installation

### Prerequisites

Requires Python 3.6+ and the python 'bitstring' package.

https://www.python.org/downloads/

`pip3 install bitstring`

### Assembler

`git clone https://github.com/masranber/ece554-assembler.git`

`cd ece554-assembler`

## Usage

### Basic
`python3 assembler.py <source filepath>`

Will generate an object file (.o) with the same as the source file in the current directory.

#### Example
`python3 assembler.py program.asm` will produce `program.o` upon successful compilation

### Advanced
Specify a custom output path for the object file:

`python3 assembler.py <source filepath> -o <output path>`

The output path directory structure must exist. The path may be relative or absolute.

#### Example
`python3 assembler.py program.asm -o build/program.o` will produce `program.o` in the directory `build`

## Assembly Language Syntax

### Instructions

#### Registers

`$<register name>` ex: `$R0`

General purpose (GP) register names: `R0`,`R1`,`R2`,`R3`,`R4`,`R5`,`R6`,`R7`

Vector dot product (VDOT) register names: `V0`,`V1`,`V2`,`V3`,`V4`,`V5`,`V6`,`V7`

#### Immediates

`#<immediate value>` ex: `#-20` (decimal) `#0xF0` (hex)

Immediate values may be written in decimal, hex, octal, or binary. Values specified in decimal are assumed to be signed (they will be sign extended during compilation).

A label may be used in place of an immediate if the instruction supports symbols (jump and branch).


### Comments

#### Line

`; <comment>` ex: `; this is a comment`

#### Multiline (block)

```
/*
<comment>
*/
```

Block comments are opened at `/*` and terminated at `*/`. Nested comments are NOT supported.

### Labels

`<label name>:` ex: `START:`

Labels assign a name to memory address in the TEXT segment that can used in jump and branch instructions. Labels must be defined on their own line.

### Directives

Directive names are case-INSENSITIVE.

#### Entry Point
`.entry <address>` ex: `.entry 0x0000` (hex)

Specifies the address in memory where the program will be loaded. Required to reference global symbols. Address may be in decimal, hex, octal, or binary.

#### Segment
`.segment <segment name>` ex: `.segment TEXT`

`TEXT`: Memory segment where all instructions (code) should be placed.

`DATA`: Memory segment where all initialized global variables should be placed.

A segment includes everything from immediately after the segment directive to immediately before the next valid segment directive. Instructions and global variables defined in the wrong section will produce an assembler error at compile time.

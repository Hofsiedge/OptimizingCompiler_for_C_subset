# Optimizing Compiler for a C subset
A project implemented at Summer Practice: subset of C -> [Netwide Assembler (NASM)](https://www.nasm.us/) compiler. Parser - [ANTLR 4](https://www.antlr.org/), Python 3 logic. The target machine is 32-bit.

The C subset includes:
* integer variable declaration
* assignment
* simple arithmetic operations ( `+`, `-`, `*`, `/`, parentheses )
* while loops (only with `<`, `>`, `<=`, `>=`, `==`, `!=` operators)

The optimization is register allocation by graph colouring described in ['Advanced Compiler Design and Implementation' by Steven Muchnick](https://books.google.ru/books/about/Advanced_Compiler_Design_Implementation.html?id=Pq7pHwG1_OkC&redir_esc=y)

## How does it work
* First, the soure code is parsed with ANTLR 4 grammar contained in C.g4 file (and in structure.g4 as well, the only difference is that structure.g4 has no semantics, it provides only the parsing tree) into a parse tree
* During the parsing: 
  * some semantic attributes are being computed (e.g. `value` in `LITERAL` syntax rule)
  * A symbol table is being filled (a symbol table maps variable or constant name to the variable object or Python int respectively)
  * All the operations are aggregated in `CParser.flow_graph`'s `BasicBlock`s (a `BasicBlock` is just a maximal linear segment of a flow graph)
* After the parsing:
  * flow graph blocks are expanded to form definition-usage graph
  * then `du-chain`s are extracted from du-graph (`du-chain` starts with some definition and includes all the usages of the same variable it can reach)
  * intersecting `du-chain`s with identical symbol (variable) are joined into `Web`s
  * an interference graph is built over `Web`s (webs are adjacent only if they exist simultaneously)
  * colouring of the graph corresponds to register allocation, so we can set three of the most frequently used colours to  `ebx`, `ecx` and `edx` registers and treat other colours as 'symbolic registers' which are just 32-bit variables
  * then the registers (real and 'symbolic' ones) are assigned to corresponding definitions, and that's the register allocation
  * the last step is printing out code snippets generated for each operation

## How to use
1. Install ANTLR4, Java and Python 3
2. `cd` to the compiler directory
3. Run `gen` to generate parser and lexer files
4. Run `make` to compile all the .c files from `test_dir\source` to .asm files in  `test_dir\compiled`
5. If you have [SASM](https://dman95.github.io/SASM/english.html) installed, you can run `open_tests` to open all .asm files in `set_dir\compiled` in SASM (you may need to change the path to SASM in open_tests.bat)
6. Run `clean` to clean up target directories

## Examples
Simple arithmetics:
```C
int const A = 10;

int main() {

    int a = 2 * (1);
    int b = 2 * a * 3;
    int c = b - 4 * a * 2 + 10;
    int d = a + b * c + a;

    return 0;
}
```
The code above is compiled into
```
%include "io.inc"

section .bss
__temp: resd 1

section .text
global CMAIN
CMAIN:
	MOV ebp,	esp             ; for correct debugging

	MOV ebx,	2               ; 2 * (1) and is computed in parser
                            		; ebx is for a now

	MOV eax,	2
	IMUL ebx                  	; 2 * a


	MOV dword [__temp], 3     	; save 3 into a temporary variable
	IMUL 	dword [__temp]      	; and multiply 2 * a by 3


	MOV ecx,	eax             ; ecx is for b now


	MOV eax,	4
	IMUL ebx                  	; 4 * a


	MOV dword [__temp], 2 
	IMUL 	dword [__temp]      	; 4 * a * 2



	MOV dword [__temp], eax
	MOV eax,	ecx
	SUB eax,	dword [__temp]  ; b - 4 * a * 2


	ADD eax,	10              ; b - 4 * a * 2 + 10


	MOV edx,	eax             ; edx is for c now


	MOV eax,	ecx
	IMUL edx                  	; b * c


	MOV dword [__temp], eax
	MOV eax,	ebx
	ADD eax,	dword [__temp]  ; a + b * c


	ADD eax,	ebx             ; a + b * c + a


	MOV ebx,	eax             ; ebx is for d now since a is not used anymore


	MOV eax,	0
	RET                       	; return 0
```

(comments are written after the compilation just to make it more understandable)

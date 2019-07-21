grammar C;

options 
{
    language=Python3;
}

@header {
from nametable import SymbolTable, Int, Const, UnknownIDException
from graph_colouring import colour_graph
from tokens import *
from operation_utils import * # BasicBlock, Definition, Usage, DUChain, InterferenceGraph
}

@members {
name_table  = SymbolTable()
code        = ''                            # generated code
loops       = 0                             # current amount of loops
du_chains   = []                            # list of definition-usage chains
webs        = []                            # list of webs
flow_graph  = [BasicBlock()]                # graph of basic-blocks (linear in this case)
operations  = flow_graph[0].operations      # list of operations
eax         = EAX()
}

source_code
@after {
debug = True


du_graph = DUNode.from_flowgraph(CParser.flow_graph)
du_chains = DUChain.build_chains(du_graph)

webs    = Web.from_chains(du_chains)
mapping = dict(enumerate(webs))

interference_graph = InterferenceGraph(du_graph, webs)
colour_lists, priorities, registers = interference_graph.colour()
interference_graph.allocate(colour_lists, priorities, registers)

print('%include "io.inc"\n\nsection .bss')
for var in (registers[3:] if len(registers) > 3 else []):
    print(f'{var}: resd 1')
print('__temp: resd 1')
print('\nsection .text\nglobal CMAIN\nCMAIN:\n\tMOV ebp,\tesp; for correct debugging')



for block in CParser.flow_graph:
    for op in block.operations:
        print(op.code)


if type(CParser.flow_graph[-1].operations[-1]) != RET:
    print('\tmov eax,\t0\n\tret')
    
if debug:
    for block in CParser.flow_graph:
        print(f'\n; {block},\tl: {block.left},\tr: {block.right}')
        print('; <' + '-' * 20 + '>')
        for operation in block.operations:
            print('; ', type(operation), '\t', operation, '\t', operation.du)

    print('\n; du-chains:')
    for chain in du_chains:
        print('; ', chain)
    print('\n; Webs: ', webs)
    print("\n; Mapping: ", mapping)
    print('\n; Colours: ', colour_lists)
    """
    print('\n; Adjacency list: ')
    for key in adj_list:
        print('; ', key, adj_list[key])
    print('\n; Colour_lists:\n; ', colour_lists)
    for colour in colour_lists:
        print('\n; ', colour, sum([len(mapping[i].nodes) + 1 for i in colour_lists[colour]]))
    """
    print(f'\n; priorities: {priorities}')
    print(f'\n; registers: {registers}')


}
    : ( const_declaration      
      | variable_declaration
      )* function_declaration+
    ;

expr
    returns [value, simplex, is_literal]
    : '(' expr ')'  {$value = $expr.value}
    | return_expr
    // | conditional_expr
    // | '++'  expr
    // | '--'  expr
    // | expr  '++'
    // | expr  '--'
    // | '-'   expr
    // | '~'   expr
    // | '!'   expr
    | l=expr  operator=(MUL | DIV)     r=expr                       {$l.value.in_stack = not ($l.simplex or $r.simplex)}
                                                                    {cls = MUL if $operator.text == '*' else DIV}
                                                                    {op = cls($l.value, $r.value, CParser.eax)}
                                                                    {CParser.operations.append(op)}
                                                                    {$value, $simplex = op, $l.is_literal and $r.is_literal}

    | l=expr  operator=(ADD | SUB)     r=expr                       {$l.value.in_stack = not ($l.simplex or $r.simplex)}
                                                                    {cls = ADD if $operator.text == '+' else SUB}
                                                                    {op = cls($l.value, $r.value, CParser.eax)}
                                                                    {CParser.operations.append(op)}
                                                                    {$value, $simplex = op, $l.is_literal and $r.is_literal}
    // | l=expr  '&&'    r=expr
    // | l=expr  '||'    r=expr
    // | expr  '?'     expr    ':'     expr
    | ID    '='     expr                                            {entity = CParser.name_table[$ID.text]                                      }
                                                                    {if entity is None or not entity.mutable:                                   }
                                                                    {   raise UnknownIDException($ID.text)                                      }
                                                                    {CParser.name_table.rewrite_var($ID.text)}
                                                                    {op = Assign(CParser.name_table[$ID.text].var, $expr.value, CParser.eax)}
                                                                    {CParser.operations.append(op)}
                                                                    {$value, $simplex = op, True}
    
    | ID    '('    (expr   (','     expr)*) ')'                     // function call placeholder
    
    | ID                                                            {if CParser.name_table[$ID.text] is None:                                   }
                                                                    {   raise UnknownIDException($ID.text)                                      }
                                                                    {entity     = CParser.name_table[$ID.text]                                      }
                                                                    {$value     = entity.var if entity.mutable else entity.value}
                                                                    {$simplex   = True}
                                                                    
    | literal                                                       {$value, $simplex, $is_literal = $literal.value, True, True}
    ;

body
@init {CParser.name_table.push_scope()}
@after {CParser.name_table.pop_scope()}
    : '{' 
      ( expr SEMICOLON 
      | variable_declaration 
      | const_declaration 
      | while_loop[CParser.loops]                                   
      )*
      '}'
    ;

condition
    returns [jmp]
    : l=expr ( '<'      {$jmp = 'jge'}   // jumps are inverted
             | '<='     {$jmp = 'jg'}
             | '>'      {$jmp = 'jle'}
             | '>='     {$jmp = 'jl'}
             | '=='     {$jmp = 'jne'}
             | '!='     {$jmp = 'je'}
             ) r=expr                                               {CParser.operations.append(Condition($l.value, $r.value, CParser.eax))}
    ;

variable_declaration
    : TYPE 
      var=variable_subdeclaration                                   {CParser.name_table[$var.name] = Int($var.name)}
                                                                    {if $var.expr_val != None:                                                          }
                                                                    {   op = Assign(CParser.name_table[$var.name].var, $var.expr_val, CParser.eax)  }
                                                                    {   CParser.operations.append(op)                                                   }
      (
        COMMA var=variable_subdeclaration                           {CParser.name_table[$var.name] = Int($var.name)}
                                                                    {if $var.expr_val != None:                                                        }
                                                                    {   op = Assign(CParser.name_table[$var.name].var, $var.expr_val, CParser.eax)  }
                                                                    {   CParser.operations.append(op)                                                   }
      )*
      SEMICOLON
    ;

variable_subdeclaration
    returns [name, expr_val]
    : ID                                                            {$name, $expr_val = $ID.text, None}
      (ASSIGN expr                                                  {$expr_val = $expr.value}
      )?
    ;

const_declaration
    : (TYPE 'const'| 'const' TYPE) ID ASSIGN literal SEMICOLON      {CParser.name_table[$ID.text] = Const($ID.text, $literal.value)}
    ;
    
function_declaration
    : TYPE ID '(' ')' body
    ;
/*
conditional_expr
    : 'if' expr
      (body | expr SEMICOLON)
      ('else' (body | expr SEMICOLON))?
    ;
*/
while_loop[loop_id]
@init   {
CParser.loops += 1

new_block_0 = BasicBlock(CParser.flow_graph[-1:])
CParser.flow_graph[-1].left = new_block_0
CParser.flow_graph.append(new_block_0)
new_block_0.add(START_WHILE(loop_id))

new_block_1 = BasicBlock([new_block_0])
new_block_0.left    = new_block_1
new_block_1.right   = new_block_0
CParser.operations  = new_block_0.operations
}
@after  {
new_block_2 = BasicBlock([new_block_1])
CParser.flow_graph[-1].left = new_block_2
CParser.flow_graph[-1].add(END_WHILE(loop_id))
CParser.flow_graph.append(new_block_2)
CParser.operations = CParser.flow_graph[-1].operations
}
    : 'while'                           
      '(' condition ')'                 {CParser.operations.append(MID_WHILE(loop_id, $condition.jmp))}
                                        {CParser.flow_graph.append(new_block_1)             }
                                        {CParser.operations = new_block_1.operations}
      body
    ;
 
return_expr
    : 'return' expr                     {CParser.operations.append(RET($expr.value, CParser.eax))}
    ;

literal 
    returns [value]
    : LITERAL {$value = Integer(int($LITERAL.text))}
    ;


SEMICOLON 
    : ';' 
    ;

TYPE
    : 'int'
    ;

COMMA 
    : ',' 
    ;

ASSIGN
    : '='
    ;

LITERAL
    : '-'? DIGIT+
    ;

ID
    : ALPHA (ALPHA | DIGIT)*
    ;

WS
   : [ \r\n\t] + -> skip
   ;

MUL : '*' ;
ADD : '+' ;
SUB : '-' ;
DIV : '/' ;
// MOD : '%' ;



fragment DIGIT
    : [0-9]
    ;

fragment ALPHA
    : [a-zA-Z]
    ;
grammar structure;

source_code
    : ( const_declaration      
      | variable_declaration
      )* function_declaration+
    ;

expr
    : '(' expr ')'
    | return_expr
    // | conditional_expr
    | '++' expr
    | '--' expr
    | expr '++'
    | expr '--'
    | '-' expr
    | '~' expr
    | '!' expr
    | expr (MUL | DIV) expr
    // | expr DIV expr
    // | expr MOD expr
    | expr (ADD | SUB) expr
    //| expr SUB expr
    | expr '<' expr
    | expr '<=' expr
    | expr '>' expr
    | expr '>=' expr
    | expr '==' expr
    | expr '!=' expr
    | expr '&&' expr
    | expr '||' expr
    | expr '?' expr ':' expr
    | ID '=' expr
    // | expr ',' expr
    | ID '(' (expr (',' expr)*) ')'
    | ID
    | LITERAL
    ;


body
    : '{' (expr SEMICOLON | while_loop | variable_declaration | const_declaration)* '}'
    ;

while_loop
    : 'while' '(' condition ')' body
    ;

condition
    : expr ('<' | '<=' | '>' | '>=' | '==' | '!=' ) expr
    ;

variable_declaration
    : TYPE 
      variable_subdeclaration
      (COMMA variable_subdeclaration)*
      SEMICOLON
    ;

variable_subdeclaration
    : ID (ASSIGN expr)?
    ;

const_declaration
    : TYPE 'const' ID ASSIGN expr SEMICOLON
    ;
    
function_declaration
    : TYPE ID '(' ')' body
    ;

conditional_expr
    : 'if' expr (body | expr SEMICOLON) ('else' (body | expr SEMICOLON))?
    ;

return_expr
    : 'return' expr
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
MOD : '%' ;

fragment DIGIT
    : [0-9]
    ;

fragment ALPHA
    : [a-zA-Z]
    ;
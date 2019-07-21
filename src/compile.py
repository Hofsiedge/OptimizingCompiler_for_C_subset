import sys
from antlr4 import FileStream, CommonTokenStream
from CLexer import CLexer
from CParser import CParser
from graph_colouring import colour_graph 

def main(argv):
    input_stream = FileStream(argv[1])
    lexer = CLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CParser(stream)
    tree = parser.source_code()
 
if __name__ == '__main__':
    main(sys.argv)

"""
QDL Compiler - Lexer (Tokenization)
====================================

Converts QDL source code into tokens.

Token types:
- KEYWORD: qubit, qureg, H, CNOT, measure, if, for, etc.
- IDENTIFIER: variable names (q0, q1, miners, etc.)
- NUMBER: integers, floats (42, 3.14, π)
- OPERATOR: +, -, *, /, =, ==, >, <, etc.
- SEPARATOR: (, ), [, ], ,, :
- STATE: |0⟩, |1⟩, |+⟩, |-⟩
- COMMENT: # comments
- NEWLINE, INDENT, DEDENT
"""

import re
from enum import Enum, auto
from typing import List, Tuple
from dataclasses import dataclass


class TokenType(Enum):
    """Token types for QDL language"""
    
    # Keywords
    QUBIT = auto()
    QUREG = auto()
    MEASURE = auto()
    PEEK = auto()
    IF = auto()
    ELSE = auto()
    FOR = auto()
    WHILE = auto()
    END = auto()
    FUNCTION = auto()
    RETURN = auto()
    PROGRAM = auto()
    PRINT = auto()
    
    # Quantum gates
    H = auto()          # Hadamard
    X = auto()          # Pauli-X
    Y = auto()          # Pauli-Y
    Z = auto()          # Pauli-Z
    S = auto()          # S gate
    T = auto()          # T gate
    CNOT = auto()       # Controlled-NOT
    CZ = auto()         # Controlled-Z
    SWAP = auto()       # SWAP
    TOFFOLI = auto()    # Controlled-controlled-NOT
    RX = auto()         # Rotation-X
    RY = auto()         # Rotation-Y
    RZ = auto()         # Rotation-Z
    
    # Algorithms
    GROVER = auto()
    QFT = auto()
    IQFT = auto()
    SHOR = auto()
    
    # ZION-specific
    ENTANGLE = auto()
    COHERENCE = auto()
    QUANTUM_PULSE = auto()
    CONSCIOUSNESS_LEVEL = auto()
    SACRED_FREQUENCY = auto()
    
    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    QUANTUM_STATE = auto()  # |0⟩, |1⟩, etc.
    STRING = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    GREATER = auto()
    LESS = auto()
    GREATER_EQUAL = auto()
    LESS_EQUAL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    ARROW = auto()      # ->
    AT = auto()         # @ (for miner assignment)
    
    # Separators
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    COLON = auto()
    DOT = auto()
    RANGE = auto()      # ..
    
    # Structure
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


@dataclass
class Token:
    """A single token"""
    type: TokenType
    value: any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, L{self.line}:C{self.column})"


class Lexer:
    """
    Tokenize QDL source code
    """
    
    # Keywords mapping
    KEYWORDS = {
        'qubit': TokenType.QUBIT,
        'qureg': TokenType.QUREG,
        'measure': TokenType.MEASURE,
        'peek': TokenType.PEEK,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'for': TokenType.FOR,
        'while': TokenType.WHILE,
        'end': TokenType.END,
        'function': TokenType.FUNCTION,
        'return': TokenType.RETURN,
        'program': TokenType.PROGRAM,
        'print': TokenType.PRINT,
        
        # Gates (case-insensitive)
        'h': TokenType.H,
        'x': TokenType.X,
        'y': TokenType.Y,
        'z': TokenType.Z,
        's': TokenType.S,
        't': TokenType.T,
        'cnot': TokenType.CNOT,
        'cz': TokenType.CZ,
        'swap': TokenType.SWAP,
        'toffoli': TokenType.TOFFOLI,
        'rx': TokenType.RX,
        'ry': TokenType.RY,
        'rz': TokenType.RZ,
        
        # Algorithms
        'grover': TokenType.GROVER,
        'qft': TokenType.QFT,
        'iqft': TokenType.IQFT,
        'shor': TokenType.SHOR,
        
        # ZION
        'entangle': TokenType.ENTANGLE,
        'coherence': TokenType.COHERENCE,
        'quantum_pulse': TokenType.QUANTUM_PULSE,
        'consciousness_level': TokenType.CONSCIOUSNESS_LEVEL,
        'sacred_frequency': TokenType.SACRED_FREQUENCY,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def current_char(self) -> str:
        """Get current character"""
        if self.pos >= len(self.source):
            return '\0'
        return self.source[self.pos]
    
    def peek_char(self, offset: int = 1) -> str:
        """Look ahead"""
        pos = self.pos + offset
        if pos >= len(self.source):
            return '\0'
        return self.source[pos]
    
    def advance(self):
        """Move to next character"""
        if self.current_char() == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1
    
    def skip_whitespace(self):
        """Skip spaces and tabs (but not newlines!)"""
        while self.current_char() in ' \t':
            self.advance()
    
    def skip_comment(self):
        """Skip # comments"""
        if self.current_char() == '#':
            while self.current_char() != '\n' and self.current_char() != '\0':
                self.advance()
    
    def read_number(self) -> Token:
        """Read integer or float"""
        start_line = self.line
        start_col = self.column
        num_str = ''
        
        # Handle π
        if self.current_char() == 'π':
            self.advance()
            return Token(TokenType.NUMBER, 3.141592653589793, start_line, start_col)
        
        while self.current_char().isdigit() or self.current_char() == '.':
            num_str += self.current_char()
            self.advance()
        
        # Convert to number
        if '.' in num_str:
            value = float(num_str)
        else:
            value = int(num_str)
        
        return Token(TokenType.NUMBER, value, start_line, start_col)
    
    def read_identifier(self) -> Token:
        """Read identifier or keyword"""
        start_line = self.line
        start_col = self.column
        ident = ''
        
        while self.current_char().isalnum() or self.current_char() == '_':
            ident += self.current_char()
            self.advance()
        
        # Check if keyword (case-insensitive)
        token_type = self.KEYWORDS.get(ident.lower(), TokenType.IDENTIFIER)
        
        return Token(token_type, ident, start_line, start_col)
    
    def read_quantum_state(self) -> Token:
        """Read quantum state notation |0⟩, |1⟩, |+⟩, etc."""
        start_line = self.line
        start_col = self.column
        
        state = ''
        self.advance()  # Skip |
        
        while self.current_char() not in '⟩\0':
            state += self.current_char()
            self.advance()
        
        if self.current_char() == '⟩':
            self.advance()
        
        return Token(TokenType.QUANTUM_STATE, f"|{state}⟩", start_line, start_col)
    
    def read_string(self) -> Token:
        """Read string literal"""
        start_line = self.line
        start_col = self.column
        quote_char = self.current_char()
        self.advance()  # Skip opening quote
        
        string = ''
        while self.current_char() != quote_char and self.current_char() != '\0':
            string += self.current_char()
            self.advance()
        
        if self.current_char() == quote_char:
            self.advance()  # Skip closing quote
        
        return Token(TokenType.STRING, string, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        """Tokenize entire source"""
        
        while self.current_char() != '\0':
            # Skip whitespace (except newlines)
            if self.current_char() in ' \t':
                self.skip_whitespace()
                continue
            
            # Comments
            if self.current_char() == '#':
                self.skip_comment()
                continue
            
            # Newlines
            if self.current_char() == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                self.advance()
                continue
            
            # Numbers
            if self.current_char().isdigit() or self.current_char() == 'π':
                self.tokens.append(self.read_number())
                continue
            
            # Quantum states
            if self.current_char() == '|':
                self.tokens.append(self.read_quantum_state())
                continue
            
            # Strings
            if self.current_char() in '"\'':
                self.tokens.append(self.read_string())
                continue
            
            # Identifiers/keywords
            if self.current_char().isalpha() or self.current_char() == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Operators and separators
            char = self.current_char()
            line, col = self.line, self.column
            
            if char == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', line, col))
                self.advance()
            elif char == '-' and self.peek_char() == '>':
                self.tokens.append(Token(TokenType.ARROW, '->', line, col))
                self.advance()
                self.advance()
            elif char == '-':
                self.tokens.append(Token(TokenType.MINUS, '-', line, col))
                self.advance()
            elif char == '*':
                self.tokens.append(Token(TokenType.MULTIPLY, '*', line, col))
                self.advance()
            elif char == '/':
                self.tokens.append(Token(TokenType.DIVIDE, '/', line, col))
                self.advance()
            elif char == '=' and self.peek_char() == '=':
                self.tokens.append(Token(TokenType.EQUAL, '==', line, col))
                self.advance()
                self.advance()
            elif char == '=':
                self.tokens.append(Token(TokenType.ASSIGN, '=', line, col))
                self.advance()
            elif char == '>':
                self.tokens.append(Token(TokenType.GREATER, '>', line, col))
                self.advance()
            elif char == '<':
                self.tokens.append(Token(TokenType.LESS, '<', line, col))
                self.advance()
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', line, col))
                self.advance()
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', line, col))
                self.advance()
            elif char == '[':
                self.tokens.append(Token(TokenType.LBRACKET, '[', line, col))
                self.advance()
            elif char == ']':
                self.tokens.append(Token(TokenType.RBRACKET, ']', line, col))
                self.advance()
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', line, col))
                self.advance()
            elif char == ':':
                self.tokens.append(Token(TokenType.COLON, ':', line, col))
                self.advance()
            elif char == '.':
                if self.peek_char() == '.':
                    self.tokens.append(Token(TokenType.RANGE, '..', line, col))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.DOT, '.', line, col))
                    self.advance()
            elif char == '@':
                self.tokens.append(Token(TokenType.AT, '@', line, col))
                self.advance()
            else:
                # Unknown character - skip
                print(f"Warning: Unknown character '{char}' at L{line}:C{col}")
                self.advance()
        
        # Add EOF
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        
        return self.tokens


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("🌌 QDL Compiler - Lexer Demo\n")
    
    # Test program
    source = """
# Simple Bell state program
program bell_state:
    qubit q0
    qubit q1
    
    H q0
    CNOT q0, q1
    
    measure q0 -> c0
    
    if c0 == 1:
        print "Qubit collapsed to |1⟩!"
    end
end
"""
    
    print("Source code:")
    print("=" * 60)
    print(source)
    print("=" * 60)
    
    # Tokenize
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    print("\nTokens:")
    print("=" * 60)
    for token in tokens:
        if token.type != TokenType.NEWLINE:  # Skip newlines for clarity
            print(token)
    
    print("\n✅ Lexer working!")
    print("   Next: Parser (build Abstract Syntax Tree)")

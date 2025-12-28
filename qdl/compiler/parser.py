"""
QDL Compiler - Parser (AST Generation)
=======================================

Converts tokens into Abstract Syntax Tree (AST).

AST Nodes:
- Program
- QuantumCircuit
- QubitDeclaration
- GateApplication
- Measurement
- IfStatement
- ForLoop
- FunctionDefinition
"""

from typing import List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from compiler.lexer import Token, TokenType, Lexer


# ============================================================================
# AST NODE DEFINITIONS
# ============================================================================

@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    pass


@dataclass
class Program(ASTNode):
    """Root node - entire program"""
    name: str
    statements: List[ASTNode]


@dataclass
class QubitDeclaration(ASTNode):
    """Declare qubit or quantum register"""
    name: str
    size: Optional[int] = None  # None = single qubit, int = register
    initial_state: Optional[str] = None  # "|0⟩", "|1⟩", "|+⟩", etc.


@dataclass
class GateApplication(ASTNode):
    """Apply quantum gate"""
    gate_name: str
    targets: List[str]  # Qubit names
    parameters: List[Any] = None  # For parameterized gates (RX, RY, RZ)


@dataclass
class Measurement(ASTNode):
    """Measure qubit(s)"""
    qubit: str
    classical_bit: str


@dataclass
class IfStatement(ASTNode):
    """Classical if statement"""
    condition: 'Expression'
    then_body: List[ASTNode]
    else_body: Optional[List[ASTNode]] = None


@dataclass
class ForLoop(ASTNode):
    """For loop"""
    variable: str
    start: int
    end: int
    body: List[ASTNode]


@dataclass
class FunctionDefinition(ASTNode):
    """Function definition"""
    name: str
    parameters: List[str]
    body: List[ASTNode]


@dataclass
class PrintStatement(ASTNode):
    """Print statement"""
    message: str


@dataclass
class Expression(ASTNode):
    """Expression (for conditions, etc.)"""
    operator: str  # "==", ">", "<", etc.
    left: Any
    right: Any


# ============================================================================
# PARSER
# ============================================================================

class Parser:
    """
    Parse tokens into AST
    
    Grammar (simplified):
    
    program      ::= "program" IDENTIFIER ":" statements "end"
    statements   ::= statement*
    statement    ::= qubit_decl | gate_app | measurement | if_stmt | for_loop | print_stmt
    
    qubit_decl   ::= "qubit" IDENTIFIER ("=" STATE)?
                   | "qureg" "[" NUMBER "]" IDENTIFIER
    
    gate_app     ::= GATE_NAME qubit_list
    
    measurement  ::= "measure" IDENTIFIER "->" IDENTIFIER
    
    if_stmt      ::= "if" expression ":" statements "end"
    
    for_loop     ::= "for" IDENTIFIER "in" NUMBER ".." NUMBER ":" statements "end"
    
    print_stmt   ::= "print" STRING
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current_token(self) -> Token:
        """Get current token"""
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.pos]
    
    def peek_token(self, offset: int = 1) -> Token:
        """Look ahead"""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]
    
    def advance(self):
        """Move to next token"""
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
    
    def expect(self, token_type: TokenType) -> Token:
        """Expect specific token type"""
        token = self.current_token()
        if token.type != token_type:
            raise SyntaxError(
                f"Expected {token_type.name}, got {token.type.name} "
                f"at L{token.line}:C{token.column}"
            )
        self.advance()
        return token
    
    def skip_newlines(self):
        """Skip newline tokens"""
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> Program:
        """Parse entire program"""
        self.skip_newlines()
        
        # Expect "program NAME:"
        self.expect(TokenType.PROGRAM)
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        # Parse statements
        statements = self.parse_statements()
        
        # Expect "end"
        self.expect(TokenType.END)
        
        return Program(name=name_token.value, statements=statements)
    
    def parse_statements(self) -> List[ASTNode]:
        """Parse list of statements"""
        statements = []
        
        while self.current_token().type != TokenType.END:
            self.skip_newlines()
            
            if self.current_token().type == TokenType.END:
                break
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            
            self.skip_newlines()
        
        return statements
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse single statement"""
        token = self.current_token()
        
        # Qubit declaration
        if token.type == TokenType.QUBIT:
            return self.parse_qubit_declaration()
        
        # Quantum register declaration
        if token.type == TokenType.QUREG:
            return self.parse_qureg_declaration()
        
        # Measurement
        if token.type == TokenType.MEASURE:
            return self.parse_measurement()
        
        # If statement
        if token.type == TokenType.IF:
            return self.parse_if_statement()
        
        # For loop
        if token.type == TokenType.FOR:
            return self.parse_for_loop()
        
        # Print statement
        if token.type == TokenType.PRINT:
            return self.parse_print_statement()
        
        # Quantum gates
        if token.type in [TokenType.H, TokenType.X, TokenType.Y, TokenType.Z,
                         TokenType.S, TokenType.T, TokenType.CNOT, TokenType.CZ,
                         TokenType.SWAP]:
            return self.parse_gate_application()
        
        # Unknown - skip
        self.advance()
        return None
    
    def parse_qubit_declaration(self) -> QubitDeclaration:
        """Parse: qubit q0 = |0⟩"""
        self.expect(TokenType.QUBIT)
        
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        initial_state = None
        
        # Optional initial state
        if self.current_token().type == TokenType.ASSIGN:
            self.advance()
            if self.current_token().type == TokenType.QUANTUM_STATE:
                initial_state = self.current_token().value
                self.advance()
        
        return QubitDeclaration(name=name, size=None, initial_state=initial_state)
    
    def parse_qureg_declaration(self) -> QubitDeclaration:
        """Parse: qureg[4] qr"""
        self.expect(TokenType.QUREG)
        self.expect(TokenType.LBRACKET)
        
        size_token = self.expect(TokenType.NUMBER)
        size = size_token.value
        
        self.expect(TokenType.RBRACKET)
        
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        return QubitDeclaration(name=name, size=size, initial_state=None)
    
    def parse_gate_application(self) -> GateApplication:
        """Parse: H q0 or CNOT q0, q1"""
        gate_token = self.current_token()
        gate_name = gate_token.type.name
        self.advance()
        
        # Parse target qubits
        targets = []
        
        # First target
        target_token = self.expect(TokenType.IDENTIFIER)
        targets.append(target_token.value)
        
        # Additional targets (for multi-qubit gates)
        while self.current_token().type == TokenType.COMMA:
            self.advance()  # Skip comma
            target_token = self.expect(TokenType.IDENTIFIER)
            targets.append(target_token.value)
        
        return GateApplication(gate_name=gate_name, targets=targets)
    
    def parse_measurement(self) -> Measurement:
        """Parse: measure q0 -> c0"""
        self.expect(TokenType.MEASURE)
        
        qubit_token = self.expect(TokenType.IDENTIFIER)
        qubit = qubit_token.value
        
        self.expect(TokenType.ARROW)
        
        classical_token = self.expect(TokenType.IDENTIFIER)
        classical_bit = classical_token.value
        
        return Measurement(qubit=qubit, classical_bit=classical_bit)
    
    def parse_if_statement(self) -> IfStatement:
        """Parse: if c0 == 1: ... end"""
        self.expect(TokenType.IF)
        
        # Parse condition (simplified - just equality for now)
        left_token = self.expect(TokenType.IDENTIFIER)
        operator_token = self.expect(TokenType.EQUAL)
        right_token = self.expect(TokenType.NUMBER)
        
        condition = Expression(
            operator=operator_token.value,
            left=left_token.value,
            right=right_token.value
        )
        
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        # Parse body
        then_body = self.parse_statements()
        
        return IfStatement(condition=condition, then_body=then_body)
    
    def parse_for_loop(self) -> ForLoop:
        """Parse: for i in 0..3: ... end"""
        self.expect(TokenType.FOR)
        
        var_token = self.expect(TokenType.IDENTIFIER)
        variable = var_token.value
        
        # Expect "in"
        in_token = self.current_token()
        if in_token.type != TokenType.IDENTIFIER or in_token.value.lower() != 'in':
            raise SyntaxError(f"Expected 'in', got {in_token.value}")
        self.advance()
        
        start_token = self.expect(TokenType.NUMBER)
        start = start_token.value
        
        self.expect(TokenType.RANGE)
        
        end_token = self.expect(TokenType.NUMBER)
        end = end_token.value
        
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        # Parse body
        body = self.parse_statements()
        
        return ForLoop(variable=variable, start=start, end=end, body=body)
    
    def parse_print_statement(self) -> PrintStatement:
        """Parse: print "message" """
        self.expect(TokenType.PRINT)
        
        message_token = self.expect(TokenType.STRING)
        message = message_token.value
        
        return PrintStatement(message=message)


# ============================================================================
# AST PRETTY PRINTER
# ============================================================================

def print_ast(node: ASTNode, indent: int = 0):
    """Pretty print AST"""
    prefix = "  " * indent
    
    if isinstance(node, Program):
        print(f"{prefix}Program: {node.name}")
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, QubitDeclaration):
        if node.size:
            print(f"{prefix}QubitRegister: {node.name}[{node.size}]")
        else:
            state = f" = {node.initial_state}" if node.initial_state else ""
            print(f"{prefix}Qubit: {node.name}{state}")
    
    elif isinstance(node, GateApplication):
        targets = ", ".join(node.targets)
        print(f"{prefix}Gate: {node.gate_name}({targets})")
    
    elif isinstance(node, Measurement):
        print(f"{prefix}Measure: {node.qubit} -> {node.classical_bit}")
    
    elif isinstance(node, IfStatement):
        print(f"{prefix}If: {node.condition.left} {node.condition.operator} {node.condition.right}")
        for stmt in node.then_body:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, ForLoop):
        print(f"{prefix}For: {node.variable} in {node.start}..{node.end}")
        for stmt in node.body:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, PrintStatement):
        print(f"{prefix}Print: \"{node.message}\"")
    
    else:
        print(f"{prefix}Unknown: {type(node).__name__}")


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("🌌 QDL Compiler - Parser Demo\n")
    
    # Test program
    source = """
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
    
    print("\nParsing...")
    print("=" * 60)
    
    # Parse
    parser = Parser(tokens)
    try:
        ast = parser.parse()
        
        print("\nAbstract Syntax Tree:")
        print("=" * 60)
        print_ast(ast)
        
        print("\n✅ Parser working!")
        print("   Next: Code generation (compile to quantum gates)")
        
    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}")

"""
ZQAL Interpreter - Parser & Execution Engine
=============================================

Parses .zqal files and executes quantum/tone algorithms in Python.

Mantra: JAY RAM SITA HANUMAN ✨
"""

import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    """ZQAL token types"""
    # Keywords
    ALGORITHM = "algorithm"
    QUANTUM = "quantum"
    KERNEL = "kernel"
    VALIDATOR = "validator"
    REWARD = "reward"
    CONST = "const"
    LET = "let"
    FOR = "for"
    IN = "in"
    IF = "if"
    ELSE = "else"
    RETURN = "return"
    IMPORT = "import"
    FROM = "from"
    AS = "as"
    TONE = "tone"
    BIND_TONE = "bind_tone"
    TO = "to"
    ASSERT = "assert"
    TRY = "try"
    CATCH = "catch"
    THROW = "throw"
    
    # Types
    U32 = "u32"
    U64 = "u64"
    F32 = "f32"
    F64 = "f64"
    BYTES = "bytes"
    BYTES80 = "bytes80"
    HASH32 = "hash32"
    BOOL = "bool"
    
    # Operators
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    CARET = "^"
    AMP = "&"
    PIPE = "|"
    EQ = "="
    EQEQ = "=="
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="
    
    # Delimiters
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACK = "["
    RBRACK = "]"
    SEMICOLON = ";"
    COLON = ":"
    COMMA = ","
    DOT = "."
    DOTDOT = ".."
    ARROW = "->"
    AT = "@"
    
    # Literals
    IDENT = "IDENT"
    NUMBER = "NUMBER"
    STRING = "STRING"
    
    # Special
    MUT = "mut"
    FN = "fn"
    EOF = "EOF"


@dataclass
class Token:
    """Token with type, value, and position"""
    type: TokenType
    value: str
    line: int
    col: int


@dataclass
class ASTNode:
    """Base AST node"""
    node_type: str
    children: List['ASTNode']
    value: Any = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ZQALLexer:
    """Tokenizer for ZQAL source code"""
    
    KEYWORDS = {
        'algorithm', 'quantum', 'kernel', 'validator', 'reward',
        'const', 'let', 'for', 'in', 'if', 'else', 'return',
        'import', 'from', 'as', 'tone', 'bind_tone', 'to',
        'assert', 'try', 'catch', 'throw', 'mut', 'fn',
        'u32', 'u64', 'f32', 'f64', 'bytes', 'bytes80', 'hash32', 'bool'
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []
    
    def tokenize(self) -> List[Token]:
        """Tokenize entire source"""
        while self.pos < len(self.source):
            self._skip_whitespace()
            if self.pos >= len(self.source):
                break
            
            # Skip comments
            if self._peek() == '/' and self._peek(1) == '/':
                self._skip_line_comment()
                continue
            if self._peek() == '/' and self._peek(1) == '*':
                self._skip_block_comment()
                continue
            
            token = self._next_token()
            if token:
                self.tokens.append(token)
        
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.col))
        return self.tokens
    
    def _peek(self, offset: int = 0) -> str:
        """Peek at character"""
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else ''
    
    def _advance(self) -> str:
        """Consume character"""
        if self.pos >= len(self.source):
            return ''
        char = self.source[self.pos]
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return char
    
    def _skip_whitespace(self):
        """Skip whitespace"""
        while self._peek().isspace():
            self._advance()
    
    def _skip_line_comment(self):
        """Skip // comment"""
        while self._peek() not in ('', '\n'):
            self._advance()
    
    def _skip_block_comment(self):
        """Skip /* */ comment"""
        self._advance()  # /
        self._advance()  # *
        while True:
            if self._peek() == '' or (self._peek() == '*' and self._peek(1) == '/'):
                break
            self._advance()
        if self._peek():
            self._advance()  # *
            self._advance()  # /
    
    def _next_token(self) -> Optional[Token]:
        """Get next token"""
        start_line = self.line
        start_col = self.col
        char = self._peek()
        
        # String literals
        if char == '"':
            return self._read_string(start_line, start_col)
        
        # Numbers
        if char.isdigit():
            return self._read_number(start_line, start_col)
        
        # Identifiers / keywords
        if char.isalpha() or char == '_':
            return self._read_ident(start_line, start_col)
        
        # Two-char operators
        two_char = char + self._peek(1)
        if two_char in ('==', '<=', '>=', '..',  '->', '//'):
            self._advance()
            self._advance()
            tt = {
                '==': TokenType.EQEQ,
                '<=': TokenType.LTE,
                '>=': TokenType.GTE,
                '..': TokenType.DOTDOT,
                '->': TokenType.ARROW,
            }.get(two_char)
            return Token(tt, two_char, start_line, start_col) if tt else None
        
        # Single-char tokens
        self._advance()
        single_char_map = {
            '+': TokenType.PLUS, '-': TokenType.MINUS,
            '*': TokenType.STAR, '/': TokenType.SLASH,
            '^': TokenType.CARET, '&': TokenType.AMP,
            '|': TokenType.PIPE, '=': TokenType.EQ,
            '<': TokenType.LT, '>': TokenType.GT,
            '(': TokenType.LPAREN, ')': TokenType.RPAREN,
            '{': TokenType.LBRACE, '}': TokenType.RBRACE,
            '[': TokenType.LBRACK, ']': TokenType.RBRACK,
            ';': TokenType.SEMICOLON, ':': TokenType.COLON,
            ',': TokenType.COMMA, '.': TokenType.DOT,
            '@': TokenType.AT,
        }
        tt = single_char_map.get(char)
        return Token(tt, char, start_line, start_col) if tt else None
    
    def _read_string(self, line: int, col: int) -> Token:
        """Read string literal"""
        self._advance()  # opening "
        value = ""
        while self._peek() and self._peek() != '"':
            value += self._advance()
        if self._peek() == '"':
            self._advance()  # closing "
        return Token(TokenType.STRING, value, line, col)
    
    def _read_number(self, line: int, col: int) -> Token:
        """Read number (int or float)"""
        value = ""
        while self._peek().isdigit() or self._peek() in ('_', '.'):
            value += self._advance()
        return Token(TokenType.NUMBER, value.replace('_', ''), line, col)
    
    def _read_ident(self, line: int, col: int) -> Token:
        """Read identifier or keyword"""
        value = ""
        while self._peek().isalnum() or self._peek() == '_':
            value += self._advance()
        
        # Check if keyword
        if value in self.KEYWORDS:
            tt = TokenType.__members__.get(value.upper())
            if not tt:
                # Special keywords
                if value == 'fn':
                    tt = TokenType.FN
                elif value == 'mut':
                    tt = TokenType.MUT
                elif value == 'bind_tone':
                    tt = TokenType.BIND_TONE
                else:
                    tt = TokenType.IDENT
            return Token(tt, value, line, col)
        
        return Token(TokenType.IDENT, value, line, col)


class ZQALParser:
    """Parser for ZQAL - builds AST"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def parse(self) -> ASTNode:
        """Parse program"""
        imports = []
        declarations = []
        
        while not self._at_end():
            if self._check(TokenType.IMPORT) or self._check(TokenType.FROM):
                imports.append(self._parse_import())
            elif self._check(TokenType.AT):
                declarations.append(self._parse_declaration())
            elif self._check(TokenType.CONST):
                declarations.append(self._parse_const())
            elif self._check(TokenType.QUANTUM):
                declarations.append(self._parse_quantum_decl())
            else:
                self._advance()  # Skip unknown
        
        return ASTNode(
            node_type="program",
            children=imports + declarations,
            metadata={"imports": len(imports), "declarations": len(declarations)}
        )
    
    def _parse_import(self) -> ASTNode:
        """Parse import statement"""
        if self._match(TokenType.IMPORT):
            path = self._consume(TokenType.STRING).value
            alias = None
            if self._match(TokenType.AS):
                alias = self._consume(TokenType.IDENT).value
            self._consume(TokenType.SEMICOLON)
            return ASTNode("import", [], metadata={"path": path, "alias": alias})
        
        elif self._match(TokenType.FROM):
            path = self._consume(TokenType.STRING).value
            self._consume(TokenType.IMPORT)
            symbols = [self._consume(TokenType.IDENT).value]
            while self._match(TokenType.COMMA):
                symbols.append(self._consume(TokenType.IDENT).value)
            self._consume(TokenType.SEMICOLON)
            return ASTNode("from_import", [], metadata={"path": path, "symbols": symbols})
        
        return ASTNode("unknown_import", [])
    
    def _parse_declaration(self) -> ASTNode:
        """Parse @ declarations"""
        self._consume(TokenType.AT)
        
        if self._check(TokenType.ALGORITHM):
            return self._parse_algorithm()
        elif self._check(TokenType.TONE):
            return self._parse_tone()
        elif self._check(TokenType.KERNEL) or self._check(TokenType.VALIDATOR) or self._check(TokenType.REWARD):
            return self._parse_function()
        elif self._check(TokenType.BIND_TONE):
            return self._parse_bind_tone()
        
        return ASTNode("unknown_decl", [])
    
    def _parse_algorithm(self) -> ASTNode:
        """Parse @algorithm { ... }"""
        self._consume(TokenType.ALGORITHM)
        name = self._consume(TokenType.IDENT).value
        self._consume(TokenType.LBRACE)
        
        meta = {}
        while not self._check(TokenType.RBRACE) and not self._at_end():
            key = self._consume(TokenType.IDENT).value
            self._consume(TokenType.COLON)
            value = self._parse_value()
            meta[key] = value
        
        self._consume(TokenType.RBRACE)
        return ASTNode("algorithm", [], value=name, metadata=meta)
    
    def _parse_tone(self) -> ASTNode:
        """Parse @tone N { ... }"""
        self._consume(TokenType.TONE)
        tone_id = int(self._consume(TokenType.NUMBER).value)
        self._consume(TokenType.LBRACE)
        
        meta = {}
        while not self._check(TokenType.RBRACE) and not self._at_end():
            key = self._consume(TokenType.IDENT).value
            self._consume(TokenType.COLON)
            value = self._parse_value()
            meta[key] = value
        
        self._consume(TokenType.RBRACE)
        return ASTNode("tone", [], value=tone_id, metadata=meta)
    
    def _parse_bind_tone(self) -> ASTNode:
        """Parse @bind_tone N to name"""
        self._consume(TokenType.BIND_TONE)
        tone_id = int(self._consume(TokenType.NUMBER).value)
        self._consume(TokenType.TO)
        name = self._consume(TokenType.IDENT).value
        return ASTNode("bind_tone", [], metadata={"tone_id": tone_id, "name": name})
    
    def _parse_const(self) -> ASTNode:
        """Parse const X: type = value;"""
        self._consume(TokenType.CONST)
        name = self._consume(TokenType.IDENT).value
        self._consume(TokenType.COLON)
        type_name = self._parse_type()
        self._consume(TokenType.EQ)
        value = self._parse_value()
        self._consume(TokenType.SEMICOLON)
        return ASTNode("const", [], value=value, metadata={"name": name, "type": type_name})
    
    def _parse_quantum_decl(self) -> ASTNode:
        """Parse quantum state[N]: type;"""
        self._consume(TokenType.QUANTUM)
        name = self._consume(TokenType.IDENT).value
        self._consume(TokenType.LBRACK)
        size = int(self._consume(TokenType.NUMBER).value)
        self._consume(TokenType.RBRACK)
        self._consume(TokenType.COLON)
        elem_type = self._parse_type()
        self._consume(TokenType.SEMICOLON)
        return ASTNode("quantum_decl", [], metadata={
            "name": name, "size": size, "elem_type": elem_type
        })
    
    def _parse_function(self) -> ASTNode:
        """Parse function (@kernel/@validator/@reward)"""
        fn_type = self._advance().value  # kernel/validator/reward
        self._consume(TokenType.FN)
        name = self._consume(TokenType.IDENT).value
        
        # Parameters
        self._consume(TokenType.LPAREN)
        params = []
        while not self._check(TokenType.RPAREN) and not self._at_end():
            param_name = self._consume(TokenType.IDENT).value
            self._consume(TokenType.COLON)
            param_type = self._parse_type()
            params.append({"name": param_name, "type": param_type})
            if not self._check(TokenType.RPAREN):
                self._match(TokenType.COMMA)  # Optional comma
        self._consume(TokenType.RPAREN)
        
        # Return type (optional)
        return_type = "void"
        if self._check(TokenType.ARROW):
            self._consume(TokenType.ARROW)
            return_type = self._parse_type()
        
        # Body (simplified - just skip for now)
        body = self._parse_block()
        
        return ASTNode("function", [body], metadata={
            "fn_type": fn_type,
            "name": name,
            "params": params,
            "return_type": return_type
        })
    
    def _parse_block(self) -> ASTNode:
        """Parse { ... } block"""
        self._consume(TokenType.LBRACE)
        statements = []
        
        while not self._check(TokenType.RBRACE) and not self._at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        self._consume(TokenType.RBRACE)
        return ASTNode("block", statements)
    
    def _parse_statement(self) -> Optional[ASTNode]:
        """Parse statement"""
        if self._check(TokenType.LET):
            return self._parse_let()
        elif self._check(TokenType.FOR):
            return self._parse_for()
        elif self._check(TokenType.IF):
            return self._parse_if()
        elif self._check(TokenType.RETURN):
            return self._parse_return()
        else:
            # Expression statement or unknown - skip to semicolon
            while not self._check(TokenType.SEMICOLON) and not self._at_end():
                self._advance()
            if self._check(TokenType.SEMICOLON):
                self._advance()
            return None
    
    def _parse_let(self) -> ASTNode:
        """Parse let x = expr;"""
        self._consume(TokenType.LET)
        is_mut = self._match(TokenType.MUT)
        name = self._consume(TokenType.IDENT).value
        self._consume(TokenType.EQ)
        # Skip expression for now
        while not self._check(TokenType.SEMICOLON) and not self._at_end():
            self._advance()
        self._consume(TokenType.SEMICOLON)
        return ASTNode("let", [], metadata={"name": name, "mut": is_mut})
    
    def _parse_for(self) -> ASTNode:
        """Parse for i in 0..N { }"""
        self._consume(TokenType.FOR)
        var = self._consume(TokenType.IDENT).value
        self._consume(TokenType.IN)
        # Skip range
        while not self._check(TokenType.LBRACE) and not self._at_end():
            self._advance()
        body = self._parse_block()
        return ASTNode("for", [body], metadata={"var": var})
    
    def _parse_if(self) -> ASTNode:
        """Parse if expr { } [else { }]"""
        self._consume(TokenType.IF)
        # Skip condition
        while not self._check(TokenType.LBRACE) and not self._at_end():
            self._advance()
        then_block = self._parse_block()
        else_block = None
        if self._match(TokenType.ELSE):
            else_block = self._parse_block()
        return ASTNode("if", [then_block] + ([else_block] if else_block else []))
    
    def _parse_return(self) -> ASTNode:
        """Parse return expr;"""
        self._consume(TokenType.RETURN)
        # Skip expression
        while not self._check(TokenType.SEMICOLON) and not self._at_end():
            self._advance()
        self._consume(TokenType.SEMICOLON)
        return ASTNode("return", [])
    
    def _parse_type(self) -> str:
        """Parse type name"""
        if self._check(TokenType.AMP):
            self._advance()
            mut = "mut " if self._match(TokenType.MUT) else ""
            base = self._parse_type()
            return f"&{mut}{base}"
        elif self._check(TokenType.LBRACK):
            self._advance()
            elem = self._parse_type()
            self._consume(TokenType.SEMICOLON)
            size = self._consume(TokenType.NUMBER).value
            self._consume(TokenType.RBRACK)
            return f"[{elem}; {size}]"
        else:
            return self._advance().value
    
    def _parse_value(self) -> Any:
        """Parse literal value"""
        if self._check(TokenType.STRING):
            return self._advance().value
        elif self._check(TokenType.NUMBER):
            val = self._advance().value
            return float(val) if '.' in val else int(val)
        elif self._check(TokenType.LBRACK):
            self._advance()
            values = []
            while not self._check(TokenType.RBRACK) and not self._at_end():
                values.append(self._parse_value())
                if not self._check(TokenType.RBRACK):
                    self._consume(TokenType.COMMA)
            self._consume(TokenType.RBRACK)
            return values
        elif self._check(TokenType.IDENT):
            # Boolean or identifier
            val = self._advance().value
            if val == "true":
                return True
            elif val == "false":
                return False
            return val
        return None
    
    def _check(self, token_type: TokenType) -> bool:
        """Check if current token matches type"""
        return not self._at_end() and self.tokens[self.pos].type == token_type
    
    def _match(self, token_type: TokenType) -> bool:
        """Match and consume if matches"""
        if self._check(token_type):
            self._advance()
            return True
        return False
    
    def _consume(self, token_type: TokenType) -> Token:
        """Consume token of expected type"""
        if not self._check(token_type):
            current = self.tokens[self.pos] if not self._at_end() else None
            raise SyntaxError(
                f"Expected {token_type}, got {current.type if current else 'EOF'}"
            )
        return self._advance()
    
    def _advance(self) -> Token:
        """Move to next token"""
        if not self._at_end():
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return self.tokens[-1]  # EOF
    
    def _at_end(self) -> bool:
        """Check if at end"""
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == TokenType.EOF


class ZQALInterpreter:
    """Main ZQAL interpreter - parse and execute .zqal programs"""
    
    def __init__(self):
        self.algorithms = {}
        self.constants = {}
        self.quantum_states = {}
        self.functions = {}
        self.tones = {}
        self.tone_bindings = {}
    
    def load_file(self, filepath: str) -> ASTNode:
        """Load and parse .zqal file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        return self.parse(source)
    
    def parse(self, source: str) -> ASTNode:
        """Parse ZQAL source code"""
        # Tokenize
        lexer = ZQALLexer(source)
        tokens = lexer.tokenize()
        
        # Parse
        parser = ZQALParser(tokens)
        ast = parser.parse()
        
        # Extract metadata
        self._extract_metadata(ast)
        
        return ast
    
    def _extract_metadata(self, ast: ASTNode):
        """Extract algorithms, constants, etc. from AST"""
        for node in ast.children:
            if node.node_type == "algorithm":
                self.algorithms[node.value] = node.metadata
            elif node.node_type == "const":
                self.constants[node.metadata["name"]] = node.value
            elif node.node_type == "quantum_decl":
                self.quantum_states[node.metadata["name"]] = node.metadata
            elif node.node_type == "function":
                self.functions[node.metadata["name"]] = node
            elif node.node_type == "tone":
                self.tones[node.value] = node.metadata
            elif node.node_type == "bind_tone":
                self.tone_bindings[node.metadata["name"]] = node.metadata["tone_id"]
    
    def execute(self, function_name: str, *args, **kwargs) -> Any:
        """Execute a ZQAL function"""
        if function_name not in self.functions:
            raise NameError(f"Function '{function_name}' not found")
        
        fn_node = self.functions[function_name]
        
        # TODO: Implement actual execution
        # For now, just return metadata
        return {
            "function": function_name,
            "type": fn_node.metadata["fn_type"],
            "params": fn_node.metadata["params"],
            "return_type": fn_node.metadata["return_type"],
            "status": "parsed_not_executed"
        }
    
    def get_algorithm_info(self, name: str) -> Dict[str, Any]:
        """Get algorithm metadata"""
        return self.algorithms.get(name, {})
    
    def get_constant(self, name: str) -> Any:
        """Get constant value"""
        return self.constants.get(name)
    
    def get_tone(self, tone_id: int) -> Dict[str, Any]:
        """Get tone definition"""
        return self.tones.get(tone_id, {})
    
    def __repr__(self) -> str:
        return (
            f"<ZQALInterpreter: "
            f"{len(self.algorithms)} algorithms, "
            f"{len(self.functions)} functions, "
            f"{len(self.tones)} tones>"
        )


if __name__ == "__main__":
    # Test with cosmic_harmony.zqal
    print("ZQAL Interpreter Test")
    print("=" * 60)
    
    interp = ZQALInterpreter()
    
    # Test source
    test_source = """
@algorithm CosmicHarmony {
  version: "1.0.0"
  target: ["GPU", "CPU"]
  consciousness: true
}

const GOLDEN_RATIO: f64 = 1.618033988749;

quantum state[12]: u32;

@kernel
fn mine(header: bytes80, nonce: u64) -> hash32 {
  let mut s = [0u32; 12];
  return collapse(s[0]);
}

@validator
fn validate(hash: hash32, target: hash32) -> bool {
  return hash <= target;
}
"""
    
    try:
        ast = interp.parse(test_source)
        print(f"✅ Parsed successfully!")
        print(f"   Algorithms: {list(interp.algorithms.keys())}")
        print(f"   Constants: {list(interp.constants.keys())}")
        print(f"   Functions: {list(interp.functions.keys())}")
        print(f"   Quantum states: {list(interp.quantum_states.keys())}")
        print()
        
        # Test algorithm info
        algo_info = interp.get_algorithm_info("CosmicHarmony")
        print(f"Algorithm 'CosmicHarmony':")
        for k, v in algo_info.items():
            print(f"   {k}: {v}")
        print()
        
        # Test constant
        print(f"GOLDEN_RATIO = {interp.get_constant('GOLDEN_RATIO')}")
        print()
        
        # Test function execution (placeholder)
        result = interp.execute("mine")
        print(f"Execute 'mine': {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

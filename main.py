import re

class Node:
    def __init__(self, op=None, left=None, right=None, value=None):
        self.op = op
        self.left = left
        self.right = right
        self.value = value
        self.label = None

    def __str__(self):
        if self.value is not None:
            return str(self.value)
        return f"({str(self.left)} {self.op} {str(self.right)})"

    def to_code(self):
        if self.value is not None:
            return str(self.value)
        return f"({self.left.to_code()}{self.op}{self.right.to_code()})"

def parse_expression(expr):
    tokens = re.findall(r'[a-zA-Z_]\w*|\d+|[()+\-*/]', expr)
    def precedence(op): return {'+':1, '-':1, '*':2, '/':2}.get(op, 0)
    def to_ast(tokens):
        output, ops = [], []
        def reduce():
            op = ops.pop()
            r = output.pop()
            l = output.pop()
            output.append(Node(op=op, left=l, right=r))
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok.isdigit():
                output.append(Node(value=int(tok)))
            elif re.match(r'[a-zA-Z_]\w*', tok):
                output.append(Node(value=tok))
            elif tok == '(':
                ops.append(tok)
            elif tok == ')':
                while ops and ops[-1] != '(':
                    reduce()
                ops.pop()
            else:
                while ops and precedence(ops[-1]) >= precedence(tok):
                    reduce()
                ops.append(tok)
            i += 1
        while ops:
            reduce()
        return output[0]
    return to_ast(tokens)

def constant_fold(node):
    if node is None or isinstance(node.value, str):
        return node
    if node.value is not None:
        return node
    node.left = constant_fold(node.left)
    node.right = constant_fold(node.right)
    if isinstance(node.left.value, int) and isinstance(node.right.value, int):
        lval, rval = node.left.value, node.right.value
        if node.op == '+': return Node(value=lval + rval)
        if node.op == '-': return Node(value=lval - rval)
        if node.op == '*': return Node(value=lval * rval)
        if node.op == '/': return Node(value=lval // rval)
    return node

def label_tree(node):
    if node is None:
        return 0
    if node.value is not None:
        node.label = 1
        return 1
    l1 = label_tree(node.left)
    l2 = label_tree(node.right)
    node.label = max(l1, l2) if l1 != l2 else l1 + 1
    return node.label

def is_invariant(node, loop_vars):
    if node is None:
        return True
    if node.value is not None:
        return not isinstance(node.value, str) or node.value not in loop_vars
    return is_invariant(node.left, loop_vars) and is_invariant(node.right, loop_vars)

def hoist_expressions(code_lines):
    optimized_lines = []
    i = 0
    temp_counter = 0
    
    while i < len(code_lines):
        line = code_lines[i].strip()
        
        # Detectar inicio de for loop
        if line.startswith("for") and '{' in line:
            hoist = []
            loop_block = []
            loop_vars = ['i']  # Variables que cambian en el loop
            
            i += 1
            # Procesar contenido del loop
            while i < len(code_lines) and '}' not in code_lines[i]:
                original_line = code_lines[i]
                stmt_stripped = original_line.strip()
                
                # Regex corregido para capturar += correctamente
                match = re.match(r'([a-zA-Z_]\w*)\[(.+?)\]\s*\+\=\s*(.+);', stmt_stripped)
                if match:
                    array_var = match.group(1)
                    index_expr = match.group(2)
                    value_expr = match.group(3)
                    
                    # Parsear la expresión del índice
                    try:
                        ast = parse_expression(index_expr)
                        if is_invariant(ast, loop_vars):
                            # Crear variable temporal
                            temp_var = f"t{temp_counter}"
                            temp_counter += 1
                            hoist.append(f"{temp_var} = {ast.to_code()};")
                            
                            # Obtener indentación original
                            indent = re.match(r'^\s*', original_line).group(0)
                            stmt = f"{indent}{array_var}[{temp_var}] += {value_expr.strip()};"
                            loop_block.append(stmt)
                        else:
                            loop_block.append(original_line.rstrip())
                    except:
                        # Si hay error parseando, mantener original
                        loop_block.append(original_line.rstrip())
                else:
                    loop_block.append(original_line.rstrip())
                i += 1
            
            # Agregar código hoisted antes del loop
            optimized_lines.extend(hoist)
            optimized_lines.append(line)
            optimized_lines.extend(loop_block)
            
            # Agregar la llave de cierre del loop
            if i < len(code_lines):
                optimized_lines.append(code_lines[i].rstrip())
        else:
            optimized_lines.append(code_lines[i].rstrip())
        i += 1
    
    return optimized_lines

def optimize_file(input_path, output_path):
    with open(input_path, 'r') as f:
        raw_lines = f.readlines()

    new_lines = []
    for line in raw_lines:
        stripped = line.strip()
        # Procesar asignaciones simples (constant folding)
        if '=' in stripped and ';' in stripped and not stripped.startswith('for') and '+=' not in stripped:
            try:
                var, expr = stripped.split('=', 1)
                expr = expr.replace(';', '').strip()
                ast = parse_expression(expr)
                ast = constant_fold(ast)
                label_tree(ast)
                indent = re.match(r'^\s*', line).group(0)
                if isinstance(ast.value, int):
                    new_lines.append(f"{indent}{var.strip()} = {ast.value};")
                else:
                    new_lines.append(f"{indent}{var.strip()} = {ast.to_code()};")
            except:
                new_lines.append(line.rstrip('\n'))
        else:
            new_lines.append(line.rstrip('\n'))

    # Aplicar code hoisting
    optimized_lines = hoist_expressions(new_lines)

    with open(output_path, 'w') as f:
        for l in optimized_lines:
            f.write(l + '\n')

    print(f"✅ Optimización completa → {output_path}")

if __name__ == "__main__":
    optimize_file("input.txt", "output.txt")
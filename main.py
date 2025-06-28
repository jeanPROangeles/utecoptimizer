#!/usr/bin/env python3
import re
import sys
import os

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

# === PLEGADO DE CONSTANTES
def constant_fold(node):
    if node is None or node.value is not None:
        return node
    node.left = constant_fold(node.left)
    node.right = constant_fold(node.right)
    if node.left.value is not None and node.right.value is not None:
        lval, rval = node.left.value, node.right.value
        if node.op == '+': return Node(value=lval + rval)
        if node.op == '-': return Node(value=lval - rval)
        if node.op == '*': return Node(value=lval * rval)
        if node.op == '/': return Node(value=lval // rval)
    return node

# === ETIQUETADO DE ÁRBOL
def label_tree(node):
    if node is None:
        return 0
    if node.value is not None:
        node.label = 1
        return 1
    l1 = label_tree(node.left)
    l2 = label_tree(node.right)
    node.label = l1 + 1 if l1 == l2 else max(l1, l2)
    return node.label

# === PARSEO DE EXPRESIÓN ARITMÉTICA MEJORADO
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
            else:  # operator
                while ops and precedence(ops[-1]) >= precedence(tok):
                    reduce()
                ops.append(tok)
            i += 1
        while ops:
            reduce()
        return output[0]
    return to_ast(tokens)

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
            loop_vars = ['i', 'j', 'k', 'm', 'n']  # Variables comunes de loop
            
            i += 1
            # Procesar contenido del loop
            while i < len(code_lines) and '}' not in code_lines[i]:
                original_line = code_lines[i]
                stmt_stripped = original_line.strip()
                
                # Regex para capturar += correctamente
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

# === PROCESAMIENTO GENERAL DEL ARCHIVO
def optimize_file(input_path, output_path):
    try:
        with open(input_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{input_path}'")
        return False
    except Exception as e:
        print(f"❌ Error leyendo el archivo: {e}")
        return False

    optimized_lines = []
    for line in lines:
        original_line = line.rstrip('\n')
        stripped = line.strip()
        
        # Procesar asignaciones simples (constant folding)
        if '=' in stripped and ';' in stripped and not stripped.startswith('for') and '+=' not in stripped:
            try:
                var, expr = stripped.split('=', 1)
                expr = expr.replace(';', '').strip()
                tree = parse_expression(expr)
                tree = constant_fold(tree)
                label_tree(tree)
                
                # Mantener indentación original
                indent = re.match(r'^\s*', line).group(0)
                if tree.value is not None:
                    optimized_lines.append(f"{indent}{var.strip()} = {tree.value};")
                else:
                    optimized_lines.append(f"{indent}{var.strip()} = {tree.to_code()};")
            except:
                optimized_lines.append(original_line)
        else:
            optimized_lines.append(original_line)

    # Aplicar code hoisting
    optimized_lines = hoist_expressions(optimized_lines)

    try:
        with open(output_path, 'w') as f:
            for line in optimized_lines:
                f.write(line + '\n')
        return True
    except Exception as e:
        print(f"❌ Error escribiendo el archivo: {e}")
        return False

def show_usage():
    print("Uso:")
    print("  python3 nombre_de_archivo.py <archivo_entrada> [archivo_salida]")
    print("  python3 nombre_de_archivo.py input.txt")
    print("  python3 nombre_de_archivo.py input.txt output.txt")
    print()
    print("Si no se especifica archivo de salida, se usará 'output.txt'")

# === MAIN ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Error: Falta especificar el archivo de entrada")
        show_usage()
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    # Determinar archivo de salida
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        # Si no se especifica, usar output.txt por defecto
        output_path = "output.txt"
    
    print(f"🔧 UtecCompiler Optimizer")
    print(f"📁 Entrada: {input_path}")
    print(f"📁 Salida: {output_path}")
    print(f"⚡ Procesando...")
    
    success = optimize_file(input_path, output_path)
    
    if success:
        print(f"✅ Optimización completada → {output_path}")
    else:
        print(f"❌ Error en la optimización")
        sys.exit(1)
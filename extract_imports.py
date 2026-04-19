import ast, os
imports = set()
for root, dirs, files in os.walk('backend'):
    if '.venv' in dirs: dirs.remove('.venv')
    if '__pycache__' in dirs: dirs.remove('__pycache__')
    for file in files:
        if file.endswith('.py') and not file.startswith('.'):
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                try: tree = ast.parse(f.read())
                except Exception as e:
                    pass
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names: imports.add(n.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.add(node.module.split('.')[0])
print(sorted(list(imports)))

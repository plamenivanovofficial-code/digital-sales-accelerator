import re

def check_file_indentation(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    issues = []
    in_multiline_string = False
    string_delimiter = None
    
    for i, line in enumerate(lines, 1):
        # Skip empty lines
        if not line.strip():
            continue
            
        # Check for multiline strings
        if '"""' in line or "'''" in line:
            if not in_multiline_string:
                in_multiline_string = True
                string_delimiter = '"""' if '"""' in line else "'''"
            elif string_delimiter in line:
                in_multiline_string = False
            continue
        
        if in_multiline_string:
            continue
        
        # Skip comments
        if line.strip().startswith('#'):
            continue
        
        # Check indentation
        stripped = line.lstrip()
        if stripped:
            indent = len(line) - len(stripped)
            if indent % 4 != 0:
                issues.append(f"Line {i}: Inconsistent indentation ({indent} spaces)")
                
            # Check for tabs
            if '\t' in line[:indent]:
                issues.append(f"Line {i}: Contains tabs instead of spaces")
    
    return issues

# Check all Python files
for filename in ['app.py', 'config.py', 'database.py', 'security.py', 'scanner.py', 'ai_engine.py', 'ui_components.py']:
    print(f"\n{'='*60}")
    print(f"Checking: {filename}")
    print('='*60)
    issues = check_file_indentation(filename)
    if issues:
        for issue in issues[:10]:  # Show first 10 issues
            print(issue)
        if len(issues) > 10:
            print(f"... and {len(issues)-10} more issues")
    else:
        print("✓ No indentation issues found")

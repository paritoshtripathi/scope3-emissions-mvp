"""
Path and import verification script
"""
import os
import ast
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple

class ImportVerifier:
    def __init__(self):
        self.project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.src_dir = self.project_root / 'src'
        self.allowed_prefixes = {'src.', 'tests.'}
        self.errors = []
        
    def verify_all(self) -> bool:
        """Verify all Python files in the project"""
        print("🔍 Verifying project structure and imports...")
        
        # Check directory structure
        self._verify_directory_structure()
        
        # Check Python files
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    filepath = Path(root) / file
                    self._verify_file(filepath)
                    
        # Print results
        if self.errors:
            print("\n❌ Found issues:")
            for error in self.errors:
                print(f"  - {error}")
            return False
        else:
            print("\n✅ All paths and imports are correct!")
            return True
            
    def _verify_directory_structure(self):
        """Verify required directories exist"""
        required_dirs = [
            'src/rag/agents',
            'src/rag/api',
            'src/rag/embeddings',
            'src/rag/indexing',
            'src/rag/models',
            'src/rag/processors',
            'src/rag/retrieval',
            'src/rag/scripts',
            'src/config',
            'src/monitoring',
            'tests/unit',
            'tests/integration'
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                self.errors.append(f"Missing directory: {dir_path}")
                
        # Check for old directories that should be removed
        old_dirs = [
            'rag',
            'agents',
            'examples',
            'postman',
            'output'
        ]
        
        for dir_path in old_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                self.errors.append(f"Old directory should be removed: {dir_path}")
                
    def _verify_file(self, filepath: Path):
        """Verify imports in a Python file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse Python file
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                self.errors.append(f"Syntax error in {filepath}: {str(e)}")
                return
                
            # Get all imports
            imports = self._get_imports(tree)
            
            # Verify each import
            rel_path = filepath.relative_to(self.project_root)
            for imp in imports:
                if not self._is_valid_import(imp, rel_path):
                    self.errors.append(
                        f"Invalid import in {rel_path}: {imp}"
                    )
                    
        except Exception as e:
            self.errors.append(f"Error processing {filepath}: {str(e)}")
            
    def _get_imports(self, tree: ast.AST) -> Set[str]:
        """Extract all imports from AST"""
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                for name in node.names:
                    if module:
                        imports.add(f"{module}.{name.name}")
                    else:
                        imports.add(name.name)
                        
        return imports
        
    def _is_valid_import(self, import_path: str, file_path: Path) -> bool:
        """Check if import path is valid"""
        # Standard library imports are always valid
        if not any(import_path.startswith(prefix) for prefix in self.allowed_prefixes):
            return True
            
        # Check relative imports
        if import_path.startswith('.'):
            return True  # Allow relative imports for now
            
        # Check project imports
        if import_path.startswith('src.'):
            module_path = self.src_dir / '/'.join(import_path.split('.')[1:])
            return (module_path.exists() or 
                   (module_path.parent / f"{module_path.name}.py").exists())
                   
        if import_path.startswith('tests.'):
            module_path = self.project_root / 'tests' / '/'.join(import_path.split('.')[1:])
            return (module_path.exists() or 
                   (module_path.parent / f"{module_path.name}.py").exists())
                   
        return False

def main():
    verifier = ImportVerifier()
    success = verifier.verify_all()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
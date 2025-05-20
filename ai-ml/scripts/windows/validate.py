"""
Comprehensive validation script for RAG system
"""
import importlib
import sys
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
import json

class RAGValidator:
    def __init__(self):
        self.project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.required_packages = [
            'flask',
            'flask_restx',
            'flask_cors',
            'numpy',
            'pandas',
            'torch',
            'transformers',
            'sentence_transformers',
            'faiss-cpu',
            'networkx',
            'python-dotenv',
            'prometheus_client',
            'pytest',
            'langchain',
            'langchain_huggingface'
        ]
        
        self.core_modules = [
            'src.config',
            'src.rag',
            'src.rag.agents.base_agent',
            'src.rag.agents.tot_reasoner',
            'src.rag.agents.moe_router',
            'src.rag.agents.agentic_rag',
            'src.rag.agents.data_insight_expert',
            'src.rag.agents.narrative_expert',
            'src.rag.embeddings.document_embedder',
            'src.rag.models.inference',
            'src.rag.processors.document_processor',
            'src.rag.processors.chunk_processor',
            'src.rag.processors.semantic_processor',
            'src.rag.retrieval.multi_vector_retriever',
            'src.rag.retrieval.context_augmenter',
            'src.rag.api.app',
            'src.monitoring.monitor'
        ]
        
        self.required_dirs = [
            'src/rag/agents',
            'src/rag/embeddings',
            'src/rag/indexing',
            'src/rag/models',
            'src/rag/processors',
            'src/rag/retrieval',
            'src/rag/api',
            'src/config',
            'src/monitoring',
            'tests/unit',
            'tests/integration',
            'models/faiss_index'
        ]
        
        self.required_env_vars = [
            'DOCUMENT_MODEL',
            'CHUNK_MODEL',
            'SEMANTIC_MODEL',
            'FLASK_APP',
            'FLASK_ENV',
            'PORT',
            'HUGGINGFACE_API_TOKEN'
        ]

    def check_python_packages(self) -> Tuple[bool, List[str]]:
        """Check required Python packages"""
        print("\n📦 Checking Python packages...")
        missing = []
        for package in self.required_packages:
            try:
                importlib.import_module(package.replace('-', '_'))
                print(f"✅ {package}")
            except ImportError:
                missing.append(package)
                print(f"❌ {package}")
        return len(missing) == 0, missing

    def check_core_modules(self) -> Tuple[bool, List[str]]:
        """Check core module imports"""
        print("\n📂 Checking core modules...")
        errors = []
        for module in self.core_modules:
            try:
                importlib.import_module(module)
                print(f"✅ {module}")
            except ImportError as e:
                errors.append(f"{module}: {str(e)}")
                print(f"❌ {module}")
        return len(errors) == 0, errors

    def check_directory_structure(self) -> Tuple[bool, List[str]]:
        """Check required directory structure"""
        print("\n📁 Checking directory structure...")
        missing = []
        for dir_path in self.required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing.append(dir_path)
                print(f"❌ {dir_path}")
            else:
                print(f"✅ {dir_path}")
        return len(missing) == 0, missing

    def check_environment_variables(self) -> Tuple[bool, List[str]]:
        """Check required environment variables"""
        print("\n🔧 Checking environment variables...")
        missing = []
        for var in self.required_env_vars:
            if not os.getenv(var):
                missing.append(var)
                print(f"❌ {var}")
            else:
                print(f"✅ {var}")
        return len(missing) == 0, missing

    def check_docker(self) -> Tuple[bool, List[str]]:
        """Check Docker setup"""
        print("\n🐳 Checking Docker setup...")
        errors = []
        
        # Check Docker installation
        try:
            subprocess.run(['docker', '--version'], check=True, capture_output=True)
            print("✅ Docker is installed")
        except Exception as e:
            errors.append(f"Docker not installed: {str(e)}")
            print("❌ Docker not installed")

        # Check Docker Compose
        try:
            subprocess.run(['docker-compose', '--version'], check=True, capture_output=True)
            print("✅ Docker Compose is installed")
        except Exception as e:
            errors.append(f"Docker Compose not installed: {str(e)}")
            print("❌ Docker Compose not installed")

        return len(errors) == 0, errors

    def check_model_downloads(self) -> Tuple[bool, List[str]]:
        """Check if required models are downloaded"""
        print("\n🤖 Checking model downloads...")
        errors = []
        try:
            from sentence_transformers import SentenceTransformer
            models = [
                'sentence-transformers/all-mpnet-base-v2',
                'sentence-transformers/all-MiniLM-L6-v2',
                'sentence-transformers/paraphrase-multilingual-mpnet-base-v2',
                'BAAI/bge-large-en-v1.5'
            ]
            
            for model_name in models:
                try:
                    _ = SentenceTransformer(model_name)
                    print(f"✅ {model_name}")
                except Exception as e:
                    errors.append(f"Error loading {model_name}: {str(e)}")
                    print(f"❌ {model_name}")
        except ImportError:
            errors.append("sentence-transformers not installed")
            print("❌ sentence-transformers not installed")
            
        return len(errors) == 0, errors

    def run_validation(self) -> bool:
        """Run all validation checks"""
        print("🔍 Starting comprehensive validation...")
        
        # Run all checks
        checks = [
            (self.check_python_packages, "Python packages"),
            (self.check_core_modules, "Core modules"),
            (self.check_directory_structure, "Directory structure"),
            (self.check_environment_variables, "Environment variables"),
            (self.check_docker, "Docker setup"),
            (self.check_model_downloads, "Model downloads")
        ]
        
        all_passed = True
        all_errors = {}
        
        for check_func, check_name in checks:
            passed, errors = check_func()
            if not passed:
                all_passed = False
                all_errors[check_name] = errors
        
        # Print summary
        print("\n📋 Validation Summary:")
        if all_passed:
            print("\n✅ All checks passed!")
        else:
            print("\n❌ Some checks failed:")
            for check_name, errors in all_errors.items():
                print(f"\n{check_name}:")
                for error in errors:
                    print(f"  - {error}")
                    
            print("\nTo fix issues:")
            print("1. Run 'pip install -e .' to install dependencies")
            print("2. Copy .env.example to .env and configure")
            print("3. Run 'scripts/windows/fix_common_issues.bat'")
            
        return all_passed

def main():
    validator = RAGValidator()
    success = validator.run_validation()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
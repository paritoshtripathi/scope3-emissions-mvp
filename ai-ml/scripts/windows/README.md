# Windows Development Scripts

This directory contains scripts for Windows development environment setup and validation.

## Available Scripts

### validate.bat
Runs comprehensive validation of the RAG system:
- Python package dependencies
- Core module imports
- Directory structure
- Environment variables
- Docker setup
- Model downloads
- GPU support

```batch
scripts\windows\validate.bat
```

### fix_common_issues.bat
Attempts to fix common setup issues:
- Creates missing directories
- Installs dependencies
- Downloads required models
- Sets up environment file

```batch
scripts\windows\fix_common_issues.bat
```

### clean.bat
Cleans up development artifacts:
- Python cache files
- Build directories
- Test cache
- Coverage reports

```batch
scripts\windows\clean.bat
```

## Validation System

The validation system (validate.py) checks:

1. Python Environment
   - Required packages
   - Core module imports
   - GPU support

2. Project Structure
   - Directory structure
   - File organization
   - Required resources

3. Environment Setup
   - Environment variables
   - Configuration files
   - Model downloads

4. Docker Setup
   - Docker installation
   - Docker Compose
   - Service configuration

## Error Handling

If validation fails:
1. Check the error messages
2. Run fix_common_issues.bat
3. If issues persist, refer to the main README.md for manual setup steps

## Adding New Checks

To add new validation checks:
1. Update RAGValidator class in validate.py
2. Add required parameters/modules to check
3. Update fix_common_issues.bat if needed
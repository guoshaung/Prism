# Contributing to innersafe-mas

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/innersafe-mas.git
   cd innersafe-mas
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Maximum line length: 88 characters (Black default)
- Run linters before committing:
  ```bash
  ruff check src/
  black src/
  mypy src/
  ```

## Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Run tests locally:
  ```bash
  pytest tests/ -v --cov=innersafe_mas
  ```

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes with clear commit messages
3. Add tests for new functionality
4. Update documentation if needed
5. Run the full test suite
6. Submit a PR with a clear description

## Documentation

- Add docstrings to all public classes and methods
- Follow Google-style docstring format
- Update `docs/architecture.md` for architectural changes
- Include examples in `examples/` for new features

## Reporting Issues

- Use GitHub Issues for bug reports and feature requests
- Include minimal reproducible examples
- Specify your Python version and OS

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 License.

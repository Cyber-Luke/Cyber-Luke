# Testing

This project uses `pytest` for unit testing with comprehensive test coverage.

## Running Tests Locally

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run Tests with Coverage

```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Generate HTML Coverage Report

```bash
pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html in your browser
```

## Test Structure

- `tests/test_today.py` - Unit tests for `today.py` functionality
- All tests use mocking to avoid real API calls
- Tests follow pytest best practices with clear test names and fixtures

## Continuous Integration

Tests run automatically on every push and pull request via GitHub Actions. The workflow tests against multiple Python versions (3.8, 3.9, 3.10, 3.11) to ensure compatibility.

## Coverage Goals

We aim for >80% code coverage on core functionality. Tests focus on:

- API data processing functions
- SVG manipulation logic
- Data formatting and counting
- Error handling

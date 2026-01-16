# IP List Manager Copilot Instructions

## Project Overview
This is a lightweight Python library for managing lists of IP addresses loaded from files. It focuses on IPv4 validation, list management, and integration with basic file-based workflows.

**Runtime Requirement**: The codebase must remain strictly compatible with Python 3.8.6.

## Architecture & Code Structure
- **Core Logic**: `ip_list.py` contains the `IPList` class which handles file reading, parsing, and validation.
- **Data Handling**:
  - Only IPv4 addresses are supported. IPv6 addresses are treated as invalid/ignored based on configuration.
  - File format: One IP per line, supports `#` comments.
- **Dependencies**: Zero external dependencies. Uses Python Standard Library (`ipaddress`, `pathlib`, `logging`, `typing`, `unittest`).

## Developer Workflow

### Testing
- Tests are located in `tests/`.
- Run all tests using `unittest`:
  ```bash
  python -m unittest discover tests
  ```
- Tests use a `sys.path` modification to import the local module:
  ```python
  sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
  ```

### Debugging
- The code uses the `logging` module.
- Check `logging.debug()` output for file reading operations and validation failures.

## Coding Conventions
- **Paths**: Always use `pathlib.Path` objects instead of path strings.
- **Type Hinting**: Use strict type hints (`typing.Union`, `typing.Set`, etc.) for all methods.
- **Docstrings**: Include comprehensive docstrings for classes and methods, detailing arguments and return values.
- **Error Handling**:
  - `ignore_invalid=True` will skip malformed lines and allowed IPv6 addresses (logged as debug).
  - `ignore_invalid=False` raises `ValueError`.

## Specific Patterns
- **IP Validation**:
  ```python
  # Always check version explicitly
  if ip.version == 4:
      self.ip_list.add(line)
  elif ip.version == 6:
      # Explicit logic for IPv6 exclusion
  ```
- **File Parsing**: Strip whitespace and check for comments (`#`) before validation.

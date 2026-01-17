# IP List Manager Copilot Instructions

## Project Overview
This is a lightweight Python library for managing lists of IP addresses loaded from files. It focuses on IPv4 validation, list management, and integration with basic file-based workflows.

**Critical Requirements:**
- **Python Version**: Must remain strictly compatible with Python 3.8.6 - do not use features from newer Python versions
- **Zero Dependencies**: Only use Python Standard Library - never add external dependencies

## Architecture & Code Structure
- **Core Logic**: `ip_list.py` contains the `IPList` class which handles file reading, parsing, and validation.
- **Data Handling**:
  - Only IPv4 addresses are supported. IPv6 addresses are treated as invalid/ignored based on configuration.
  - File format: One IP per line, supports `#` comments.
- **Standard Library Modules**: `ipaddress`, `pathlib`, `logging`, `typing`, `unittest`, `tempfile`, `contextlib`

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
- **Paths**: Always use `pathlib.Path` objects instead of path strings. Never use string concatenation for paths.
- **Type Hinting**: Use strict type hints (`typing.Union`, `typing.Set`, `typing.Optional`, `typing.List`) for all methods and function signatures.
- **Docstrings**: Include comprehensive docstrings for all classes and methods, detailing:
  - Args with types
  - Returns with types
  - Raises (exceptions that may be raised)
  - Examples where helpful
- **Error Handling**:
  - `ignore_invalid=True` will skip malformed lines and IPv6 addresses (logged as debug).
  - `ignore_invalid=False` raises `ValueError` for invalid data.
  - Always use specific exception types, never bare `except:` clauses.
- **Logging**: Use the `logging` module for all output. Log at appropriate levels (DEBUG for detailed info, INFO for important events, WARNING for issues).

## Specific Patterns
- **IP Validation**:
  ```python
  # Always check version explicitly
  if ip.version == 4:
      self.ip_list.add(line)
  elif ip.version == 6:
      # Explicit logic for IPv6 exclusion
      if self.ignore_invalid:
          logging.debug(f"Ignoring IPv6 address: {line}")
      else:
          raise ValueError(f"IPv6 address found and not ignored: {line}")
  ```
- **File Parsing**: Strip whitespace and check for comments (`#`) before validation:
  ```python
  line = line.strip()
  if not line or "#" in line:
      continue
  ```
- **Temporary File Handling**: Always clean up temporary files, prefer context managers:
  ```python
  with ip_list.to_tempfile() as temp_path:
      # Use temp_path
      # File automatically deleted on exit
  ```

## Security Considerations
- Always validate file paths using `pathlib.Path` to prevent directory traversal attacks
- Never trust user-provided IP addresses without validation through `ipaddress.ip_address()`
- Log security-relevant events (invalid IPs, file access errors) appropriately
- Use `missing_ok=True` when unlinking files to handle race conditions gracefully

## Rules and Restrictions

### Must Do
- Always validate IP addresses using the `ipaddress` module from the standard library
- Check IP version explicitly (`ip.version == 4` or `ip.version == 6`)
- Use context managers (`with` statements) for file operations
- Write tests for any new functionality
- Preserve backwards compatibility

### Must NOT Do
- **Never** add external dependencies (pip packages) - this library must use only the Python Standard Library
- **Never** use Python features introduced after 3.8.6 (e.g., avoid `match` statements, `|` for Union types, etc.)
- **Never** use `os.path` - always use `pathlib.Path` instead
- **Never** hardcode file paths - accept them as parameters
- **Never** ignore security: validate and sanitize file paths to prevent directory traversal
- **Never** remove existing tests or reduce test coverage
- **Never** change the public API without careful consideration of backwards compatibility

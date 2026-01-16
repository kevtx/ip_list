#!/usr/bin/env python3
"""
Example usage demonstrating new IPList features:
- Initializing with a list of IPs
- Creating temporary files from IP lists
"""

import logging

from ip_list import IPList

# Suppress debug logs for cleaner output
logging.getLogger().setLevel(logging.WARNING)


def example_list_initialization():
    """Example: Initialize IPList with a list of IPs."""
    print("=" * 60)
    print("Example 1: Initialize IPList with a list of IPs")
    print("=" * 60)

    ips = ["192.168.1.1", "10.0.0.1", "8.8.8.8", "1.1.1.1"]
    ip_list = IPList(ips=ips)

    print(f"Created IPList: {ip_list}")
    print(f"Contains 8.8.8.8: {'8.8.8.8' in ip_list}")
    print(f"Contains 5.5.5.5: {'5.5.5.5' in ip_list}")
    print()


def example_tempfile_basic():
    """Example: Write IP list to a temporary file."""
    print("=" * 60)
    print("Example 2: Write IP list to temporary file")
    print("=" * 60)

    ips = ["192.168.1.1", "10.0.0.1", "8.8.8.8"]
    ip_list = IPList(ips=ips)

    # Create a temp file (caller is responsible for cleanup)
    temp_path = ip_list.write_to_tempfile()
    print(f"Created temporary file: {temp_path}")

    # Read it back to verify
    with open(temp_path, "r") as f:
        print("Contents:")
        print(f.read())

    # Clean up
    temp_path.unlink()
    print("Temporary file deleted")
    print()


def example_tempfile_context_manager():
    """Example: Use context manager for automatic cleanup."""
    print("=" * 60)
    print("Example 3: Context manager with automatic cleanup")
    print("=" * 60)

    ips = ["192.168.1.1", "10.0.0.1", "172.16.0.1"]
    ip_list = IPList(ips=ips)

    with ip_list.to_tempfile() as temp_path:
        print(f"Using temporary file: {temp_path}")

        # File can be used by external tools
        # For example, loading it back into another IPList
        loaded_list = IPList(temp_path)
        print(f"Loaded back: {loaded_list}")
        print(f"IP lists match: {ip_list == loaded_list}")

    print("Temporary file automatically deleted after context exit")
    print()


def example_mixed_usage():
    """Example: Combining file-based and list-based IPLists."""
    print("=" * 60)
    print("Example 4: Mixed usage - file and list based")
    print("=" * 60)

    # Create list-based IPList
    list_ips = ["192.168.1.1", "10.0.0.1"]
    list_based = IPList(ips=list_ips)

    # Convert to temp file and use it
    with list_based.to_tempfile() as temp_path:
        # Now create a file-based IPList from the temp file
        file_based = IPList(temp_path)

        print(f"List-based: {list_based}")
        print(f"File-based: {file_based}")
        print(f"Are equal: {list_based == file_based}")

    print()


def example_invalid_ips():
    """Example: Handling invalid IPs."""
    print("=" * 60)
    print("Example 5: Handling invalid IPs")
    print("=" * 60)

    # With ignore_invalid=False (default), invalid IPs raise errors
    try:
        IPList(ips=["192.168.1.1", "not-an-ip", "10.0.0.1"])
    except ValueError as e:
        print(f"Error with ignore_invalid=False: {e}")

    # With ignore_invalid=True, invalid IPs are skipped
    ip_list = IPList(ips=["192.168.1.1", "not-an-ip", "10.0.0.1"], ignore_invalid=True)
    print(f"With ignore_invalid=True: {ip_list}")
    print(f"Only valid IPs loaded: {sorted(ip_list.values)}")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("IPList Usage Examples")
    print("=" * 60 + "\n")

    example_list_initialization()
    example_tempfile_basic()
    example_tempfile_context_manager()
    example_mixed_usage()
    example_invalid_ips()

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)

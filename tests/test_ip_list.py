import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the sys.path to allow imports from the main project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ip_list import IPList


class TestIPList(unittest.TestCase):
    def setUp(self):
        """Set up test files."""
        self.test_dir = Path("test_data")
        self.test_dir.mkdir(exist_ok=True)

        self.valid_ips_file = self.test_dir / "valid_ips.txt"
        with open(self.valid_ips_file, "w") as f:
            f.write("192.168.1.1\n")
            f.write("10.0.0.1\n")
            f.write("# This is a comment\n")
            f.write("\n")
            f.write(
                "2001:0db8:85a3:0000:0000:8a2e:0370:7334\n"
            )  # Valid IPv6, but IPv6 is unsupported so treated as invalid

        self.invalid_ips_file = self.test_dir / "invalid_ips.txt"
        with open(self.invalid_ips_file, "w") as f:
            f.write("192.168.1.1\n")
            f.write("not-an-ip\n")
            f.write("10.0.0.2\n")

        self.empty_file = self.test_dir / "empty.txt"
        self.empty_file.touch()

        self.ipv6_file = self.test_dir / "ipv6.txt"
        with open(self.ipv6_file, "w") as f:
            f.write("2001:0db8:85a3:0000:0000:8a2e:0370:7334\n")

    def tearDown(self):
        """Clean up test files."""
        for f in self.test_dir.iterdir():
            f.unlink()
        self.test_dir.rmdir()

    def test_read_valid_ips(self):
        """Test reading a file with valid IP addresses."""
        ip_list = IPList(self.valid_ips_file, ignore_invalid=True)
        self.assertEqual(len(ip_list.ip_list), 2)
        self.assertIn("192.168.1.1", ip_list)
        self.assertIn("10.0.0.1", ip_list)
        self.assertNotIn("2001:0db8:85a3:0000:0000:8a2e:0370:7334", ip_list)

    def test_read_invalid_ips_raise_error(self):
        """Test reading a file with invalid IPs and ignore_invalid=False."""
        with self.assertRaises(ValueError):
            IPList(self.invalid_ips_file)

    def test_read_ipv6_raise_error(self):
        """Test reading a file with an IPv6 address and ignore_invalid=False."""
        with self.assertRaisesRegex(ValueError, "IPv6 address found and not ignored"):
            IPList(self.ipv6_file)

    def test_read_invalid_ips_ignore(self):
        """Test reading a file with invalid IPs and ignore_invalid=True."""
        ip_list = IPList(self.invalid_ips_file, ignore_invalid=True)
        self.assertEqual(len(ip_list.ip_list), 2)
        self.assertIn("192.168.1.1", ip_list)
        self.assertIn("10.0.0.2", ip_list)
        self.assertNotIn("not-an-ip", ip_list)

    def test_reload(self):
        """Test reloading the IP list from the file."""
        ip_list = IPList(self.valid_ips_file, ignore_invalid=True)
        self.assertEqual(len(ip_list.ip_list), 2)

        with open(self.valid_ips_file, "a") as f:
            f.write("8.8.8.8\n")

        ip_list.reload()
        self.assertEqual(len(ip_list.ip_list), 3)
        self.assertIn("8.8.8.8", ip_list)

    def test_equality(self):
        """Test the equality comparison of two IPList objects."""
        ip_list1 = IPList(self.valid_ips_file, ignore_invalid=True)
        ip_list2 = IPList(self.valid_ips_file, ignore_invalid=True)
        self.assertEqual(ip_list1, ip_list2)

        ip_list3 = IPList(self.invalid_ips_file, ignore_invalid=True)
        self.assertNotEqual(ip_list1, ip_list3)
        self.assertNotEqual(ip_list1, "not an IPList")

    def test_contains(self):
        """Test the 'in' operator."""
        ip_list = IPList(self.valid_ips_file, ignore_invalid=True)
        self.assertIn("192.168.1.1", ip_list)
        self.assertNotIn("1.1.1.1", ip_list)

    def test_repr(self):
        """Test the __repr__ method."""
        ip_list = IPList(self.valid_ips_file, ignore_invalid=True)
        expected_repr = (
            f"IPList(file_path={ip_list.file_path}, ignore_invalid=True, ip_count=2)"
        )
        self.assertEqual(repr(ip_list), expected_repr)

    def test_str(self):
        """Test the __str__ method."""
        ip_list = IPList(self.valid_ips_file, ignore_invalid=True)
        expected_str = f"IPList with 2 IPs from {ip_list.file_path}"
        self.assertEqual(str(ip_list), expected_str)

    def test_empty_file(self):
        """Test reading from an empty file."""
        ip_list = IPList(self.empty_file)
        self.assertEqual(len(ip_list.ip_list), 0)

    def test_init_with_list(self):
        """Test initializing IPList with a list of IPs."""
        ips = ["192.168.1.1", "10.0.0.1", "8.8.8.8"]
        ip_list = IPList(ip_addresses=ips)
        self.assertEqual(len(ip_list.ip_list), 3)
        self.assertIn("192.168.1.1", ip_list)
        self.assertIn("10.0.0.1", ip_list)
        self.assertIn("8.8.8.8", ip_list)
        self.assertIsNone(ip_list.file_path)

    def test_init_with_list_invalid_ips_raise(self):
        """Test initializing with invalid IPs and ignore_invalid=False."""
        ips = ["192.168.1.1", "not-an-ip", "10.0.0.1"]
        with self.assertRaises(ValueError):
            IPList(ip_addresses=ips)

    def test_init_with_list_invalid_ips_ignore(self):
        """Test initializing with invalid IPs and ignore_invalid=True."""
        ips = ["192.168.1.1", "not-an-ip", "10.0.0.1"]
        ip_list = IPList(ip_addresses=ips, ignore_invalid=True)
        self.assertEqual(len(ip_list.ip_list), 2)
        self.assertIn("192.168.1.1", ip_list)
        self.assertIn("10.0.0.1", ip_list)

    def test_init_with_list_ipv6_raise(self):
        """Test initializing with IPv6 and ignore_invalid=False."""
        ips = ["192.168.1.1", "2001:0db8:85a3:0000:0000:8a2e:0370:7334"]
        with self.assertRaisesRegex(ValueError, "IPv6 address found and not ignored"):
            IPList(ip_addresses=ips)

    def test_init_with_list_ipv6_ignore(self):
        """Test initializing with IPv6 and ignore_invalid=True."""
        ips = ["192.168.1.1", "2001:0db8:85a3:0000:0000:8a2e:0370:7334", "10.0.0.1"]
        ip_list = IPList(ip_addresses=ips, ignore_invalid=True)
        self.assertEqual(len(ip_list.ip_list), 2)
        self.assertIn("192.168.1.1", ip_list)
        self.assertIn("10.0.0.1", ip_list)

    def test_init_with_list_comments_and_whitespace(self):
        """Test initializing with list containing comments and whitespace."""
        ips = ["192.168.1.1", "  10.0.0.1  ", "# comment", "", "8.8.8.8"]
        ip_list = IPList(ip_addresses=ips, ignore_invalid=True)
        self.assertEqual(len(ip_list.ip_list), 3)
        self.assertIn("192.168.1.1", ip_list)
        self.assertIn("10.0.0.1", ip_list)
        self.assertIn("8.8.8.8", ip_list)

    def test_init_no_args_raises(self):
        """Test that initializing without file_path or ip_addresses raises ValueError."""
        with self.assertRaisesRegex(
            ValueError, "Either file_path or ip_addresses must be provided"
        ):
            IPList()

    def test_init_both_args_raises(self):
        """Test that providing both file_path and ip_addresses raises ValueError."""
        ips = ["192.168.1.1"]
        with self.assertRaisesRegex(
            ValueError, "Cannot provide both file_path and ip_addresses"
        ):
            IPList(file_path=self.valid_ips_file, ip_addresses=ips)

    def test_write_to_tempfile(self):
        """Test writing IP list to a temporary file."""
        ips = ["192.168.1.1", "10.0.0.1", "8.8.8.8"]
        ip_list = IPList(ip_addresses=ips)
        temp_file = ip_list.write_to_tempfile()

        try:
            self.assertTrue(temp_file.exists())
            with open(temp_file, "r") as f:
                content = f.read().strip().split("\n")
            # Should be sorted
            self.assertEqual(content, ["10.0.0.1", "192.168.1.1", "8.8.8.8"])
        finally:
            temp_file.unlink(missing_ok=True)

    def test_to_tempfile_context_manager(self):
        """Test the to_tempfile context manager."""
        ips = ["192.168.1.1", "10.0.0.1"]
        ip_list = IPList(ip_addresses=ips)

        with ip_list.to_tempfile() as temp_path:
            self.assertTrue(temp_path.exists())
            with open(temp_path, "r") as f:
                content = f.read().strip().split("\n")
            self.assertEqual(sorted(content), ["10.0.0.1", "192.168.1.1"])
            temp_file_saved = temp_path

        # File should be deleted after context exits
        self.assertFalse(temp_file_saved.exists())

    def test_reload_without_file_raises(self):
        """Test that reload raises ValueError when no file_path is set."""
        ips = ["192.168.1.1"]
        ip_list = IPList(ip_addresses=ips)
        with self.assertRaisesRegex(ValueError, "Cannot reload: no file_path set"):
            ip_list.reload()

    def test_read_without_file_raises(self):
        """Test that read raises ValueError when no file_path is set."""
        ips = ["192.168.1.1"]
        ip_list = IPList(ip_addresses=ips)
        with self.assertRaisesRegex(ValueError, "Cannot read from file: no file_path set"):
            ip_list.read()

    def test_repr_with_list(self):
        """Test __repr__ for list-based initialization."""
        ips = ["192.168.1.1", "10.0.0.1"]
        ip_list = IPList(ip_addresses=ips)
        expected_repr = "IPList(from_list=True, ignore_invalid=False, ip_count=2)"
        self.assertEqual(repr(ip_list), expected_repr)

    def test_str_with_list(self):
        """Test __str__ for list-based initialization."""
        ips = ["192.168.1.1", "10.0.0.1"]
        ip_list = IPList(ip_addresses=ips)
        expected_str = "IPList with 2 IPs from list"
        self.assertEqual(str(ip_list), expected_str)

    def test_tempfile_usage_with_file_based_iplist(self):
        """Test that tempfile methods work with file-based IPList too."""
        ip_list = IPList(self.valid_ips_file, ignore_invalid=True)
        
        with ip_list.to_tempfile() as temp_path:
            self.assertTrue(temp_path.exists())
            # Read back and verify
            temp_ip_list = IPList(temp_path)
            self.assertEqual(ip_list.ip_list, temp_ip_list.ip_list)


if __name__ == "__main__":
    unittest.main()

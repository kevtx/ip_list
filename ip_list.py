import ipaddress
import logging
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional, Set, Union

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class IPList:
    """
    A list of IP addresses.
    Attributes:
        file_path (Path | None): The path to the file containing IP addresses.
        ignore_invalid (bool): Whether to ignore invalid IP addresses.
        ip_list (Set[str]): A set of valid IP addresses.

    Methods:
        read(): Reads and validates IP addresses from the file.
        reload(): Re-reads the IPs from the file.
        write_to_tempfile(): Writes the IP list to a temporary file and returns the path.
        to_tempfile(): Context manager for temporary file creation.
    """

    def __init__(
        self,
        file_path: Optional[Union[str, Path]] = None,
        ignore_invalid: bool = False,
        ip_addresses: Optional[List[str]] = None,
    ):
        """
        Initializes the IPList object.

        Args:
            file_path (str | Path | None): The path to the file containing IP addresses.
            ignore_invalid (bool): If True, invalid IPs are ignored. If False, a ValueError is raised.
            ip_addresses (List[str] | None): A list of IP addresses to initialize with (instead of a file).

        Raises:
            ValueError: If neither file_path nor ip_addresses is provided, or if both are provided.
        """
        if file_path is None and ip_addresses is None:
            raise ValueError("Either file_path or ip_addresses must be provided")
        if file_path is not None and ip_addresses is not None:
            raise ValueError("Cannot provide both file_path and ip_addresses")

        self.file_path = Path(file_path) if file_path is not None else None
        self.ignore_invalid = ignore_invalid
        self.ip_list: Set[str] = set()

        if ip_addresses is not None:
            self._load_from_list(ip_addresses)
        else:
            self.read()

    def _load_from_list(self, ip_addresses: List[str]):
        """
        Loads and validates IP addresses from a list.

        Args:
            ip_addresses (List[str]): A list of IP address strings.
        """
        logging.debug("Loading IP list from provided list")
        self.ip_list.clear()
        for line in ip_addresses:
            line = line.strip()
            if not line or "#" in line:
                continue
            try:
                ip = ipaddress.ip_address(line)
            except ValueError:
                if self.ignore_invalid:
                    logging.debug(f"Ignoring invalid IP address: {line}")
                    continue
                else:
                    raise ValueError(f"Invalid IP address found: {line}")

            if ip.version == 4:
                self.ip_list.add(line)
            elif ip.version == 6:
                if self.ignore_invalid:
                    logging.debug(f"Ignoring IPv6 address: {line}")
                else:
                    raise ValueError(f"IPv6 address found and not ignored: {line}")
        logging.info(f"Loaded {len(self.ip_list)} IPs from list")

    def read(self):
        """
        Reads and validates IP addresses from the file.

        Raises:
            ValueError: If no file_path is set.
        """
        if self.file_path is None:
            raise ValueError("Cannot read from file: no file_path set")
        logging.debug(f"Reading IP list from {self.file_path}")
        self.ip_list.clear()
        with open(self.file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or "#" in line:
                    continue
                try:
                    ip = ipaddress.ip_address(line)
                except ValueError:
                    if self.ignore_invalid:
                        logging.debug(f"Ignoring invalid IP address: {line}")
                        continue
                    else:
                        raise ValueError(f"Invalid IP address found: {line}")

                if ip.version == 4:
                    self.ip_list.add(line)
                elif ip.version == 6:
                    if self.ignore_invalid:
                        logging.debug(f"Ignoring IPv6 address: {line}")
                    else:
                        raise ValueError(f"IPv6 address found and not ignored: {line}")
                logging.info(f"Loaded IP list from: {self.file_path}")

    def reload(self):
        """
        Re-reads the IPs from the file.

        Raises:
            ValueError: If no file_path is set.
        """
        if self.file_path is None:
            raise ValueError("Cannot reload: no file_path set")
        logging.debug("Reloading IP list.")
        self.read()

    def write_to_tempfile(self) -> Path:
        """
        Writes the IP list to a temporary file.

        Returns:
            Path: The path to the created temporary file.

        Note:
            The caller is responsible for deleting the temporary file.
        """
        temp_fd, temp_path = tempfile.mkstemp(suffix=".txt", prefix="iplist_")
        temp_file = Path(temp_path)
        try:
            with open(temp_fd, "w") as f:
                for ip in sorted(self.ip_list):
                    f.write(f"{ip}\n")
            logging.debug(f"Wrote IP list to temporary file: {temp_file}")
            return temp_file
        except Exception:
            # Clean up on error
            temp_file.unlink(missing_ok=True)
            raise

    @contextmanager
    def to_tempfile(self):
        """
        Context manager that writes the IP list to a temporary file.
        The file is automatically deleted when the context exits.

        Yields:
            Path: The path to the temporary file.

        Example:
            with ip_list.to_tempfile() as temp_path:
                # Use temp_path here
                process_file(temp_path)
            # File is automatically deleted after the block
        """
        temp_file = None
        try:
            temp_file = self.write_to_tempfile()
            yield temp_file
        finally:
            if temp_file is not None:
                temp_file.unlink(missing_ok=True)
                logging.debug(f"Deleted temporary file: {temp_file}")

    def __eq__(self, other):
        """
        Checks equality with another IPList instance.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if the IP lists are equal, False otherwise.
        """
        if isinstance(other, IPList):
            return self.ip_list == other.ip_list
        return False

    def __contains__(self, ip: str) -> bool:
        """
        Checks if a given IP is in the list.

        Args:
            ip (str): The IP address to check.

        Returns:
            bool: True if the IP is in the list, False otherwise.
        """
        return ip in self.ip_list

    def __repr__(self):
        file_info = f"file_path={self.file_path}" if self.file_path else "from_list=True"
        return f"IPList({file_info}, ignore_invalid={self.ignore_invalid}, ip_count={len(self.ip_list)})"

    def __str__(self):
        source = str(self.file_path) if self.file_path else "list"
        return f"IPList with {len(self.ip_list)} IPs from {source}"

    def __reduce__(self):
        # For pickling: convert ip_list back to list for ip_addresses parameter
        if self.file_path is not None:
            return (self.__class__, (self.file_path, self.ignore_invalid, None))  # type: ignore
        else:
            return (self.__class__, (None, self.ignore_invalid, list(self.ip_list)))  # type: ignore

    def __len__(self):
        return len(self.ip_list)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage a list of IP addresses from a file."
    )
    parser.add_argument(
        "file_path", type=str, help="Path to the file containing IP addresses."
    )
    parser.add_argument(
        "--ignore-invalid", action="store_true", help="Ignore invalid IP addresses."
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Silence output")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Verbose logging is enabled.")
    elif args.quiet:
        logging.getLogger().setLevel(logging.CRITICAL + 10)
    else:
        logging.getLogger().setLevel(logging.INFO)

    ip_list = IPList(args.file_path, ignore_invalid=args.ignore_invalid)
    logging.info(f"IP Addresses: {','.join(ip_list.ip_list)}")

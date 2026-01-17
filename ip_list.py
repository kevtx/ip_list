import ipaddress
import logging
import tempfile
from contextlib import contextmanager
from pathlib import Path
from shlex import quote
from typing import List, Optional, Set, Union

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class IPList:
    """
    A list of IP addresses.

    Attributes:
        file_path (Path | None): The path to the file containing IP addresses.
            aliases: file, path
            coersion: quoted_abs[olute]
        ignore_invalid (bool): Whether to ignore invalid IP addresses.
        ips (Set[str]): A set of valid IP addresses.
            aliases: values, set
            coersions: list

    Methods:
        read(): Reads and validates IP addresses from the file.
        reload(): Re-reads the IPs from the file, overwriting the existing '.ips' attribute.
        write_to_tempfile(): Writes the IP list to a temporary file and returns the path object.
        to_tempfile(): Context manager for temporary file creation.

    Supported dunders: __contains__, __eq__, __len__, __reduce__, __repr__, __str__

    """

    def __init__(
        self,
        file_path: Optional[Union[str, Path]] = None,
        ignore_invalid: bool = False,
        ips: Optional[List[str]] = None,
    ):
        """
        Initializes the IPList object.

        Args:
            file_path (str | Path | None): The path to the file containing IP addresses.
            ignore_invalid (bool): If True, invalid IPs are ignored. If False, a ValueError is raised.
            ips (List[str] | None): A list of IP addresses to initialize with (instead of a file).

        Raises:
            ValueError: If neither file_path nor ips is provided, or if both are provided.
        """
        if file_path is None and ips is None:
            raise ValueError("Either file_path or ips must be provided")
        if file_path is not None and ips is not None:
            raise ValueError("Cannot provide both file_path and ips")

        self.file_path = Path(file_path) if file_path is not None else None
        self.ignore_invalid = ignore_invalid
        self.ips: Set[str] = set()

        if ips is not None:
            self._load_from_list(ips)
        else:
            self.read()

    def _load_from_list(self, ips: List[str]):
        """
        Loads and validates IP addresses from a list.

        Args:
            ips (List[str]): A list of IP address strings.
        """
        logging.debug("Loading IP list from provided list")
        self.ips.clear()
        for line in ips:
            # Normalize whitespace
            line = line.strip()
            if not line:
                # Skip empty lines
                continue

            # Handle inline comments in the same way as file-based loading:
            # take only the part before the first '#' and strip it again.
            if "#" in line:
                line = line.split("#", 1)[0].strip()
                if not line:
                    # Line contained only a comment after stripping
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
                self.ips.add(line)
            elif ip.version == 6:
                if self.ignore_invalid:
                    logging.debug(f"Ignoring IPv6 address: {line}")
                else:
                    raise ValueError(f"IPv6 address found and not ignored: {line}")
        logging.info(f"Loaded {len(self.ips)} IPs from list")

    def read(self):
        """
        Reads and validates IP addresses from the file.

        Raises:
            ValueError: If no file_path is set.
        """
        if self.file_path is None:
            raise ValueError("Cannot read from file: no file_path set")
        logging.debug(f"Reading IP list from {self.file_path}")
        self.ips.clear()
        ips_from_file = set()
        with open(self.file_path, "r") as f:
            for line in f:
                line = line.strip()
                if "#" in line:
                    line = line.split("#", 1)[0].strip()
                if not line:
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
                    ips_from_file.add(line)
                elif ip.version == 6:
                    if self.ignore_invalid:
                        logging.debug(f"Ignoring IPv6 address: {line}")
                    else:
                        raise ValueError(f"IPv6 address found and not ignored: {line}")

        self.ips.clear()
        self.ips = ips_from_file
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
                for ip in sorted(self.ips):
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
            return self.ips == other.ips
        return False

    def __contains__(self, ip: object) -> bool:
        """Check whether a value is contained in this list.

        This implements the standard container protocol used by
        membership tests (``in`` / ``not in``) and by helpers such as
        ``unittest.TestCase.assertIn``.

        Args:
            ip (object): Value to test for membership. Only strings are
                considered valid IP candidates; any non-string value
                will return ``False``.

        Returns:
            bool: ``True`` if *ip* is a string and is present in the
            underlying IP set, otherwise ``False``.
        """
        if not isinstance(ip, str):
            return False
        return ip in self.ips

    def __repr__(self):
        file_info = (
            f"file_path={self.file_path}" if self.file_path else "from_list=True"
        )
        return f"IPList({file_info}, ignore_invalid={self.ignore_invalid}, ip_count={len(self.ips)})"

    def __str__(self):
        source = str(self.file_path) if self.file_path else "list"
        return f"IPList with {len(self.ips)} IPs from {source}"

    def __reduce__(self):
        # For pickling: convert ip_list back to list for ips parameter
        if self.file_path is not None:
            return (self.__class__, (self.file_path, self.ignore_invalid, None))  # type: ignore
        else:
            return (self.__class__, (None, self.ignore_invalid, list(self.ips)))  # type: ignore

    def __len__(self):
        return len(self.ips)

    @property
    def file(self):
        """
        Alias for :attr:`file_path`.

        Returns
        -------
        Optional[pathlib.Path]
            The path to the underlying IP list file, or ``None`` if this
            instance was created from an in-memory list of IPs.
        """
        return self.file_path

    @property
    def path(self):
        """
        Alias for :attr:`file_path`.

        Returns
        -------
        Optional[pathlib.Path]
            The path to the underlying IP list file, or ``None`` if this
            instance was created from an in-memory list of IPs.
        """
        return self.file_path

    @property
    def set(self):
        """
        Alias for :attr:`ips`.

        Returns
        -------
        Set[str]
            The internal set of IPv4 address strings managed by this instance.
            Mutating this set will affect the contents of the ``IPList``.
        """
        return self.ips

    @property
    def values(self):
        """
        Alias for :attr:`ips`.

        Returns
        -------
        Set[str]
            The internal set of IPv4 address strings managed by this instance.
            Mutating this set will affect the contents of the ``IPList``.
        """
        return self.ips

    @property
    def list(self):
        """
        List view of :attr:`ips`.

        Returns
        -------
        List[str]
            A list containing all IPv4 address strings currently stored in
            the internal set. The returned list is a copy and can be mutated
            without affecting the underlying set.
        """
        return list(self.ips)

    @property
    def quoted_abs(self):
        """
        Shell-quoted absolute path to the backing file.

        Returns
        -------
        Optional[str]
            The absolute path to :attr:`file_path`, expanded with
            ``Path.expanduser()``, converted to a string, and safely quoted
            using :func:`shlex.quote`. Returns ``None`` if no file is
            associated with this instance.
    def quoted_absolute_path(self) -> Optional[str]:
        """
        Return the shell-quoted absolute path to the IP list file, or None if no file is associated.

        The returned string is safe to embed in shell commands because it is quoted using shlex.quote.
        """
        return quote(str(self.path.expanduser().absolute())) if self.path else None

    @property
    def quoted_abs(self) -> Optional[str]:
        """
        Backwards-compatible alias for quoted_absolute_path.

        Prefer using quoted_absolute_path for clarity.
        """
        return self.quoted_absolute_path
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
    logging.info(f"IP Addresses: {','.join(ip_list.ips)}")

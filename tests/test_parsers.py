import unittest

from intelligence.parsers import parse_nmap_like_output


class ParserTests(unittest.TestCase):
    def test_nmap_like_ports_are_extracted(self) -> None:
        ports = parse_nmap_like_output("22/tcp open ssh OpenSSH\n443/tcp open https nginx")
        self.assertEqual([(port.port, port.service) for port in ports], [(22, "ssh"), (443, "https")])
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import struct
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).parents[1]
README = ROOT / "README.md"
HERO = ROOT / "showcase/assets/codex-x-hermes.png"
ROUTE = ROOT / "showcase/assets/route.svg"


class DocumentationTests(unittest.TestCase):
    def test_canonical_hero_is_unchanged_and_accessible(self):
        data = HERO.read_bytes()
        self.assertEqual(
            hashlib.sha256(data).hexdigest(),
            "f80ec9b83fdca0177618fdf607eb12d9d576db91c1f6831f4926d633daf0179d",
        )
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", data[16:24]), (2048, 682))

        readme = README.read_text()
        self.assertIn('src="./showcase/assets/codex-x-hermes.png"', readme)
        self.assertIn('alt="Codex x Hermes"', readme)

    def test_route_svg_is_self_contained_and_accessible(self):
        source = ROUTE.read_text()
        root = ET.fromstring(source)
        namespace = "{http://www.w3.org/2000/svg}"

        self.assertTrue(root.findtext(f"{namespace}title"))
        self.assertTrue(root.findtext(f"{namespace}desc"))
        self.assertNotIn("linearGradient", source)
        self.assertNotIn("radialGradient", source)
        self.assertNotIn("base64", source)
        self.assertNotIn("@import", source)
        self.assertNotRegex(source, r"(?:href|src)=[\"'](?:https?:|//)")

    def test_readme_local_links_resolve(self):
        source = README.read_text()
        targets = re.findall(r"!?\[[^]]*\]\(([^)]+)\)", source)
        targets += re.findall(r"\bsrc=[\"']([^\"']+)[\"']", source)

        for target in targets:
            with self.subTest(target=target):
                if target.startswith(("http://", "https://", "#")):
                    continue
                path = target.split("#", 1)[0]
                self.assertTrue((ROOT / path).exists(), target)


if __name__ == "__main__":
    unittest.main()

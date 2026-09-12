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
LOCAL_WORKER_SKILL = ROOT / "skills/local-worker/SKILL.md"
IRIS_SKILL = ROOT / "skills/iris-camera/SKILL.md"


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

    def test_worker_skill_routes_tiers_without_private_model_ids(self):
        source = LOCAL_WORKER_SKILL.read_text()

        self.assertIn("Would the stronger worker materially improve", source)
        self.assertIn("--tier fast", source)
        self.assertIn("--tier strong", source)
        self.assertIn("final architecture", source)
        self.assertIn("$iris-camera", source)
        self.assertIn("Iris is optional", source)
        self.assertNotRegex(source.lower(), r"gpt-\d+(?:\.\d+)?-[a-z][a-z0-9-]*")
        self.assertNotRegex(source.lower(), r"qwen\d")

    def test_iris_skill_and_installer_stay_optional(self):
        self.assertTrue(IRIS_SKILL.is_file())
        self.assertTrue((IRIS_SKILL.parent / "agents/openai.yaml").is_file())
        self.assertEqual(IRIS_SKILL.parent.name, "iris-camera")

        install = (ROOT / "install.sh").read_text()
        uninstall = (ROOT / "uninstall.sh").read_text()
        self.assertIn('skills/iris-camera', install)
        self.assertNotRegex(install, r"\b(?:curl|cargo)\b")
        self.assertNotIn("codex mcp", install)
        self.assertNotIn("codex mcp remove", uninstall)
        self.assertNotIn(".local/bin/iris", uninstall)


if __name__ == "__main__":
    unittest.main()

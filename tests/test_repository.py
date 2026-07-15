import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "documentation-governance"


def read_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise AssertionError(f"Missing frontmatter: {path}")

    values = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if not separator:
            raise AssertionError(f"Invalid frontmatter line in {path}: {line}")
        values[key.strip()] = value.strip().strip('"')
    return values, text


def public_text_files():
    roots = [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "docs", ROOT / "skills", ROOT / "tests"]
    for root in roots:
        if root.is_file():
            yield root
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".json", ".py", ".yaml", ".yml"}:
                yield path


class RepositoryTests(unittest.TestCase):
    def test_apache_license_configuration(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Apache License\n                           Version 2.0, January 2004", license_text)
        self.assertIn("3. Grant of Patent License.", license_text)
        self.assertIn("END OF TERMS AND CONDITIONS", license_text)
        self.assertIn("APPENDIX: How to apply the Apache License to your work.", license_text)

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("[Apache License, Version 2.0](LICENSE)", readme)

    def test_skill_frontmatter_and_directory_name(self):
        metadata, _ = read_frontmatter(SKILL / "SKILL.md")
        self.assertEqual({"name", "description"}, set(metadata))
        self.assertEqual(SKILL.name, metadata["name"])
        self.assertGreater(len(metadata["description"]), 80)
        for trigger in ("READMEs", "PRDs", "ADRs", "runbooks", "migration"):
            self.assertIn(trigger, metadata["description"])

    def test_openai_metadata_matches_skill(self):
        metadata, _ = read_frontmatter(SKILL / "SKILL.md")
        text = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Documentation Governance"', text)
        match = re.search(r'short_description: "([^"]+)"', text)
        self.assertIsNotNone(match)
        self.assertTrue(25 <= len(match.group(1)) <= 64)
        self.assertIn("current-state", match.group(1))
        self.assertIn(f"${metadata['name']}", text)

    def test_references_are_direct_and_exist(self):
        _, text = read_frontmatter(SKILL / "SKILL.md")
        references = re.findall(r"\]\((references/[^)]+)\)", text)
        self.assertGreaterEqual(len(references), 5)
        self.assertEqual(len(references), len(set(references)))
        for reference in references:
            self.assertTrue((SKILL / reference).is_file(), reference)

    def test_skill_has_no_extraneous_or_product_manifest_files(self):
        forbidden_names = {"readme.md", "changelog.md", "installation_guide.md"}
        for path in SKILL.rglob("*"):
            self.assertNotIn(path.name.lower(), forbidden_names)
        self.assertFalse((SKILL / "scripts").exists())
        self.assertFalse((ROOT / ".codex-plugin").exists())

    def test_markdown_local_links_resolve(self):
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for path in public_text_files():
            if path.suffix.lower() != ".md":
                continue
            for target in link_pattern.findall(path.read_text(encoding="utf-8")):
                if target.startswith(("https://", "http://", "#", "mailto:")):
                    continue
                local_target = target.split("#", 1)[0]
                self.assertTrue((path.parent / local_target).resolve().exists(), f"{path}: {target}")

    def test_public_text_has_no_machine_paths_or_private_urls(self):
        user_home_prefixes = (
            "/" + "Users" + "/",
            "/" + "home" + "/",
            "C:" + "\\" + "Users" + "\\",
        )
        private_url = re.compile(r"https?://[^\s)]+(?:\.internal|\.corp)(?:[/:]|$)", re.IGNORECASE)
        for path in public_text_files():
            text = path.read_text(encoding="utf-8")
            for prefix in user_home_prefixes:
                self.assertNotIn(prefix, text, str(path))
            self.assertIsNone(private_url.search(text), str(path))

    def test_acceptance_fixtures_cover_document_semantics(self):
        manifest_path = ROOT / "tests" / "fixtures" / "document-review" / "cases.json"
        cases = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = {
            "current-readme-retired-option": ("current-state", "revise-and-relocate-history"),
            "adr-superseded-option": ("historical-decision", "allow"),
            "current-readme-current-architecture": ("current-state", "allow"),
            "current-security-prohibition": ("current-state", "allow"),
            "migration-old-version-context": ("migration-history", "allow"),
        }
        self.assertEqual(set(expected), {case["id"] for case in cases})
        for case in cases:
            self.assertEqual(expected[case["id"]], (case["document_class"], case["expected_action"]))
            document = manifest_path.parent / case["document"]
            self.assertTrue(document.is_file(), document)
            self.assertGreater(len(document.read_text(encoding="utf-8").strip()), 40)


if __name__ == "__main__":
    unittest.main()

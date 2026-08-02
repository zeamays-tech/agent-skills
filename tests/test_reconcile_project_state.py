import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "reconcile-project-state"
COLLECTOR = SKILL / "scripts" / "collect_project_state.py"
VALIDATOR = SKILL / "scripts" / "validate_reconciliation.py"
FIXTURES = ROOT / "tests" / "fixtures" / "reconcile-project-state"


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


def run_json(*arguments, input_text=None):
    result = subprocess.run(
        [sys.executable, *map(str, arguments)],
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result, json.loads(result.stdout)


def git(repo: Path, *arguments: str):
    return subprocess.run(
        ["git", "-C", str(repo), *arguments],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def initialize_repository(path: Path):
    path.mkdir(parents=True)
    subprocess.run(
        ["git", "init", "--quiet", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    git(path, "config", "user.name", "Fixture User")
    git(path, "config", "user.email", "fixture@example.invalid")
    (path / "AGENTS.md").write_text("# Fixture rules\n", encoding="utf-8")
    (path / "contract.txt").write_text("accepted\n", encoding="utf-8")
    git(path, "add", "AGENTS.md", "contract.txt")
    git(path, "commit", "--quiet", "-m", "fixture baseline")


class ReconcileProjectStateTests(unittest.TestCase):
    def test_skill_metadata_and_direct_references(self):
        metadata, text = read_frontmatter(SKILL / "SKILL.md")
        self.assertEqual({"name", "description"}, set(metadata))
        self.assertEqual(SKILL.name, metadata["name"])
        for trigger in ("requirements", "schemas", "gate", "post-deployment", "repositories"):
            self.assertIn(trigger, metadata["description"])
        for exclusion in ("spelling or format-only", "behavior-preserving", "unaccepted drafts"):
            self.assertIn(exclusion, metadata["description"])
        for mode in ("`impact`", "`audit`", "`reconcile`", "`gate`", "`post-deploy`"):
            self.assertIn(mode, text)
        self.assertIn("explicit `$reconcile-project-state` invocation with no arguments", text)

        references = re.findall(r"\]\((references/[^)]+)\)", text)
        self.assertEqual(5, len(references))
        self.assertEqual(len(references), len(set(references)))
        for reference in references:
            self.assertTrue((SKILL / reference).is_file(), reference)

    def test_openai_metadata_and_readme_listing(self):
        metadata, _ = read_frontmatter(SKILL / "SKILL.md")
        interface = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Reconcile Project State"', interface)
        match = re.search(r'short_description: "([^"]+)"', interface)
        self.assertIsNotNone(match)
        self.assertTrue(25 <= len(match.group(1)) <= 64)
        self.assertIn(f"${metadata['name']}", interface)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("skills/reconcile-project-state/SKILL.md", readme)

    def test_skill_structure_stays_portable(self):
        forbidden_names = {"readme.md", "changelog.md", "installation_guide.md"}
        for path in SKILL.rglob("*"):
            self.assertNotIn(path.name.lower(), forbidden_names)
        self.assertFalse((SKILL / ".codex-plugin").exists())
        self.assertTrue(COLLECTOR.is_file())
        self.assertTrue(VALIDATOR.is_file())

    def test_single_repository_inventory_uses_real_git_state(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "project"
            initialize_repository(repo)
            (repo / "contract.txt").write_text("changed\n", encoding="utf-8")
            (repo / "untracked.txt").write_text("new\n", encoding="utf-8")

            result, output = run_json(COLLECTOR, "--root", repo)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(output["read_only"])
        self.assertEqual(1, len(output["repositories"]))
        record = output["repositories"][0]
        self.assertEqual(".", record["path"])
        self.assertEqual(["AGENTS.md"], record["governance_files"])
        self.assertFalse(record["working_tree_clean"])
        self.assertEqual(
            {"contract.txt", "untracked.txt"},
            {entry["path"] for entry in record["working_tree"]},
        )

    def test_known_base_ref_collects_committed_change_range(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "project"
            initialize_repository(repo)
            base = git(repo, "rev-parse", "HEAD").stdout.decode().strip()
            (repo / "contract.txt").write_text("changed\n", encoding="utf-8")
            git(repo, "add", "contract.txt")
            git(repo, "commit", "--quiet", "-m", "change contract")

            result, output = run_json(
                COLLECTOR, "--root", repo, "--base-ref", base
            )

        self.assertEqual(0, result.returncode, result.stderr)
        record = output["repositories"][0]
        self.assertEqual(base, record["base_ref"])
        self.assertEqual(["contract.txt"], record["base_changed_paths"])
        self.assertEqual([], record["errors"])

    def test_multi_repository_inventory_requires_opt_in_discovery(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            workspace.mkdir()
            initialize_repository(workspace / "service-a")
            initialize_repository(workspace / "service-b")

            default_result, default_output = run_json(COLLECTOR, "--root", workspace)
            nested_result, nested_output = run_json(
                COLLECTOR,
                "--root",
                workspace,
                "--discover-nested",
                "--max-depth",
                "2",
            )

        self.assertEqual(0, default_result.returncode, default_result.stderr)
        self.assertEqual([], default_output["repositories"])
        self.assertEqual(0, nested_result.returncode, nested_result.stderr)
        self.assertEqual(
            ["service-a", "service-b"],
            [record["path"] for record in nested_output["repositories"]],
        )

    def test_source_conflict_fails_gate_without_silent_resolution(self):
        fixture = json.loads((FIXTURES / "source-conflict.json").read_text(encoding="utf-8"))
        result, output = run_json(VALIDATOR, FIXTURES / "source-conflict.json")
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertTrue(output["valid"])
        self.assertEqual("fail", output["gate"]["computed"])
        self.assertEqual(["contract-conflict"], output["unresolved_conflicts"])

        fixture["mismatches"][0]["gate_blocking"] = False
        non_blocking_claim, non_blocking_output = run_json(
            VALIDATOR, "-", input_text=json.dumps(fixture)
        )
        self.assertEqual(1, non_blocking_claim.returncode, non_blocking_claim.stderr)
        self.assertTrue(non_blocking_output["valid"])
        self.assertEqual("fail", non_blocking_output["gate"]["computed"])

    def test_unavailable_required_test_blocks_gate_and_cannot_be_claimed_passed(self):
        fixture = json.loads((FIXTURES / "test-unavailable.json").read_text(encoding="utf-8"))
        result, output = run_json(VALIDATOR, FIXTURES / "test-unavailable.json")
        self.assertEqual(1, result.returncode, result.stderr)
        self.assertTrue(output["valid"])
        self.assertEqual("blocked", output["gate"]["computed"])
        self.assertEqual(["acceptance-check"], output["unverified_items"])

        fixture["gate"]["decision"] = "pass"
        false_pass, false_output = run_json(
            VALIDATOR, "-", input_text=json.dumps(fixture)
        )
        self.assertEqual(2, false_pass.returncode, false_pass.stderr)
        self.assertFalse(false_output["valid"])
        self.assertTrue(
            any("does not match evidence-derived blocked" in error for error in false_output["errors"])
        )

    def test_applied_fix_outside_explicit_write_boundary_is_invalid(self):
        result, output = run_json(VALIDATOR, FIXTURES / "unauthorized-reconcile.json")
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertFalse(output["valid"])
        self.assertIsNone(output["gate"]["satisfied"])
        self.assertTrue(
            any("outside authorized write paths" in error for error in output["errors"])
        )

    def test_evidenced_gate_passes(self):
        result, output = run_json(VALIDATOR, FIXTURES / "passing-gate.json")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(output["valid"])
        self.assertEqual("pass", output["gate"]["computed"])


if __name__ == "__main__":
    unittest.main()

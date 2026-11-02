import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "documentation-governance"
RELEASE_SCRIPT = ROOT / "scripts" / "release.sh"


def read_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise AssertionError(f"Missing frontmatter: {path}")

    values = {}
    for line in match.group(1).splitlines():
        if line.startswith(" "):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise AssertionError(f"Invalid frontmatter line in {path}: {line}")
        values[key.strip()] = value.strip().strip('"')
    return values, text


def public_text_files():
    roots = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "docs",
        ROOT / "scripts",
        ROOT / "skills",
        ROOT / "tests",
    ]
    for root in roots:
        if root.is_file():
            yield root
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {
                ".md",
                ".json",
                ".py",
                ".sh",
                ".yaml",
                ".yml",
            }:
                yield path


class RepositoryTests(unittest.TestCase):
    def test_agents_requires_full_worktree_commit_recommendation(self):
        guidance = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for requirement in (
            "staged changes, unstaged changes, and untracked files",
            "exactly one commit message",
            "Conventional Commits 1.0.0",
            "all uncommitted repository changes",
        ):
            self.assertIn(requirement, guidance)

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
        self.assertEqual({"name", "description", "metadata"}, set(metadata))
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

    def test_installed_skills_carry_consumer_integration_guidance(self):
        for skill in sorted((ROOT / "skills").iterdir()):
            if not skill.is_dir():
                continue
            skill_name = skill.name
            skill_text = (skill / "SKILL.md").read_text(encoding="utf-8")
            reference = "references/consumer-integration.md"
            integration = (
                (skill / reference).read_text(encoding="utf-8")
                if reference in skill_text else skill_text
            )
            self.assertIn(f"${skill_name}", integration)
            self.assertIn("AGENTS.md", integration)

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for skill_name in ("documentation-governance", "reconcile-project-state"):
            self.assertIn(
                f"skills/{skill_name}/references/consumer-integration.md", readme
            )
        self.assertIn("installed-Skill invocation", agents)

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

    def test_release_script_is_executable_and_has_valid_shell_syntax(self):
        self.assertTrue(RELEASE_SCRIPT.is_file())
        self.assertNotEqual(0, RELEASE_SCRIPT.stat().st_mode & 0o111)
        result = subprocess.run(
            ["bash", "-n", str(RELEASE_SCRIPT)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_release_script_validates_semver_tags(self):
        script = shlex.quote(str(RELEASE_SCRIPT))
        valid_tags = ("v0.1.0", "v1.2.3", "v2.0.0-rc.1", "v3.4.5+build.7")
        invalid_tags = (
            "1.2.3",
            "v01.2.3",
            "v1.02.3",
            "v1.2",
            "v1.2.3-01",
            "latest",
        )

        for tag in valid_tags:
            result = subprocess.run(
                ["bash", "-c", f"source {script}; validate_release_tag {shlex.quote(tag)}"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, (tag, result.stderr))

        for tag in invalid_tags:
            result = subprocess.run(
                ["bash", "-c", f"source {script}; validate_release_tag {shlex.quote(tag)}"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, result.returncode, tag)

    def test_release_reads_and_updates_selected_skill_version(self):
        script = shlex.quote(str(RELEASE_SCRIPT))
        for version in ('1.2.3', '2.0.0-rc.1+build.7', 'v1.2.3', '01.2.3', '1.2.3 ', '1.2.3\n2.0.0', ''):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'SKILL.md'
                original = ('---\nname: sample\ndescription: Sample\nmetadata:\n'
                            f'  version: "{version}"\n  author: Example\n---\nBody\n')
                path.write_text(original)
                command = f'source {script}; SKILL_FILE=SKILL.md; read_release_tag'
                result = subprocess.run(['bash', '-c', command], cwd=directory,
                                        capture_output=True, text=True)
                if version in ('1.2.3', '2.0.0-rc.1+build.7'):
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertEqual('v' + version, result.stdout.strip())
                    result = subprocess.run(
                        ['bash', '-c', f'source {script}; SKILL_FILE=SKILL.md; write_release_version v3.0.0'],
                        cwd=directory, capture_output=True, text=True)
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertEqual(original.replace(f'"{version}"', '"3.0.0"'), path.read_text())
                else:
                    self.assertNotEqual(0, result.returncode)
                    self.assertEqual(original, path.read_text())

        for path in (ROOT / 'skills').glob('*/SKILL.md'):
            result = subprocess.run(
                ['bash', '-c', f'source {script}; SKILL_FILE={shlex.quote(str(path))}; read_release_tag'],
                capture_output=True, text=True)
            self.assertEqual(0, result.returncode, (path.name, result.stderr))

    def test_version_update_rejects_ambiguous_metadata_without_changing_file(self):
        helper = ROOT / 'scripts' / 'skill_version.py'
        headers = (
            'metadata:\n  version: "1.0.0"\nmetadata: {version: "2.0.0"}\n',
            'metadata:\n  version: "1.0.0"\n  version: "2.0.0"\n',
            'metadata:\n  author: Example\n',
            'version: "1.0.0"\n',
        )
        for header in headers:
            with self.subTest(header=header), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'SKILL.md'
                original = '---\nname: sample\n' + header + '---\nBody\n'
                path.write_text(original)
                result = subprocess.run(['python3', str(helper), str(path), '1.0.1'],
                                        capture_output=True, text=True)
                self.assertNotEqual(0, result.returncode, result.stdout)
                self.assertEqual(original, path.read_text())

    def test_release_upgrade_choices_and_semver_precedence(self):
        script = shlex.quote(str(RELEASE_SCRIPT))
        cases = [
            ('next_release_tag v1.2.9 major', 0, 'v2.0.0'),
            ('next_release_tag v1.2.9 minor', 0, 'v1.3.0'),
            ('next_release_tag v1.2.9 patch', 0, 'v1.2.10'),
            ('next_release_tag v1.2.9-rc.1+build.7 patch', 0, 'v1.2.10'),
            ('next_release_tag v1.2.9 v2.0.0', 1, ''),
            ('release_not_older v1.2.10 v1.2.9', 0, ''),
            ('release_not_older v1.2.9 v1.2.10', 1, ''),
            ('release_not_older v1.2.3 v1.3.0', 1, ''),
            ('release_not_older v1.9.9 v2.0.0', 1, ''),
            ('release_not_older v1.0.0-rc.1 v1.0.0', 1, ''),
            ('release_not_older v1.0.0 v1.0.0-rc.1', 0, ''),
            ('release_not_older v1.0.0-beta.11 v1.0.0-beta.2', 0, ''),
            ('release_not_older v1.0.0-alpha v1.0.0-alpha.1', 1, ''),
            ('release_not_older v1.0.0-1 v1.0.0-alpha', 1, ''),
            ('release_not_older v1.0.0+one v1.0.0+two', 0, ''),
        ]
        for command, code, output in cases:
            with self.subTest(command=command):
                result = subprocess.run(
                    ['bash', '-c', f'source {script}; {command}'],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(code, result.returncode, result.stderr)
                self.assertEqual(output, result.stdout.strip())

    def test_release_interaction_dry_run_and_failed_publication_retry(self):
        # Real local Git; external validation and remote calls are isolated stubs.
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            repository = base / 'repository'
            repository.mkdir()
            binary = base / 'bin'
            binary.mkdir()
            log = base / 'calls'
            real_git = shutil.which('git')
            environment = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull,
                               GIT_CONFIG_SYSTEM=os.devnull, CALL_LOG=str(log),
                               PYTHONDONTWRITEBYTECODE='1')

            def git(*args):
                return subprocess.check_output(
                    [real_git, *args], cwd=repository, env=environment, text=True,
                    stderr=subprocess.DEVNULL,
                ).strip()

            git('init')
            git('checkout', '-b', 'main')
            git('config', 'user.name', 'Fixture Maintainer')
            git('config', 'user.email', 'fixture@example.com')
            skill_file = repository / 'skills' / 'sample' / 'SKILL.md'
            skill_file.parent.mkdir(parents=True)
            original_skill = '---\nname: sample\ndescription: Example skill\nmetadata:\n  version: "1.2.3"\n---\nBody\n'
            skill_file.write_text(original_skill)
            other = repository / 'skills' / 'other' / 'SKILL.md'
            other.parent.mkdir()
            other.write_text(original_skill.replace('sample', 'other'))
            (skill_file.parent / 'references').mkdir()
            (skill_file.parent / 'references' / 'guide.md').write_text('Example reference\n')
            git('add', 'skills')
            git('commit', '-m', 'Initial release')
            git('tag', 'sample-v1.2.3')
            git('tag', 'other-v99.0.0')
            git('tag', 'v99.0.0')
            (repository / 'tests').mkdir()
            (repository / 'tests' / 'test_version.py').write_text(
                'import unittest\nfrom pathlib import Path\n'
                'class VersionTest(unittest.TestCase):\n'
                '    def test_version(self):\n'
                '        self.assertTrue(Path("skills/sample/SKILL.md").is_file())\n'
            )
            (repository / 'change.txt').write_text('Ready for release\n')
            git('add', 'change.txt', 'tests')
            git('commit', '-m', 'Prepare release')
            git('remote', 'add', 'origin', 'https://github.com/example/skills.git')
            git('update-ref', 'refs/remotes/origin/main', 'HEAD')
            git('symbolic-ref', 'refs/remotes/origin/HEAD', 'refs/remotes/origin/main')
            initial_head = git('rev-parse', 'HEAD')
            commands = {
                'git': '#!/bin/bash\ncase "$1" in\n'
                       'fetch|push) echo "git $*" >> "$CALL_LOG"; '
                       '[[ "$FAIL_STAGE" == "$1" ]] && exit 1; exit 0;;\n'
                       f'esac\nexec {shlex.quote(real_git)} "$@"\n',
                'npx': '#!/bin/bash\nexit 0\n',
                'gh': '#!/bin/bash\necho "gh $*" >> "$CALL_LOG"\n'
                      'case "$*" in\n'
                      '"auth status "*) [[ "$FAIL_STAGE" == auth ]] && exit 1; exit 0;;\n'
                      '"repo view "*) echo main;;\n'
                      '*"--json url"*) echo https://example.com/release;;\n'
                      '"release create "*) cp "$4" "$CALL_LOG.zip"; [[ "$FAIL_STAGE" == release ]] && exit 1; exit 0;;\n'
                      '"release view "*) [[ "$FAIL_STAGE" == exists ]] && exit 0; exit 1;;\n'
                      '*) exit 1;;\nesac\n',
            }
            for name, content in commands.items():
                command = binary / name
                command.write_text(content)
                command.chmod(0o755)
            environment['PATH'] = str(binary) + os.pathsep + os.environ['PATH']

            def release(*args, input='', fail=''):
                return subprocess.run(
                    ['bash', str(RELEASE_SCRIPT), '--skill', 'sample', *args], cwd=repository,
                    env=dict(environment, FAIL_STAGE=fail), input=input,
                    capture_output=True, text=True, check=False,
                )

            result = release('v1.2.4')
            self.assertNotEqual(0, result.returncode)
            self.assertIn('custom versions are not accepted', result.stderr)
            self.assertFalse(log.exists())
            result = release(input='1.2.4\n\n \nPatch release\n1\n')
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn('Current version (sample): 1.2.3', result.stderr)
            self.assertIn('1) major -> v2.0.0', result.stderr)
            self.assertIn('2) minor -> v1.3.0', result.stderr)
            self.assertIn('3) patch -> v1.2.4', result.stderr)
            self.assertIn('custom versions are not accepted', result.stderr)
            self.assertIn('Release title must not be blank', result.stderr)
            self.assertIn('1.2.3 -> 1.2.4', result.stdout)
            self.assertEqual(initial_head, git('rev-parse', 'HEAD'))
            self.assertEqual(original_skill, skill_file.read_text())
            self.assertEqual({'sample-v1.2.3', 'other-v99.0.0', 'v99.0.0'}, set(git('tag', '--list').splitlines()))
            self.assertFalse(log.exists(), 'Dry run must not contact Git or GitHub remotes')
            result = subprocess.run(
                ['bash', str(RELEASE_SCRIPT), '--current', '--dry-run', '--title', 'Initial'],
                cwd=repository, env=dict(environment, FAIL_STAGE=''), input='sample\n',
                capture_output=True, text=True)
            self.assertNotEqual(0, result.returncode)
            self.assertIn('Existing tag sample-v1.2.3 does not point to HEAD', result.stderr)
            self.assertIn('Skill name:', result.stderr)
            self.assertEqual(initial_head, git('rev-parse', 'HEAD'))


            git('tag', 'sample-v2.0.0')
            result = release('--dry-run', '--title', 'Patch', 'patch')
            self.assertNotEqual(0, result.returncode)
            self.assertIn('older than existing tag sample-v2.0.0', result.stderr)
            git('tag', '-d', 'sample-v2.0.0')
            divergent = git('commit-tree', 'HEAD^{tree}', '-m', 'Unrelated history')
            git('tag', 'sample-v1.2.2', divergent)
            result = release('--dry-run', '--title', 'Patch', 'patch')
            self.assertNotEqual(0, result.returncode)
            self.assertIn('not an ancestor', result.stderr)
            git('tag', '-d', 'sample-v1.2.2')

            result = release('--publish', '--title', 'Patch', 'patch')
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(initial_head, git('rev-parse', 'HEAD'))
            self.assertEqual(original_skill, skill_file.read_text())

            result = release('--publish', '--yes', '--title', 'Patch', 'patch', fail='auth')
            self.assertNotEqual(0, result.returncode)
            self.assertIn('Local release sample-v1.2.4 (Skill version commit and tag) is retained', result.stderr)
            version_head = git('rev-parse', 'HEAD')
            self.assertNotEqual(initial_head, version_head)
            self.assertEqual(original_skill.replace('1.2.3', '1.2.4'), skill_file.read_text())
            self.assertEqual(original_skill.replace('sample', 'other'), other.read_text())
            self.assertEqual('skills/sample/SKILL.md', git('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'))
            self.assertEqual(version_head, git('rev-list', '-n', '1', 'sample-v1.2.4'))
            self.assertEqual('chore(release): sample-v1.2.4', git('log', '-1', '--format=%s'))
            self.assertEqual('tag', git('cat-file', '-t', 'sample-v1.2.4'))
            for stage in ('fetch', 'push', 'release'):
                with self.subTest(failure_stage=stage):
                    result = release('--retry', '--publish', '--yes', '--title', 'Patch', fail=stage)
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn('Local release sample-v1.2.4 (Skill version commit and tag) is retained', result.stderr)
                    self.assertEqual(version_head, git('rev-parse', 'HEAD'))
                    self.assertEqual(version_head, git('rev-list', '-n', '1', 'sample-v1.2.4'))
                    self.assertEqual(original_skill.replace('1.2.3', '1.2.4'), skill_file.read_text())
                    self.assertEqual(original_skill.replace('sample', 'other'), other.read_text())
            result = release('--retry', '--publish', '--yes', '--title', 'Patch')
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(version_head, git('rev-parse', 'HEAD'))
            self.assertEqual('', git('status', '--porcelain'))
            self.assertIn('Published https://example.com/release', result.stdout)
            with zipfile.ZipFile(str(log) + '.zip') as archive:
                self.assertIn('sample/SKILL.md', archive.namelist())
                self.assertEqual(b'Example reference\n', archive.read('sample/references/guide.md'))
                self.assertTrue(all(name.startswith('sample/') for name in archive.namelist()))
                self.assertEqual(skill_file.read_text(), archive.read('sample/SKILL.md').decode())
            self.assertIn('--latest=false', log.read_text())
            self.assertNotIn('--generate-notes', log.read_text())
            self.assertIn('/tree/sample-v1.2.4/skills/sample', log.read_text())
            result = release('--retry', '--publish', '--yes', '--title', 'Patch', fail='exists')
            self.assertNotEqual(0, result.returncode)
            self.assertIn('already exists', result.stderr)
            self.assertEqual(version_head, git('rev-parse', 'HEAD'))

            # A different Skill can publish its current version at the same commit.
            git('tag', '-d', 'other-v99.0.0')
            result = release('--skill', 'other', '--current', '--publish', '--yes', '--title', 'Other')
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(version_head, git('rev-parse', 'HEAD'))
            self.assertEqual(version_head, git('rev-list', '-n', '1', 'other-v1.2.3'))
            with zipfile.ZipFile(str(log) + '.zip') as archive:
                self.assertEqual(other.read_text(), archive.read('other/SKILL.md').decode())
                self.assertTrue(all(name.startswith('other/') for name in archive.namelist()))
            self.assertNotIn('--prerelease', log.read_text())
            for skill in ('../sample', 'missing', '-sample'):
                result = release('--skill', skill, '--current', '--dry-run', '--title', 'Invalid')
                self.assertNotEqual(0, result.returncode)
                self.assertEqual(version_head, git('rev-parse', 'HEAD'))


    def test_release_script_uses_guarded_github_release_flow(self):
        text = RELEASE_SCRIPT.read_text(encoding="utf-8")
        for required in (
            "git tag -a",
            "git push",
            "gh release create",
            "--notes",
            "--verify-tag",
            "Interactive release setup",
            "Release title",
            "Release mode",
        ):
            self.assertIn(required, text)

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("--skill documentation-governance", readme)
        self.assertNotIn("Use $documentation-governance", readme)
        self.assertIn('skill_name="replace-with-skill-name"', readme)
        for documented_behavior in (
            "Bash",
            "`basename`, `mktemp`, and `rm`",
            "`NPM_CONFIG_CACHE` or `npm_config_cache`",
            "otherwise, it creates an isolated temporary npm cache",
        ):
            self.assertIn(documented_behavior, readme)


if __name__ == "__main__":
    unittest.main()

"""Structural checks for the plugin's skills. Run: python3 -m unittest discover tests"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"


def frontmatter(path):
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    fm = m.group(1)
    name = re.search(r"^name:\s*(\S+)", fm, re.M)
    desc = re.search(r"^description:\s*>?\s*\n?(.*)", fm, re.S | re.M)
    return {
        "name": name.group(1) if name else None,
        "description": " ".join(desc.group(1).split()) if desc else "",
    }, text


def skill_dirs():
    return sorted(p for p in SKILLS.iterdir() if (p / "SKILL.md").is_file())


class SkillStructure(unittest.TestCase):
    def test_every_skill_has_valid_frontmatter(self):
        for d in skill_dirs():
            with self.subTest(skill=d.name):
                fm, _ = frontmatter(d / "SKILL.md")
                self.assertIsNotNone(fm, "missing frontmatter")
                self.assertEqual(fm["name"], d.name)
                self.assertTrue(fm["description"])
                self.assertLessEqual(len(fm["description"]), 1024)

    def test_every_skill_has_codex_config_and_command(self):
        for d in skill_dirs():
            with self.subTest(skill=d.name):
                self.assertTrue((d / "agents" / "openai.yaml").is_file())
                cmd = ROOT / ".claude" / "commands" / f"{d.name}.md"
                self.assertTrue(cmd.exists(), f"missing {cmd}")
                self.assertEqual(cmd.resolve(), (d / "SKILL.md").resolve())

    def test_skills_listed_in_readmes_and_llms(self):
        readme = (ROOT / "README.md").read_text()
        skills_readme = (SKILLS / "README.md").read_text()
        llms = (ROOT / "llms.txt").read_text()
        for d in skill_dirs():
            with self.subTest(skill=d.name):
                self.assertIn(f"skills/{d.name}/SKILL.md", readme)
                self.assertIn(f"{d.name}/SKILL.md", skills_readme)
                self.assertIn(f"skills/{d.name}/SKILL.md", llms)

    def test_eval_guide_routes_to_every_skill(self):
        guide = (SKILLS / "eval-guide" / "SKILL.md").read_text()
        for d in skill_dirs():
            if d.name == "eval-guide":
                continue
            with self.subTest(skill=d.name):
                self.assertIn(f"`{d.name}`", guide)

    def test_manifest_versions_match(self):
        claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        self.assertEqual(claude["version"], codex["version"])


class EvalCoach(unittest.TestCase):
    DIR = SKILLS / "eval-coach"

    def test_referenced_paths_exist(self):
        text = (self.DIR / "SKILL.md").read_text()
        for ref in set(re.findall(r"`((?:references|assets)/[^`\s]+\.(?:md|html))`", text)):
            with self.subTest(ref=ref):
                self.assertTrue((self.DIR / ref).is_file(), ref)

    def test_every_reference_file_is_indexed(self):
        text = (self.DIR / "SKILL.md").read_text()
        for f in sorted((self.DIR / "references").rglob("*.md")):
            rel = f.relative_to(self.DIR).as_posix()
            with self.subTest(file=rel):
                self.assertTrue(f"`{rel}`" in text, f"{rel} is not in the SKILL.md index")

    def test_references_have_no_private_links_or_drafts(self):
        bad = re.compile(r"docs\.google\.com|drive\.google\.com|slack\.com/archives|WORK IN PROGRESS|\{\{")
        for f in sorted((self.DIR / "references").rglob("*.md")):
            with self.subTest(file=f.name):
                hits = [l for l in f.read_text().splitlines() if bad.search(l)]
                self.assertEqual(hits, [])

    def test_lessons_reference_existing_repo_files(self):
        text = (self.DIR / "references" / "lessons.md").read_text()
        for ref in set(re.findall(r"`((?:templates|docs)/[^`\s]+)`", text)):
            with self.subTest(ref=ref):
                self.assertTrue((ROOT / ref).exists(), ref)
        for skill in set(re.findall(r"`([a-z]+(?:-[a-z]+)*)` on", text)):
            with self.subTest(skill=skill):
                self.assertTrue((SKILLS / skill / "SKILL.md").is_file(), skill)

    def test_diagram_template_is_self_contained(self):
        html = (self.DIR / "assets" / "diagram-template.html").read_text()
        self.assertIn("<svg", html)
        self.assertNotRegex(html, r"<script|<img")


if __name__ == "__main__":
    unittest.main()

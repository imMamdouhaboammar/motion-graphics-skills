"""Keep imported skills, nested modules, package metadata and docs aligned."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PluginCatalogTests(unittest.TestCase):
    def test_catalog_contains_every_imported_skill_and_named_module(self):
        skills = set(ROOT.glob('skills/*/SKILL.md'))
        modules = {p for p in ROOT.glob('skills/video-style-cloner/skills/*/*.md')
                   if p.stem == p.parent.name}
        catalog = (ROOT / 'docs/plugin/CATALOG.md').read_text()
        links = set(re.findall(r'\]\(../../([^)]*)\)', catalog))
        self.assertEqual(links, {p.relative_to(ROOT).as_posix() for p in skills | modules})
        self.assertIn(f'**{len(skills)} top-level skills**', catalog)
        self.assertIn(f'**{len(modules)} named workflow modules**', catalog)
        for path in links:
            self.assertTrue((ROOT / path).is_file(), path)

    def test_manifest_identity_and_presentation_match(self):
        portable = json.loads((ROOT / 'plugin.json').read_text())
        codex = json.loads((ROOT / '.codex-plugin/plugin.json').read_text())
        for field in ('name', 'version', 'description', 'author'):
            self.assertEqual(portable[field], codex[field], field)
        self.assertEqual(portable['extensions']['com.openai']['interface'], codex['interface'])
        self.assertEqual(portable['version'], json.loads((ROOT / 'marketplace.json').read_text())['version'])
        self.assertEqual(portable['version'], json.loads((ROOT / 'package.json').read_text())['version'])
        self.assertLessEqual(len(codex['interface']['shortDescription']), 30)

    def test_readme_and_package_docs_use_actual_skill_count(self):
        count = len(list(ROOT.glob('skills/*/SKILL.md')))
        self.assertIn(f'{count} agent skills', (ROOT / 'README.md').read_text())
        self.assertIn(f'{count} top-level skills', (ROOT / 'docs/plugin/README.md').read_text())


if __name__ == '__main__':
    unittest.main()

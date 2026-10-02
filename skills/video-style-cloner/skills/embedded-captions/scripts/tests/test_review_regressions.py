"""Public CLI regressions for captions and sibling project scaffolders."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
SKILLS = SCRIPTS.parents[1]
NODE = shutil.which('node')

class ReviewRegressions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def fill(self, words, transcript):
        (self.root / 'plan.json').write_text(json.dumps({'groups': [{'words': words}]}))
        (self.root / 'transcript.json').write_text(json.dumps({'words': transcript}))
        subprocess.run([NODE, str(SCRIPTS / 'fill-timings.cjs'), str(self.root)], check=True, capture_output=True)
        return json.loads((self.root / 'plan.json').read_text())['groups'][0]['words']

    def test_unicode_words_receive_transcript_times(self):
        words = [{'text': '日本語'}, {'text': 'العربية'}, {'text': 'cafe\u0301'}]
        tr = [{'text': '日本語。', 'start': 1, 'end': 2}, {'text': 'العربية!', 'start': 2, 'end': 3}, {'text': 'CAFÉ', 'start': 3, 'end': 4}]
        got = self.fill(words, tr)
        self.assertEqual([w.get('start') for w in got], [1, 2, 3])
        self.assertEqual([w.get('end') for w in got], [2, 3, 4])

    def test_alignment_miss_does_not_overwrite_later_repeated_word(self):
        for miss in ['typo', '!!!']:
            with self.subTest(miss=miss):
                got = self.fill([{'text': miss}, {'text': 'and', 'start': 9, 'end': 10}],
                                [{'text': 'and', 'start': 1, 'end': 2}, {'text': 'and', 'start': 9, 'end': 10}])
                self.assertEqual((got[1]['start'], got[1]['end']), (9, 10))

    def test_dropped_fillers_and_repeated_words_still_align(self):
        got = self.fill([{'text': 'and'}, {'text': 'then'}, {'text': 'and'}],
                        [{'text': 'um', 'start': 0, 'end': .2}, {'text': 'and', 'start': 1, 'end': 2}, {'text': 'then', 'start': 3, 'end': 4}, {'text': 'and', 'start': 5, 'end': 6}])
        self.assertEqual([w['start'] for w in got], [1, 3, 5])

    def test_escaped_svg_glyphs_have_paths(self):
        font = self.root / 'font.svg'
        font.write_text('<svg xmlns="http://www.w3.org/2000/svg"><defs><font>'
                        '<glyph unicode="&apos;" horiz-adv-x="10" d="M 0 0 L 1 1"/>'
                        '<glyph unicode="&amp;" horiz-adv-x="10" d="M 0 0 L 1 1"/>'
                        '<glyph unicode="&#233;" horiz-adv-x="10" d="M 0 0 L 1 1"/>'
                        '</font></defs></svg>')
        r = subprocess.run(['python3', str(SCRIPTS / 'gen-stroke-path.py'), str(font), "'&é", '30', '0', '0'], check=True, capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), 'M 0.0 0.0 L 1.0 -1.0 M 10.0 0.0 L 11.0 -1.0 M 20.0 0.0 L 21.0 -1.0')

    def fake_bin(self):
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        for name in ['bash', 'dirname', 'mkdir', 'cp', 'sed', 'rm', 'tail']:
            (bin_dir / name).symlink_to(shutil.which(name))
        npm = bin_dir / 'npm'
        npm.write_text('#!/bin/bash\nmkdir -p node_modules/p5.brush/dist\n: > node_modules/p5.brush/dist/p5.brush.crayon.js\n')
        npm.chmod(0o755)
        (bin_dir / 'node').symlink_to(NODE)
        return bin_dir

    def test_no_rsync_scaffold_uses_relative_target_and_preserves_output(self):
        bin_dir = self.fake_bin()
        for skill in ['anime-cel', 'crayon-storybook']:
            with self.subTest(skill=skill):
                target = self.root / skill
                (target / 'out').mkdir(parents=True)
                (target / 'out' / 'existing.mp4').write_text('precious render')
                r = subprocess.run(['/bin/bash', str(SKILLS / skill / 'scripts/new_project.sh'), skill], cwd=self.root, env={**os.environ, 'PATH': str(bin_dir)}, capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertTrue((target / 'studio.html').exists())
                self.assertTrue((target / 'out' / 'existing.mp4').exists(), 'existing render was deleted')
                self.assertEqual((target / 'out' / 'existing.mp4').read_text(), 'precious render')

    def test_resolver_preserves_explicit_source(self):
        (self.root / 'source.mp4').write_bytes(b'explicit source')
        (self.root / 'larger.mov').write_bytes(b'x' * 100)
        r = subprocess.run([NODE, str(SCRIPTS / 'resolve-source.cjs'), str(self.root)], capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.root / 'source.mp4').read_bytes(), b'explicit source')

    def test_resolver_missing_input_fails_without_creating_source(self):
        (self.root / 'final.mp4').write_bytes(b'export')
        r = subprocess.run([NODE, str(SCRIPTS / 'resolve-source.cjs'), str(self.root)], capture_output=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse((self.root / 'source.mp4').exists())

    def test_prepare_resolves_source_before_any_worker(self):
        bin_dir = self.fake_bin()
        (bin_dir / 'node').unlink()
        fake = bin_dir / 'node'
        fake.write_text('#!/bin/bash\ncase "${1##*/}" in\nresolve-source.cjs) exec '+NODE+' "$@" ;;\n*) [ -f "$2/source.mp4" ] || { echo "worker started without source"; exit 7; } ;;\nesac\n')
        fake.chmod(0o755)
        (self.root / 'small.mov').write_bytes(b'a')
        (self.root / 'large.mp4').write_bytes(b'abcdef')
        (self.root / 'final.mp4').write_bytes(b'x' * 100)
        r = subprocess.run(['/bin/bash', str(SCRIPTS / 'prepare.sh'), str(self.root)], env={**os.environ, 'PATH': str(bin_dir)}, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.root / 'source.mp4').read_bytes(), b'abcdef')

if __name__ == '__main__':
    unittest.main()

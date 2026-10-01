# Full videos inside GitHub README

GitHub renders a full, controllable video player in a README for videos uploaded via its **Markdown attachment uploader** or the official GitHub CLI media attachment option (`gh` 2.99+). A relative path to an MP4 committed in this repository, a `raw.githubusercontent.com` URL, and an `iframe` are **not equivalent** and must not be presented as working inline video embeds.

The original high-quality masters remain under `projects/**/renders/` and the root `TEOLA-ad.mp4`. GitHub attachment copies are only for in-README streaming, with audio, seek bar and fullscreen (subject to the browser's and GitHub's player behavior).

## Films to attach

| ID | Finished master |
| --- | --- |
| `arabic` | [Motion Graphics Skills Arabic](../projects/mgs-promo/renders/mgs-promo-final.mp4) |
| `curve` | [The Curve English](../projects/skills-promo-curve/renders/skills-promo-curve.mp4) |
| `countdown` | [5 Skills Countdown English](../projects/skills-countdown-promo/renders/skills-promo-final.mp4) |
| `teola` | [TEOLA](../TEOLA-ad.mp4) |
| `four-steps` | [Four Steps Events](../projects/four-steps-events/renders/Four-Steps-Events-Motion-Final-v2.mp4) |
| `jedar` | [JEDAR](../projects/jedar-lesh-majani/renders/JEDAR-lesh-majani-final.mp4) |

## Automated publishing (recommended)

Check out this PR's branch locally on a computer signed in to your GitHub account. You need [GitHub CLI 2.99 or later](https://cli.github.com/) with personal login (OAuth or personal access token), Python 3, FFmpeg and FFprobe.

```bash
gh auth login
git checkout fix/readme-playable-promos-20261001
python3 tools/publish_readme_videos.py --pr 33 --max-mb 10 --commit
git push origin fix/readme-playable-promos-20261001
```

This command:
1. Reads **each of the six final film masters**, including the original sound and full duration.
2. Uploads originals if they are below the size limit. Otherwise, makes a separate 2-pass H.264/AAC upload encode within the 10 MB attachment limit. The final masters in the repository **remain untouched**.
3. Uses official `gh pr comment --attach` to upload full videos and create real `github.com/user-attachments/assets/UUID` links.
4. Extracts the links from the new PR comment, validates them and fills the six README video slots with native players.
5. Commits the README locally (without pushing until the final command).

With a paid GitHub account that permits 100 MB video attachments, use `--max-mb 100` to keep **all six original masters** rather than compressing them. The command is idempotent at the README slot level, but each run re-uploads attachments. Use it once and verify the result.

**Important:** A GitHub Actions `GITHUB_TOKEN` is a GitHub App installation token. The native attachment endpoint does not accept that token type, so this cannot be completed from CI with only `GITHUB_TOKEN`. A personally authenticated CLI (or the web editor below) is required.

## Browser upload (manual alternative)



1. Open the repository on GitHub, sign in, open `README.md`, and choose **Edit this file**.
2. Drag a complete MP4 into the editor (or use the editor's **Attach files** control). **Do not commit the temporary edit.** Uploading it creates a URL beginning with `https://github.com/user-attachments/assets/` and ending in a UUID. Copy it.
3. Repeat once per film. The embedded attachment has to be the **whole final MP4** with its audio, not a GIF, still, teaser or opening-only render.
4. If GitHub rejects a file because of its upload limit, create a secondary H.264/AAC delivery encode and recheck its duration, audio and readability. Do not overwrite the high-quality master. GitHub may apply different attachment size limits depending on the account and surface.
5. Save the six attachment URLs in a local JSON file named `readme-video-attachments.json` (do not add it to Git until you are ready):

```json
{
  "arabic": "https://github.com/user-attachments/assets/REPLACE_WITH_UPLOADED_UUID",
  "curve": "https://github.com/user-attachments/assets/REPLACE_WITH_UPLOADED_UUID",
  "countdown": "https://github.com/user-attachments/assets/REPLACE_WITH_UPLOADED_UUID",
  "teola": "https://github.com/user-attachments/assets/REPLACE_WITH_UPLOADED_UUID",
  "four-steps": "https://github.com/user-attachments/assets/REPLACE_WITH_UPLOADED_UUID",
  "jedar": "https://github.com/user-attachments/assets/REPLACE_WITH_UPLOADED_UUID"
}
```

The placeholders above are **examples, not real upload URLs**, and validation rejects them.

From the repository root, run:

```bash
python3 tools/embed_readme_videos.py readme-video-attachments.json
python3 tools/embed_readme_videos.py readme-video-attachments.json --check
python3 -m unittest discover -s tests -p 'test_embed_readme_videos.py' -v
```

This replaces the six labeled thumbnail slots with native HTML5 `<video>` players containing only verified **GitHub attachment URL shapes**. Commit the updated README and inspect the rendered README on GitHub (not only a local Markdown preview). GitHub may start players muted; unmute using the native control to hear the original audio.

## Acceptance checklist

- All six players appear **inside** the README, not on a separate website.
- Each plays from 0:00 through its exact delivered duration without stopping early.
- Seek, play/pause, fullscreen and audio controls work in desktop and mobile browsers.
- The original high-quality MP4s remain downloadable and their source links remain valid.
- Revisit the rendered README to confirm that GitHub has not changed its Markdown/media policy.
- Keep the README lightweight: use `preload="metadata"` so six full films are not eagerly downloaded at page load.

**Known constraint:** the connected GitHub repository API can edit files and create PRs but does not expose the media upload endpoint with a personal OAuth or PAT token. Use personally authenticated `gh` CLI 2.99+ or the GitHub web editor. Never commit generated UUIDs or pretend a source MP4 path is an inline player.

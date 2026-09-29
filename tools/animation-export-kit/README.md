# Animation export kit

Turns an animated HTML file into an MP4 you can post. 30 frames a second, 12 seconds by default. Feed size (1080 x 1350) or Story and Reel size (1080 x 1920).

You don't write any code. You install two free tools once, then run one command.

## What's in the folder

| File | What it is |
|---|---|
| `render.mjs` | The exporter. It opens your HTML in a hidden browser, steps through it frame by frame and hands the frames to ffmpeg. |
| `package.json` | Tells npm which version of Puppeteer (the hidden browser) to install: 23.11.1. |
| `examples/launch-video/index.html` | My LinkedIn AI OS launch video, 1080 x 1350, as Opus 5.5 wrote it. Use it to test the kit. |
| `examples/story-ad/index.html` | A portrait Story ad, 1080 x 1920, built in my Claude Code session with Opus 5.5. Use it to test portrait. |
| `prompts/prompt-that-writes-your-prompt.txt` | The prompt from the newsletter. Give it your idea and brand, and it writes a build prompt for Claude Code. |
| `prompts/original-launch-brief.txt` | The exact brief behind the launch video. Two lines in it were only for my test: "Output the complete HTML only, without markdown fences." and "Do not use tools, browse, install, delegate or alter files." Swap both for "Save it as index.html in this folder." before you use it. |
| `prompts/explainer-brief.txt`, `prompts/story-ad-brief.txt` | The briefs behind the explainer and the Story ad in the newsletter. |

## What your HTML needs

The exporter works with any single HTML file that:

1. Has a function called `window.seek(seconds)` that draws the exact frame for that moment.
2. Is designed at the size you export. Changing `--width` and `--height` changes the window, not the design, so a feed layout won't rearrange itself for a Story.
3. Loads nothing from the internet. The exporter blocks internet requests, so web fonts and online images won't appear.

The prompt in `prompts/` already asks Claude for `window.seek` and one self-contained file. It will ask you for the size: answer 1080 x 1350 for a feed post or 1080 x 1920 for a Story or Reel. And add one line to your message: "Nothing loaded from the internet, no web fonts."

---

## Step 1. Install Node.js (once)

Node.js runs the exporter. npm comes with it.

1. Go to the official download page: https://nodejs.org/en/download
2. Download the **LTS** version for your computer and run the installer. The kit needs Node 18 or later, and LTS is the safe pick.
3. Close your terminal and open a new one.

**Mac:** open Terminal (press Cmd + Space, type Terminal).
**Windows:** open PowerShell (press the Windows key, type PowerShell).

Check it worked:

```
node --version
npm --version
```

You should see a version number for each. If `node --version` starts with v16 or lower, install the LTS version.

## Step 2. Install ffmpeg (once)

ffmpeg is a free video tool. It turns the frames into an MP4. Official page: https://ffmpeg.org/download.html

**First, check you don't already have it:**

```
ffmpeg -version
```

If that prints a line starting `ffmpeg version`, skip to Step 3.

### Mac

**If you already use Homebrew** (check with `brew --version`), install the Homebrew package (https://formulae.brew.sh/formula/ffmpeg):

```
brew install ffmpeg
```

You don't need Homebrew for this kit. If you don't have it, use the manual route below. Homebrew itself is at https://brew.sh if you ever want it.

**Manual route (no Homebrew):**

1. From https://ffmpeg.org/download.html, pick the macOS icon and download a static build from one of the sites listed there. Unzip it. You get one file called `ffmpeg`.
2. Check nothing is already in the folder you'll use. This should say "No such file or directory":

   ```
   ls ~/bin/ffmpeg
   ```

   If it lists a file, stop. You already have an ffmpeg there, so fix your PATH instead of replacing it.
3. Move it in without overwriting anything (`-n` means never overwrite), then make it runnable:

   ```
   mkdir -p ~/bin
   mv -n ~/Downloads/ffmpeg ~/bin/ffmpeg
   chmod +x ~/bin/ffmpeg
   ```

   If your download landed somewhere else, change `~/Downloads/ffmpeg` to that path.
4. Add that folder to your PATH once:

   ```
   echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zprofile
   ```

5. Close Terminal and open a new one. If macOS blocks ffmpeg the first time it runs, open System Settings, then Privacy & Security, and allow it there.

### Windows

**With winget** (built into recent Windows). This is the command gyan.dev documents for its build (https://www.gyan.dev/ffmpeg/builds/):

```
winget install "FFmpeg (Essentials Build)"
```

Close PowerShell and open a new one.

**Manual route:**

1. From https://www.gyan.dev/ffmpeg/builds/ download the "essentials" release zip.
2. Extract it to a folder you'll keep, for example `C:\Users\<your name>\ffmpeg`. Inside you'll find a folder named after the version, and inside that a `bin` folder holding `ffmpeg.exe`. Copy the full path of that `bin` folder from File Explorer's address bar.
3. Add it to **your own** PATH, not the system one: press the Windows key, type "environment variables", open **Edit environment variables for your account**, select **Path** under your user variables, click **Edit**, then **New**, and paste the `bin` path. Click OK on every window.
4. Close PowerShell and open a new one.

**Check ffmpeg worked (Mac or Windows):**

```
ffmpeg -version
```

You should see a line starting `ffmpeg version`. If you see "not found" or "not recognized", the folder isn't on your PATH yet, or the terminal needs reopening.

## Step 3. Open this folder in your terminal

Unzip `export-kit.zip`. You'll get a folder called `animation-export-kit`.

**Mac** (if it's in Downloads):

```
cd ~/Downloads/animation-export-kit
```

**Windows PowerShell** (if it's in Downloads):

```
cd $HOME\Downloads\animation-export-kit
```

Check you're in the right place. `ls` (Mac) or `dir` (Windows) should list `render.mjs` and `package.json`.

## Step 4. Install the kit's one dependency

```
npm install
```

This downloads Puppeteer into a `node_modules` folder here. Puppeteer then downloads its own copy of Chrome for Testing into a cache in your home folder, `~/.cache/puppeteer` (that's Puppeteer's default, see https://pptr.dev/guides/installation). Both are free and need no account. Your normal browser is left alone. To remove this kit later, delete its own folder. Keep the shared Chrome cache if you use Puppeteer in any other project.

## Step 5. Test it with the examples

A one-second feed test first:

```
node render.mjs examples/launch-video/index.html test-feed --seconds 1
```

Then a one-second portrait test:

```
node render.mjs examples/story-ad/index.html test-story --seconds 1 --width 1080 --height 1920
```

Each makes a new folder with `video.mp4` and three check pictures.

Then the full 12-second launch video:

```
node render.mjs examples/launch-video/index.html launch-video
```

## Step 6. Export your own animation

Copy your HTML file (the one Claude Code made) into this folder. Every export needs its own new folder name.

Feed post (1080 x 1350):

```
node render.mjs index.html my-video
```

Story or Reel (1080 x 1920, and the HTML must be designed at that size):

```
node render.mjs index.html my-story --width 1080 --height 1920
```

Add a GIF as well (smaller, softer, loops in email), into another new folder:

```
node render.mjs index.html my-video-gif --gif
```

Add `--seconds 8` (any number from 1 to 60) if your animation isn't 12 seconds long. `--width` and `--height` take even numbers from 320 to 3840.

## What you get

Inside your new output folder:

- `video.mp4`: your size, 30 frames a second, no sound.
- `check-start.png`, `check-middle.png`, `check-end.png`: look at these first. If start and end match, the loop won't jump.
- `render-log.json`: the settings used, the frame count, and any page errors or blocked internet requests.
- `video.gif` if you asked for one.

## Safety rules built in

- It never overwrites anything. The output folder must be new or empty.
- It checks Node, ffmpeg and Puppeteer before doing any work, and tells you which is missing.
- It stops if your HTML has no `window.seek`, or if the frames aren't the size you asked for.
- It blocks every internet request from the page.
- If anything fails, or you press Ctrl+C, it closes the hidden browser and ffmpeg and deletes the half-made video.

## If something goes wrong

| You see | Do this |
|---|---|
| `ffmpeg was not found` | Go back to Step 2. Reopen the terminal after changing PATH. |
| `Puppeteer is not installed in this folder` | Run `npm install` inside this folder (Step 4). |
| `Node ... is too old` | Install the LTS version from Step 1. |
| `The output folder is not empty` | Pick a new name, for example `my-video-2`. |
| `The HTML has no window.seek(seconds) function` | Ask Claude Code: "Add a window.seek(seconds) function that draws any moment from the time alone." |
| `Frames came out ... expected ...` | Ask Claude Code to draw the animation at exactly the size you're exporting. |
| `ffmpeg stopped early` | Check `ffmpeg -version` works, then try again with a new output folder. |
| `npm` or `node` not recognised | Go back to Step 1 and reopen the terminal. |

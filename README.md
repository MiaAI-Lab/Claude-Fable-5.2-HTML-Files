# Claude Fable 5.2 HTML Files

A gallery of the 76 HTML studies present in this collection, with their complete original prompts. The index follows the layout of [the Fable 5.1 gallery](https://miaai-lab.github.io/Fable-5.1-100-HTML-Files/): a searchable list, large screenshot previews, links that open each study, and expandable prompts.

## Build and screenshots

```sh
python3 scripts/build_gallery.py
python3 -m pip install -r scripts/requirements.txt
python3 -m playwright install --with-deps chromium
python3 scripts/capture_screenshots.py
```

Open `index.html` directly or serve this directory with a static web server. Real screenshots are saved to `thumbs/`. Before capture, the preview area links to the study and explains that its screenshot is pending. The capture script also verifies search, prompt expansion, and mobile overflow.

The source numbering is preserved. Files 076–078 are absent from the supplied collection; no studies or prompts are invented.

## Publish the private repository and GitHub Pages

On a machine with network access and GitHub CLI authenticated for MiaAI-Lab:

```sh
bash scripts/publish.sh
```

This creates the repository privately if needed, verifies that an existing repository is private, pushes the collection without force, configures Pages to use Actions, and starts the deployment workflow. It uses a temporary Git checkout and preserves the supplied source directory.

The workflow captures screenshots of every study in Chromium, verifies the gallery, and deploys only HTML, prompt files, screenshots, and the favicon. Screenshots are also available as a `gallery-screenshots` workflow artifact. A failed capture or check prevents deployment. If Pages is not enabled, the workflow completes the screenshots and checks and skips deployment. Once Pages is enabled with Actions, rerun the workflow to publish.

GitHub Pages for a private organization repository requires a supporting GitHub Team or Enterprise plan. Repository privacy is retained; Pages site access is a separate GitHub setting. This project requests publication of the gallery.

Expected URL after successful deployment:
https://miaai-lab.github.io/Claude-Fable-5.2-HTML-Files/

Local preparation does not imply that the repository has been pushed, screenshots captured, or Pages enabled. Check the workflow's successful deployment before treating that URL as live.

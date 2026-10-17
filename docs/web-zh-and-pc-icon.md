# Web Chinese UI and Pc glass icon

This fork carries the Chinese UI fix previously validated in the self-hosted v0.9.0 Web build.

- Downloaded served fonts are registered in egui's UI font families as well as the document font library. The Web shell retains them across language/theme font-definition resets.
- Web Auto resolves to Simplified Chinese. Explicitly saved languages remain authoritative; native locale detection is unchanged.
- Chinese is requested from the host's served-font catalog even when the browser prefers English.
- The in-app title bar uses the rounded 128 px Pc glass tile. The original full-bleed SVG and rounded title-bar SVG are editable sources; PNGs were exported with VectorCraft CLI.
- Both Web entry points copy the same icon directory through Trunk. The manifest and iOS standalone metadata use relative paths, so deployment under a subdirectory works. The PNG simulates glass statically; it is not an Apple native layered icon.

## Fonts and packaging

The UI fix still requires actual CJK font bytes. Fonts are deliberately not committed.
Use the existing optional `PHOTOCRAFT_WEB_FONTS_DIR` input documented in
`packaging/web/README.md`, pointing to a served-font folder with
`fonts/manifest.txt` and the font/license paths listed in it. Include a
Simplified Chinese family whose scripts contain Hans. The deployed reference
uses unmodified Noto Sans CJK Regular at notofonts/noto-cjk commit
`f8d157532fbfaeda587e826d4cd5b21a49186f7c`, under SIL OFL 1.1.
Run `packaging/web/package.sh` with that input to copy the font catalog,
font files and licenses into the final site.

## Validation boundary

The earlier deployed font fix was exercised in Chromium: Chinese UI and language
menus, English/Chinese switching, preference persistence, opening PNG and saving PSD.
The Pc exports were visually reviewed at 1024, 64, 32 and 16 px.
This source-port commit has not been rebuilt or run through Rust checks.
No build, deployment or production service restart is part of this commit.
## Touch menus

The Web shell installs a Rust capture listener before eframe starts. It mirrors
the previously deployed, user-verified menu touch workaround: a gesture beginning
within the canvas's top 32 CSS pixels uses only eframe's PointerEvent path.
Duplicate TouchEvents for that gesture are consumed until its final touch ends.
Browsers without PointerEvent keep their touch fallback. Mouse events, the pen
feed and touch gestures starting in the editor remain unchanged.

The Rust port must still be checked in a real browser; the earlier JavaScript
workaround's iPad validation does not constitute validation of this new binary.

## Web-only GitHub Actions

`.github/workflows/web.yml` builds on pushes to main, pull requests and manual
dispatch. All imported upstream workflows are manual-only in this fork.
Only the browser app and its small WebAssembly boot loader are compiled.
The workflow downloads pinned, SHA-256-verified SC/TC/JP/KR fonts and their OFL
licenses with `packaging/web/prepare-fonts.py`, then passes that external folder
to the existing Web packager. Font files are not stored in Git.

Download `photocraft-web-<commit>` from the workflow's Artifacts section.
It contains the ready-to-host static-site zip and SHA256SUMS.txt, retained for
30 days. Successful compilation alone is not browser or iPad acceptance.

Both Web entry points explicitly disable wasm-opt; the earlier Binaryen 108
optimized output failed at runtime in Chromium. Thin LTO and two Cargo jobs
reduce CI memory pressure. No desktop packaging or server deployment runs.


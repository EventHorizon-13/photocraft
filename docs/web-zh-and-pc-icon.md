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
The separate deployed touch-menu workaround is not part of this Rust patch.

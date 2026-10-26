#!/usr/bin/env python3
"""Add a lazy Chinese glyph fallback to the fixed SolidCraft Web release."""
import pathlib
import sys

root = pathlib.Path(sys.argv[1]).resolve()

def replace_once(path, old, new):
    file = root / path
    text = file.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one source anchor in {path}, got {count}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")

replace_once(
    "crates/ui-egui/src/fonts.rs",
    "/// Lower-case file-name fragments that identify CJK fonts. Deliberately specific: generic\n",
    '''/// Install the simplified-Chinese fallback without replacing the Japanese CJK face.\n/// The Web shell downloads this font only for a Chinese UI and retains it across font resets.\npub fn install_chinese_fallback_for(ctx: &egui::Context, bytes: Vec<u8>) -> bool {\n    let fonts = ctx.data(|d| d.get_temp::<FontDefinitions>(installed_fonts_id())).unwrap_or_else(base_font_definitions);\n    match with_fallback(fonts, CHINESE_FALLBACK, bytes) {\n        Some(fonts) => {\n            install(ctx, fonts);\n            true\n        }\n        None => false,\n    }\n}\n\n/// Lower-case file-name fragments that identify CJK fonts. Deliberately specific: generic\n''')

replace_once(
    "crates/ui-egui/src/fonts.rs",
    '''    if let Some(data) = previous.and_then(|f| f.font_data.get(CJK_FALLBACK).cloned()) {\n        fonts.font_data.insert(CJK_FALLBACK.to_owned(), data);\n        for family in all_families() {\n            fonts.families.entry(family).or_default().push(CJK_FALLBACK.to_owned());\n        }\n    }\n''',
    '''    if let Some(previous) = previous {\n        // Keep both downloaded faces when a theme, language, or UI-font change rebuilds Web fonts.\n        for name in [CJK_FALLBACK, CHINESE_FALLBACK] {\n            if let Some(data) = previous.font_data.get(name).cloned() {\n                fonts.font_data.insert(name.to_owned(), data);\n                for family in all_families() {\n                    let list = fonts.families.entry(family).or_default();\n                    list.retain(|entry| entry != name);\n                    list.push(name.to_owned());\n                }\n            }\n        }\n    }\n''')

replace_once(
    "apps/solidcraft-web/src/main.rs",
    '    const JAPANESE_FONT_PATH: &str = "./fonts/BIZUDPGothic-Regular.ttf";\n',
    '    const JAPANESE_FONT_PATH: &str = "./fonts/BIZUDPGothic-Regular.ttf";\n    const CHINESE_FONT_PATH: &str = "./fonts/DroidSansFallbackFull.ttf";\n')

replace_once(
    "apps/solidcraft-web/src/main.rs",
    '''        /// The fetched CJK font's bytes: kept so a language change can re-order the fallbacks.\n        cjk_bytes: Option<Vec<u8>>,\n        /// The language the fonts were last set up for (a CJK UI leads with the CJK face).\n''',
    '''        /// The fetched CJK font's bytes: kept so a language change can re-order the fallbacks.\n        cjk_bytes: Option<Vec<u8>>,\n        /// Simplified-Chinese glyph fallback, fetched only for a Chinese UI.\n        chinese_font_result: FontLoadResult,\n        chinese_bytes: Option<Vec<u8>>,\n        chinese_font_requested: bool,\n        /// The language the fonts were last set up for (a CJK UI leads with the CJK face).\n''')

replace_once(
    "apps/solidcraft-web/src/main.rs",
    '''            if self.font.tick(&mut self.app.preferences.language) {\n                self.fetch_font(ctx);\n            }\n            // The CJK face leads only a CJK UI: its Cyrillic glyphs are full-width, so switching\n''',
    '''            if self.font.tick(&mut self.app.preferences.language) {\n                self.fetch_font(ctx);\n            }\n            let chinese_result = { self.chinese_font_result.borrow_mut().take() };
            if let Some(result) = chinese_result {\n                match result {\n                    Ok(bytes) => {\n                        self.chinese_bytes = Some(bytes);\n                        self.apply_fonts(ctx);\n                        log::info!("loaded Web simplified-Chinese fallback from {CHINESE_FONT_PATH}");\n                        ctx.request_repaint();\n                    }\n                    Err(err) => log::warn!("failed to fetch simplified-Chinese font from {CHINESE_FONT_PATH}: {err}"),\n                }\n            }\n            if matches!(self.app.preferences.language.as_str(), "zh" | "zh-TW") && !self.chinese_font_requested {\n                self.fetch_chinese_font(ctx);\n            }\n            // The CJK face leads only a CJK UI: its Cyrillic glyphs are full-width, so switching\n''')

replace_once(
    "apps/solidcraft-web/src/main.rs",
    '''            match self.cjk_bytes.clone() {\n                Some(bytes) => {\n                    solidcraft_ui_egui::fonts::install_cjk_font_for(ctx, bytes, &self.app.preferences.language);\n                }\n                None => solidcraft_ui_egui::fonts::setup_fonts(ctx),\n            }\n            self.font_language.clone_from(&self.app.preferences.language);\n''',
    '''            match self.cjk_bytes.clone() {\n                Some(bytes) => {\n                    solidcraft_ui_egui::fonts::install_cjk_font_for(ctx, bytes, &self.app.preferences.language);\n                }\n                None => solidcraft_ui_egui::fonts::setup_fonts(ctx),\n            }\n            if let Some(bytes) = self.chinese_bytes.clone()\n                && !solidcraft_ui_egui::fonts::install_chinese_fallback_for(ctx, bytes)\n            {\n                log::warn!("could not install simplified-Chinese fallback font");\n            }\n            self.font_language.clone_from(&self.app.preferences.language);\n''')

replace_once(
    "apps/solidcraft-web/src/main.rs",
    '''        fn fetch_font(&self, ctx: &egui::Context) {\n            let slot = self.font_result.clone();\n            let ctx = ctx.clone();\n            wasm_bindgen_futures::spawn_local(async move {\n                let res = fetch_font_bytes(JAPANESE_FONT_PATH).await;\n                *slot.borrow_mut() = Some(res);\n                ctx.request_repaint();\n            });\n        }\n''',
    '''        fn fetch_font(&self, ctx: &egui::Context) {\n            let slot = self.font_result.clone();\n            let ctx = ctx.clone();\n            wasm_bindgen_futures::spawn_local(async move {\n                let res = fetch_font_bytes(JAPANESE_FONT_PATH).await;\n                *slot.borrow_mut() = Some(res);\n                ctx.request_repaint();\n            });\n        }\n\n        fn fetch_chinese_font(&mut self, ctx: &egui::Context) {\n            self.chinese_font_requested = true;\n            let slot = self.chinese_font_result.clone();\n            let ctx = ctx.clone();\n            wasm_bindgen_futures::spawn_local(async move {\n                let res = fetch_font_bytes(CHINESE_FONT_PATH).await;\n                *slot.borrow_mut() = Some(res);\n                ctx.request_repaint();\n            });\n        }\n''')

replace_once(
    "apps/solidcraft-web/src/main.rs",
    '''                            font: Default::default(),\n                            font_result: Rc::new(std::cell::RefCell::new(None)),\n                            cjk_bytes: None,\n                            font_language,\n''',
    '''                            font: Default::default(),\n                            font_result: Rc::new(std::cell::RefCell::new(None)),\n                            cjk_bytes: None,\n                            chinese_font_result: Rc::new(std::cell::RefCell::new(None)),\n                            chinese_bytes: None,\n                            chinese_font_requested: false,\n                            font_language,\n''')

print("Patched SolidCraft Web with a lazily fetched simplified-Chinese font fallback.")

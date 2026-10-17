//! Avoid delivering a menu gesture twice through eframe's pointer and touch paths.
//!
//! A native PointerEvent opens the press-driven menu immediately. The matching
//! TouchEvent otherwise queues another primary press and closes it again.
//! Only gestures starting in the top menu strip use the pointer path alone;
//! editor touch gestures, multiple touches and the pen feed keep their existing paths.

use std::cell::Cell;
use std::rc::Rc;

use wasm_bindgen::JsCast as _;
use wasm_bindgen::closure::Closure;

const MENU_STRIP_HEIGHT: f64 = 32.0;

pub(super) fn install(document: &web_sys::Document, canvas: &web_sys::HtmlCanvasElement) -> Result<(), wasm_bindgen::JsValue> {
    // Older browsers without PointerEvent still need eframe's touch fallback.
    if !js_sys::Reflect::has(&js_sys::global(), &wasm_bindgen::JsValue::from_str("PointerEvent")).unwrap_or(false) {
        return Ok(());
    }
    let menu_touch = Rc::new(Cell::new(false));
    let options = web_sys::AddEventListenerOptions::new();
    options.set_capture(true);
    options.set_passive(false);
    for kind in ["touchstart", "touchmove", "touchend", "touchcancel"] {
        let menu_touch = Rc::clone(&menu_touch);
        let canvas = canvas.clone();
        let callback = Closure::<dyn FnMut(web_sys::TouchEvent)>::new(move |event: web_sys::TouchEvent| {
            let event_type = event.type_();
            let touches = event.touches();
            if event_type == "touchstart" && !menu_touch.get() && touches.length() == 1 {
                let on_canvas = event.target().and_then(|target| target.dyn_into::<web_sys::HtmlCanvasElement>().ok()).is_some_and(|target| target == canvas);
                if on_canvas && let Some(touch) = touches.item(0) {
                    let y = f64::from(touch.client_y()) - canvas.get_bounding_client_rect().top();
                    menu_touch.set((0.0..MENU_STRIP_HEIGHT).contains(&y));
                }
            }
            if !menu_touch.get() {
                return;
            }
            event.stop_immediate_propagation();
            if event.cancelable() {
                event.prevent_default();
            }
            if matches!(event_type.as_str(), "touchend" | "touchcancel") && touches.length() == 0 {
                menu_touch.set(false);
            }
        });
        document.add_event_listener_with_callback_and_add_event_listener_options(kind, callback.as_ref().unchecked_ref(), &options)?;
        // The listener lives for the page's lifetime, as do eframe's own listeners.
        callback.forget();
    }
    Ok(())
}

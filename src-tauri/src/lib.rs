use tauri::{
    menu::{Menu, MenuItem},
    tray::TrayIconBuilder,
    Manager,
};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_notification::init())
        .setup(|app| {
            // Build system tray menu
            let quit_i = MenuItem::with_id(app, "quit", "Quit CyberShield", true, None::<&str>)?;
            let show_i = MenuItem::with_id(app, "show", "Open Scanner", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&show_i, &quit_i])?;

            let _tray = TrayIconBuilder::new()
                .menu(&menu)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "quit" => {
                        app.exit(0);
                    }
                    "show" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                    _ => {}
                })
                .build(app)?;

            // Automatically spawn embedded FastAPI sidecar backend
            #[cfg(desktop)]
            {
                use tauri_plugin_shell::ShellExt;
                let app_handle = app.handle().clone();
                tauri::async_runtime::spawn(async move {
                    if let Ok(sidecar) = app_handle.shell().sidecar("cybershield-backend") {
                        if let Ok((_rx, _child)) = sidecar.spawn() {
                            println!("[Tauri] Embedded CyberShield FastAPI backend sidecar started successfully.");
                        }
                    }
                });
            }

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running CyberShield desktop application");
}

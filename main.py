import os
import sys
import ctypes
import threading
import keyboard
import requests
import time
import win32api
import win32con
import win32gui
import win32process
import pystray
from PIL import Image
from pystray import MenuItem as item
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass


try:
    ctypes.windll.user32.LoadKeyboardLayoutW("0000040C", 1 | 0x00000100)
except:
    pass

from config_manager import Config
from logic import DofusLogic
from gui import OrganizerGUI
from radial_menu import RadialMenu


AZERTY_TO_SCAN = {
    "a": 16,
    "z": 17,
    "e": 18,
    "r": 19,
    "t": 20,
    "y": 21,
    "u": 22,
    "i": 23,
    "o": 24,
    "p": 25,
    "q": 30,
    "s": 31,
    "d": 32,
    "f": 33,
    "g": 34,
    "h": 35,
    "j": 36,
    "k": 37,
    "l": 38,
    "m": 39,
    "w": 44,
    "x": 45,
    "c": 46,
    "v": 47,
    "b": 48,
    "n": 49,
    "1": 2,
    "2": 3,
    "3": 4,
    "4": 5,
    "5": 6,
    "6": 7,
    "7": 8,
    "8": 9,
    "9": 10,
    "0": 11,
    "f1": 59,
    "f2": 60,
    "f3": 61,
    "f4": 62,
    "f5": 63,
    "f6": 64,
    "f7": 65,
    "f8": 66,
    "f9": 67,
    "f10": 68,
    "f11": 87,
    "f12": 88,
    "tab": 15,
    "enter": 28,
    "space": 57,
    "esc": 1,
    "backspace": 14,
    "²": 41,
    "&": 2,
    "é": 3,
    '"': 4,
    "'": 5,
    "(": 6,
    "-": 7,
    "è": 8,
    "_": 9,
    "ç": 10,
    "à": 11,
    ")": 12,
    "=": 13,
    "num 1": 79,
    "num 2": 80,
    "num 3": 81,
    "num 4": 75,
    "num 5": 76,
    "num 6": 77,
    "num 7": 71,
    "num 8": 72,
    "num 9": 73,
    "num 0": 82,
}


class OrganizerApp:
    def __init__(self):
        self.config = Config()
        self.logic = DofusLogic(self.config)
        self.gui = OrganizerGUI(self)
        self.current_idx = 0
        self.hotkey_actions = {}

        self.logic.set_error_callback(self.show_calibration_error)

        self.radial_focus = RadialMenu(
            self.gui.root, self.on_radial_focus_select, accent_color="#444444"
        )
        saved_vol = self.config.data.get("volume_level", 50) / 100.0
        self.radial_focus.set_base_volume(saved_vol)

        threading.Thread(target=self.background_listener, daemon=True).start()

        self.setup_hotkeys()
        self.refresh()
        self.setup_system_tray()

        if not self.config.data.get("tutorial_done", False):
            self.gui.root.after(800, self.gui.launch_tutorial)

        self.gui.root.after(1000, self.check_conflicting_software)

    def setup_system_tray(self):

        icon_path = "logo.ico"

        try:
            image = Image.open(icon_path)
        except:

            image = Image.new("RGB", (64, 64), color=(44, 62, 80))

        menu = pystray.Menu(
            item("Afficher/Cacher", self.toggle_from_tray, default=True),
            item("Quitter", self.quit_from_tray),
        )

        self.tray_icon = pystray.Icon("dosoft_tray", image, "DOFRAME", menu)
        self.tray_icon.run_detached()

    def toggle_from_tray(self, icon, item):

        self.gui.root.after(0, self.gui.toggle_visibility)

    def toggle_from_tray(self, icon, item):

        def safe_toggle():
            if self.gui.root.state() == "withdrawn":
                self.gui.root.deiconify()
                self.gui.root.lift()
                self.gui.root.focus_force()
            else:
                self.gui.root.withdraw()

        self.gui.root.after(0, safe_toggle)

    def quit_from_tray(self, icon, item):

        self.tray_icon.stop()
        self.gui.root.after(0, self.gui.root.destroy)

    def check_conflicting_software(self):

        if self.config.data.get("ignore_organizer_warning", False):
            return

        try:
            output = (
                os.popen('tasklist /FI "IMAGENAME eq organizer.exe" /NH').read().lower()
            )

            if "organizer.exe" in output:
                self.show_conflict_popup()
        except Exception:
            pass

    def show_conflict_popup(self):

        popup = ctk.CTkToplevel(self.gui.root)
        popup.title("⚠️ Conflit de logiciels détecté")
        popup.geometry("480x250")
        popup.attributes("-topmost", True)
        popup.resizable(False, False)
        popup.transient(self.gui.root)

        popup.update_idletasks()
        x = self.gui.root.winfo_x() + (self.gui.root.winfo_width() // 2) - (480 // 2)
        y = self.gui.root.winfo_y() + (self.gui.root.winfo_height() // 2) - (250 // 2)
        popup.geometry(f"+{x}+{y}")

        msg = (
            "Le logiciel 'Organizer' est actuellement ouvert.\n"
            "L'utilisation de deux gestionnaires de pages simultanément\n"
            "va créer des bugs et des conflits de focus sur DOFRAME.\n\n"
            "Nous vous recommandons fortement de le fermer."
        )

        lbl = ctk.CTkLabel(popup, text=msg, justify="center", font=ctk.CTkFont(size=13))
        lbl.pack(pady=(20, 15))

        var_ignore = ctk.BooleanVar(value=False)
        chk = ctk.CTkCheckBox(
            popup, text="Ne plus m'afficher cet avertissement", variable=var_ignore
        )
        chk.pack(pady=(0, 20))

        frame_btn = ctk.CTkFrame(popup, fg_color="transparent")
        frame_btn.pack(fill="x", padx=20)

        def on_close_organizer():
            if var_ignore.get():
                self.config.data["ignore_organizer_warning"] = True
                self.config.save()

            os.system("taskkill /F /IM organizer.exe /T")

            popup.destroy()
            self.gui.show_temporary_message(
                "✅ Organizer fermé avec succès !", "#444444"
            )

        def on_keep_organizer():
            if var_ignore.get():
                self.config.data["ignore_organizer_warning"] = True
                self.config.save()
            popup.destroy()

        btn_close = ctk.CTkButton(
            frame_btn, text="Fermer Organizer", fg_color="#444444"
        )
        btn_close.pack(side="left", expand=True, padx=10)

        btn_keep = ctk.CTkButton(frame_btn, text="Conserver", fg_color="#444444")
        btn_keep.pack(side="right", expand=True, padx=10)

        popup.grab_set()

    def show_calibration_error(self, msg):
        def trigger_error():
            if not self.gui.is_visible:
                self.gui.show_gui()
            messagebox.showwarning("Action Impossible", msg)

        self.gui.root.after(0, trigger_error)

    def update_volume(self, volume_val):
        self.config.data["volume_level"] = volume_val
        self.config.save()
        vol_float = volume_val / 100.0
        self.radial_focus.set_base_volume(vol_float)

    def get_vk(self, key_str):
        key_str = key_str.lower().strip()
        mapping = {
            "alt": win32con.VK_MENU,
            "ctrl": win32con.VK_CONTROL,
            "shift": win32con.VK_SHIFT,
            "left_click": 0x01,
            "right_click": 0x02,
            "middle_click": 0x04,
            "mouse4": 0x05,
            "mouse5": 0x06,
        }
        if key_str in mapping:
            return mapping[key_str]

        scan_code = AZERTY_TO_SCAN.get(key_str)
        if scan_code is not None:
            vk = ctypes.windll.user32.MapVirtualKeyW(scan_code, 1)
            if vk:
                return vk

        if len(key_str) == 1:
            return ord(key_str.upper())
        if key_str.startswith("f") and key_str[1:].isdigit():
            return 0x6F + int(key_str[1:])
        return None

    def is_hotkey_pressed(self, hk_str):
        if not hk_str:
            return False
        parts = hk_str.split("+")
        for p in parts:
            vk = self.get_vk(p)
            if vk is None or win32api.GetAsyncKeyState(vk) >= 0:
                return False
        return True

    def background_listener(self):
        radial_was_open = False

        while True:

            if hasattr(self, "mouse_hotkeys"):
                for hk_str, func in self.mouse_hotkeys.items():
                    is_pressed = self.is_hotkey_pressed(hk_str)
                    was_pressed = self.mouse_states.get(hk_str, False)

                    if is_pressed and not was_pressed:
                        self.mouse_states[hk_str] = True

                        def safe_mouse_execute(f=func):
                            self.release_modifiers()
                            f()

                        threading.Thread(target=safe_mouse_execute, daemon=True).start()
                    elif not is_pressed and was_pressed:
                        self.mouse_states[hk_str] = False

            m_pressed = win32api.GetAsyncKeyState(win32con.VK_MBUTTON) < 0
            if m_pressed and self.config.data.get("spam_click_active", False):
                fg_hwnd = win32gui.GetForegroundWindow()
                is_dofus = any(
                    acc["hwnd"] == fg_hwnd for acc in self.logic.all_accounts
                )
                if is_dofus:
                    while win32api.GetAsyncKeyState(win32con.VK_MBUTTON) < 0:
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        time.sleep(0.02)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        time.sleep(0.02)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        time.sleep(0.02)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                        time.sleep(0.20)
                    time.sleep(0.05)

            radial_hk = self.config.data.get("radial_menu_hotkey", "")
            radial_active = self.config.data.get("radial_menu_active", True)

            if radial_active and radial_hk:
                is_pressed = self.is_hotkey_pressed(radial_hk)

                if is_pressed and not radial_was_open:
                    radial_was_open = True
                    active_accs = [
                        {
                            "name": acc["name"],
                            "classe": acc.get("classe", "Inconnu"),
                            "hwnd": acc["hwnd"],
                        }
                        for acc in self.logic.get_cycle_list()
                    ]

                    fg_hwnd = win32gui.GetForegroundWindow()
                    current_name = None
                    for acc in active_accs:
                        if acc["hwnd"] == fg_hwnd:
                            current_name = acc["name"]
                            break

                    x, y = win32api.GetCursorPos()

                    self.gui.root.after(
                        0, self.radial_focus.show, x, y, active_accs, current_name
                    )

                elif radial_was_open and not is_pressed:
                    radial_was_open = False
                    self.gui.root.after(0, self.radial_focus.hide)

            try:
                fg_hwnd = win32gui.GetForegroundWindow()
                cycle_list = self.logic.get_cycle_list()
                if cycle_list:
                    for index, acc in enumerate(cycle_list):

                        if acc["hwnd"] == fg_hwnd:

                            if self.current_idx != index:
                                self.current_idx = index
                            break
            except Exception:
                pass

            time.sleep(0.01)

    def on_radial_focus_select(self, target_name):
        for acc in self.logic.all_accounts:
            if acc["name"] == target_name:
                self.logic.focus_window(acc["hwnd"])
                break

        cycle_list = self.logic.get_cycle_list()
        for index, acc in enumerate(cycle_list):
            if acc["name"] == target_name:
                self.current_idx = index
                break

    def is_hotkey_pressed(self, hk_str):

        if not hk_str:
            return False
        parts = hk_str.split("+")
        for p in parts:
            vk = self.get_vk(p.strip())
            if not vk:
                return False
            if win32api.GetAsyncKeyState(vk) >= 0:
                return False
        return True

    def _execute_advanced_and_update(self, mode, identifier):

        new_idx = self.logic.execute_advanced_bind(mode, identifier)
        if new_idx != -1:
            self.current_idx = new_idx

    def register_action(self, hk_str, func):
        if not hk_str:
            return
        parts = hk_str.lower().split("+")

        if "click" in hk_str or "mouse" in hk_str:
            self.mouse_hotkeys[hk_str] = func
            return

        mods = set()
        main_scan = None
        for p in parts:
            if p in ["ctrl", "alt", "shift"]:
                mods.add(p)
            elif p in AZERTY_TO_SCAN:
                main_scan = AZERTY_TO_SCAN[p]
            else:
                try:
                    main_scan = keyboard.key_to_scan_codes(p)[0]
                except:
                    pass
        if main_scan is not None:
            self.hotkey_actions[(frozenset(mods), main_scan)] = func

    def release_modifiers(self):

        try:
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)

            win32api.mouse_event(0x0100, 0, 0, 0x0001, 0)
            win32api.mouse_event(0x0100, 0, 0, 0x0002, 0)
        except:
            pass

    def restore_modifiers(self, mods):

        try:

            if "alt" in mods and win32api.GetAsyncKeyState(win32con.VK_MENU) < 0:
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)

            if "ctrl" in mods and win32api.GetAsyncKeyState(win32con.VK_CONTROL) < 0:
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)

            if "shift" in mods and win32api.GetAsyncKeyState(win32con.VK_SHIFT) < 0:
                win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        except:
            pass

    def global_hook_listener(self, event):
        if event.event_type != keyboard.KEY_DOWN:
            return

        current_mods = set()
        if win32api.GetAsyncKeyState(win32con.VK_CONTROL) < 0:
            current_mods.add("ctrl")
        if win32api.GetAsyncKeyState(win32con.VK_MENU) < 0:
            current_mods.add("alt")
        if win32api.GetAsyncKeyState(win32con.VK_SHIFT) < 0:
            current_mods.add("shift")

        key = (frozenset(current_mods), event.scan_code)
        if key in self.hotkey_actions:

            def safe_execute(mods=current_mods):
                self.release_modifiers()
                self.hotkey_actions[key]()
                time.sleep(0.05)
                self.restore_modifiers(mods)

            threading.Thread(target=safe_execute, daemon=True).start()

    def setup_hotkeys(self):
        keyboard.unhook_all()
        self.hotkey_actions = {}
        self.mouse_hotkeys = {}
        self.mouse_states = {}

        self.register_action("f12", self.quit_app)

        cfg = self.config.data

        mode = cfg.get("advanced_bind_mode", "cycle")
        if mode == "cycle":
            row_binds = cfg.get("cycle_row_binds", [])
            for index, bind_str in enumerate(row_binds):
                if bind_str:

                    self.register_action(
                        bind_str,
                        lambda idx=index: self._execute_advanced_and_update(
                            "cycle", idx
                        ),
                    )

        elif mode == "bind":
            char_binds = cfg.get("persistent_character_binds", {})
            for pseudo, bind_str in char_binds.items():
                if bind_str:
                    self.register_action(
                        bind_str,
                        lambda ps=pseudo: self._execute_advanced_and_update("bind", ps),
                    )

        try:
            if cfg.get("refresh_key"):
                self.register_action(cfg["refresh_key"], self.refresh)
            if cfg.get("auto_zaap_key"):
                self.register_action(cfg["auto_zaap_key"], self.logic.execute_auto_zaap)
            if cfg.get("sort_taskbar_key"):
                self.register_action(cfg["sort_taskbar_key"], self.logic.sort_taskbar)
            if cfg.get("invite_group_key"):
                self.register_action(
                    cfg["invite_group_key"], self.logic.execute_group_invite
                )
            if cfg.get("prev_key"):
                self.register_action(cfg["prev_key"], self.prev_char)
            if cfg.get("next_key"):
                self.register_action(cfg["next_key"], self.next_char)
            if cfg.get("leader_key"):
                self.register_action(cfg["leader_key"], self.focus_leader)
            if cfg.get("sync_key"):
                self.register_action(cfg["sync_key"], self.logic.sync_click_all)
            if cfg.get("sync_right_key"):
                self.register_action(
                    cfg["sync_right_key"], self.logic.sync_right_click_all
                )
            if cfg.get("treasure_key"):
                self.register_action(
                    cfg["treasure_key"], self.logic.execute_treasure_hunt
                )
            if cfg.get("swap_xp_drop_key"):
                self.register_action(
                    cfg["swap_xp_drop_key"], self.logic.execute_swap_xp_drop
                )
            if cfg.get("toggle_app_key"):
                self.register_action(
                    cfg["toggle_app_key"],
                    lambda: self.gui.root.after(0, self.gui.toggle_visibility),
                )
            if cfg.get("paste_enter_key"):
                self.register_action(
                    cfg["paste_enter_key"], self.logic.execute_paste_enter
                )

            keyboard.hook(self.global_hook_listener)
        except Exception as e:
            print(f"Erreur de raccourci : {e}")

    def refresh(self):

        slots = self.logic.scan_slots()

        self.gui.root.after(0, self.gui.refresh_list, slots)

    def focus_leader(self):
        if self.logic.leader_hwnd:
            self.logic.focus_window(self.logic.leader_hwnd)
            cycle_list = self.logic.get_cycle_list()
            leader_name = self.config.data.get("leader_name", "")
            for index, acc in enumerate(cycle_list):
                if acc["name"] == leader_name:
                    self.current_idx = index
                    break

    def next_char(self):
        cycle_list = self.logic.get_cycle_list()
        if not cycle_list:
            return
        self.current_idx = (self.current_idx + 1) % len(cycle_list)
        self.logic.focus_window(cycle_list[self.current_idx]["hwnd"])

    def prev_char(self):
        cycle_list = self.logic.get_cycle_list()
        if not cycle_list:
            return
        self.current_idx = (self.current_idx - 1) % len(cycle_list)
        self.logic.focus_window(cycle_list[self.current_idx]["hwnd"])

    def quit_app(self):

        my_pid = os.getpid()
        os.system(f"taskkill /F /PID {my_pid} /T")


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    if getattr(sys, "frozen", False):
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv[1:]), None, 1
        )
    else:
        script = os.path.abspath(sys.argv[0])
        params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}" {params}', None, 1
        )


def handle_multiple_instances():
    mutex_name = "DOFRAME_SINGLE_INSTANCE_MUTEX"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)

    if ctypes.windll.kernel32.GetLastError() == 183:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        rep = messagebox.askyesno(
            "Instance détectée",
            "Une instance de DOFRAME est déjà en cours d'exécution !\n\nVoulez-vous fermer l'ancienne instance pour ouvrir celle-ci ?",
            parent=root,
        )

        if rep:
            hwnd = win32gui.FindWindow(None, "DOFRAME")
            if hwnd:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
                    ctypes.windll.kernel32.TerminateProcess(handle, 0)
                    ctypes.windll.kernel32.CloseHandle(handle)
                except:
                    pass
            time.sleep(0.5)
            root.destroy()
        else:
            root.destroy()
            sys.exit(0)

    return mutex


def start_application():
    if not is_admin():
        run_as_admin()
        sys.exit()

    _app_mutex = handle_multiple_instances()

    app = OrganizerApp()
    app.gui.run()


if __name__ == "__main__":
    start_application()

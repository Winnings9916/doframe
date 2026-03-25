import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import keyboard
import threading
import time
import win32api
import win32con
import os
import webbrowser 
from PIL import Image, ImageTk

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

AZERTY_TO_SCAN = {
    'a': 16, 'z': 17, 'e': 18, 'r': 19, 't': 20, 'y': 21, 'u': 22, 'i': 23, 'o': 24, 'p': 25,
    'q': 30, 's': 31, 'd': 32, 'f': 33, 'g': 34, 'h': 35, 'j': 36, 'k': 37, 'l': 38, 'm': 39,
    'w': 44, 'x': 45, 'c': 46, 'v': 47, 'b': 48, 'n': 49,
    '1': 2, '2': 3, '3': 4, '4': 5, '5': 6, '6': 7, '7': 8, '8': 9, '9': 10, '0': 11,
    'f1': 59, 'f2': 60, 'f3': 61, 'f4': 62, 'f5': 63, 'f6': 64, 'f7': 65, 'f8': 66, 'f9': 67, 'f10': 68, 'f11': 87, 'f12': 88,
    'tab': 15, 'enter': 28, 'space': 57, 'esc': 1, 'backspace': 14,
    '²': 41, '&': 2, 'é': 3, '"': 4, "'": 5, '(': 6, '-': 7, 'è': 8, '_': 9, 'ç': 10, 'à': 11, ')': 12, '=': 13,
    'num 1': 79, 'num 2': 80, 'num 3': 81, 'num 4': 75, 'num 5': 76, 'num 6': 77, 'num 7': 71, 'num 8': 72, 'num 9': 73, 'num 0': 82,
}
SCAN_TO_AZERTY = {v: k for k, v in AZERTY_TO_SCAN.items()}

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent_gui):
        super().__init__(parent_gui.root)
        self.parent = parent_gui
        self.app = parent_gui.app
        self.title("⚙️ Paramètres DOFRAME")
        
        self.geometry("520x700")
        self.minsize(350, 300)
        self.attributes("-topmost", True)
        self.resizable(True, True)


        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        title_font = ctk.CTkFont(size=16, weight="bold")
        
        ctk.CTkLabel(self.scroll_container, text="Raccourcis Jeu & Macros", font=title_font).pack(pady=(15, 5))
        frame_game = ctk.CTkFrame(self.scroll_container)
        frame_game.pack(fill="x", padx=10, pady=5)
        
      
        self.parent.create_hotkey_row(frame_game, "Inventaire", "game_inv_key", 0, 0, "Touche jeu pour ouvrir l'inventaire")
        self.parent.create_hotkey_row(frame_game, "Carac", "game_char_key", 0, 3, "Touche jeu pour ouvrir les caractéristiques")
        
        
        self.parent.create_hotkey_row(frame_game, "Sorts", "game_spell_key", 1, 0, "Touche jeu pour ouvrir les sorts")
        self.parent.create_hotkey_row(frame_game, "Havre-Sac", "game_haven_key", 1, 3, "Touche jeu pour ouvrir le Havre-Sac")

    
        separateur = ctk.CTkFrame(frame_game, height=2, fg_color="#34495e")
        separateur.grid(row=2, column=0, columnspan=6, pady=15, sticky="ew", padx=10)

   
        self.parent.create_hotkey_row(frame_game, "Inviter Groupe", "invite_group_key", 3, 0, "Inviter automatiquement le groupe")
        self.parent.create_hotkey_row(frame_game, "Auto-Zaap", "auto_zaap_key", 3, 3, "Lancer la macro Auto-Zaap")

   
        self.parent.create_hotkey_row(frame_game, "Ctrl+V/Entrée", "paste_enter_key", 4, 0, "Coller et Entrée sur tout le monde (Ctrl+V)")
        self.parent.create_hotkey_row(frame_game, "Actualiser", "refresh_key", 4, 3, "Actualisation des pages")

  
        self.parent.create_hotkey_row(frame_game, "Trier Barre", "sort_taskbar_key", 5, 0, "Trie la barre des tâches Windows")
        self.parent.create_hotkey_row(frame_game, "Calibrage (Bind)", "calib_key", 5, 3, "Touche de bind calibrage")

        ctk.CTkLabel(self.scroll_container, text="Roue de Focus (Radiale)", font=title_font).pack(pady=(20, 5))
        frame_radial = ctk.CTkFrame(self.scroll_container)
        frame_radial.pack(fill="x", padx=10, pady=5)
        
        self.var_radial = ctk.BooleanVar(value=self.app.config.data.get("radial_menu_active", True))
        sw_radial = ctk.CTkSwitch(frame_radial, text="Activer la roue", variable=self.var_radial, command=self.save_settings)
        sw_radial.pack(pady=10)
        self.parent.bind_tooltip(sw_radial, "Activer ou désactiver complètement la roue de sélection")

        frame_radial_hk = ctk.CTkFrame(frame_radial, fg_color="transparent")
        frame_radial_hk.pack(pady=(0, 10))

        lbl_hk = ctk.CTkLabel(frame_radial_hk, text="Raccourci :")
        lbl_hk.pack(side="left", padx=(0, 5))
        
        current_val = self.app.config.data.get("radial_menu_hotkey", "alt+left_click")
        btn_hk = ctk.CTkButton(frame_radial_hk, text=current_val if current_val else "Aucun", width=120, command=lambda: self.parent.catch_key("radial_menu_hotkey", btn_hk, allow_mouse=True))
        btn_hk.pack(side="left", padx=5)
        
        self.parent.hotkey_btns["radial_menu_hotkey"] = btn_hk

        btn_x = ctk.CTkButton(frame_radial_hk, text="✖", width=25, fg_color="#c0392b", hover_color="#e74c3c", command=lambda: self.parent.clear_key("radial_menu_hotkey", btn_hk))
        btn_x.pack(side="left", padx=5)
        
       
        ctk.CTkLabel(self.scroll_container, text="Vitesse du Clic Multi", font=title_font).pack(pady=(15, 5))
        frame_speed = ctk.CTkFrame(self.scroll_container)
        frame_speed.pack(fill="x", padx=10, pady=5)
        
        lbl_speed = ctk.CTkLabel(frame_speed, text="Vitesse :")
        lbl_speed.pack(side="left", padx=10, pady=10)
        
        self.combo_speed = ctk.CTkOptionMenu(frame_speed, values=["Rapide", "Moyen", "Lent"], command=self.save_speed)
        self.combo_speed.set(self.app.config.data.get("click_speed", "Lent"))
        self.combo_speed.pack(side="left", padx=10, pady=10)
        self.parent.bind_tooltip(self.combo_speed, "Ajuste la vitesse d'exécution des clics synchronisés (Gauche et Droit)")
        
        ctk.CTkLabel(self.scroll_container, text="Macro Auto-Zaap", font=title_font).pack(pady=(15, 5))
        frame_zaap = ctk.CTkFrame(self.scroll_container)
        frame_zaap.pack(fill="x", padx=10, pady=5)

        lbl_zaap = ctk.CTkLabel(frame_zaap, text="Délai avant clic (sec) :")
        lbl_zaap.pack(side="left", padx=10, pady=10)

        self.entry_zaap_delay = ctk.CTkEntry(frame_zaap, width=60)
        self.entry_zaap_delay.insert(0, str(self.app.config.data.get("zaap_delay", "1.8")))
        self.entry_zaap_delay.pack(side="left", padx=10, pady=10)
        self.parent.bind_tooltip(self.entry_zaap_delay, "Temps d'attente pour l'ouverture du Havre-Sac (ex: 1.0 ou 1.8)")

        
        btn_close = ctk.CTkButton(self.scroll_container, text="Fermer & Sauvegarder", fg_color="#27ae60", hover_color="#2ecc71", command=self.close_and_save)
        btn_close.pack(pady=(20, 10))

    def save_settings(self):
        self.app.config.data["radial_menu_active"] = self.var_radial.get()
        self.app.config.save()
        
    def close_and_save(self):
        self.app.config.data["zaap_delay"] = self.entry_zaap_delay.get()
        self.app.config.save()
        self.destroy()

    def save_speed(self, choice):
        self.app.config.data["click_speed"] = choice
        self.app.config.save()

class FloatingToolbar:
    def __init__(self, app_controller, parent_gui):
        self.app = app_controller
        self.parent_gui = parent_gui
        self.window = tk.Toplevel(parent_gui.root)
        self.window.overrideredirect(True) 
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.90) 
        self.window.configure(bg="#1e1e1e")
        
        self.x = 0; self.y = 0
        saved_x = self.app.config.data.get("toolbar_x", 100)
        saved_y = self.app.config.data.get("toolbar_y", 100)
        self.window.geometry(f"+{saved_x}+{saved_y}")
        
        title_frame = tk.Frame(self.window, bg="#c0392b", cursor="fleur")
        title_frame.pack(fill="x")
        title_frame.bind("<Button-1>", self.start_move)
        title_frame.bind("<B1-Motion>", self.do_move)
        title_frame.bind("<ButtonRelease-1>", self.stop_move) 
        
        tk_lbl = tk.Label(title_frame, text="≡ Doframe ≡", bg="#c0392b", fg="white", font=("Arial", 8, "bold"))
        tk_lbl.pack(pady=2)
        tk_lbl.bind("<Button-1>", self.start_move)
        tk_lbl.bind("<B1-Motion>", self.do_move)
        tk_lbl.bind("<ButtonRelease-1>", self.stop_move) 

        content = tk.Frame(self.window, bg="#1e1e1e")
        content.pack(padx=5, pady=5)
        
        top_row = tk.Frame(content, bg="#1e1e1e")
        top_row.pack(fill="x", pady=(0, 5))
        
        self.btn_show_gui = ctk.CTkButton(top_row, text="⬅", width=25, height=25, fg_color="#34495e", hover_color="#2c3e50", command=self.parent_gui.show_gui)
        self.btn_show_gui.pack(side="left", padx=2)
        self.parent_gui.bind_tooltip(self.btn_show_gui, "Ouvrir l'interface principale")
        
        self.combo_mode = ctk.CTkOptionMenu(top_row, values=["ALL", "Team 1", "Team 2"], width=80, height=25, command=self.on_mode_change)
        self.combo_mode.set(self.app.config.data.get("current_mode", "ALL"))
        self.combo_mode.pack(side="left", padx=2)
        
        img_dup = self.load_icon("dupliquer.png")
        self.btn_paste = ctk.CTkButton(top_row, text="📋" if not img_dup else "", image=img_dup, width=25, height=25, fg_color="#8e44ad", hover_color="#9b59b6", command=lambda: threading.Thread(target=self.app.logic.execute_paste_enter, daemon=True).start())
        self.btn_paste.pack(side="right", padx=2)
        self.parent_gui.bind_tooltip(self.btn_paste, "Coller + Entrée sur toutes les pages (Ctrl+V)")

        self.btn_refresh_overlay = ctk.CTkButton(top_row, text="F5", font=ctk.CTkFont(size=11, weight="bold"), width=25, height=25, fg_color="#27ae60", hover_color="#2ecc71", command=self.parent_gui.original_app_refresh)
        self.btn_refresh_overlay.pack(side="right", padx=2)
        self.parent_gui.bind_tooltip(self.btn_refresh_overlay, "Rafraîchir les pages Dofus")

        self.bot_row = tk.Frame(content, bg="#1e1e1e")
        self.bot_row.pack(fill="x")

        img_inv = self.load_icon("inventaire.png")  
        img_carac = self.load_icon("carac.png")    
        img_sort = self.load_icon("sort.png")      
        img_havre = self.load_icon("havresac.png")
        img_zaap = self.load_icon("zaap.png")

        self.b1 = ctk.CTkButton(self.bot_row, text="I" if not img_inv else "", image=img_inv, width=28, height=28, fg_color="#2c3e50", hover_color="#e67e22", command=lambda: self.bcast("game_inv_key", "i"))
        self.b1.pack(side="left", padx=2)
        self.parent_gui.bind_tooltip(self.b1, "Ouvrir Inventaire")
        
        self.b2 = ctk.CTkButton(self.bot_row, text="C" if not img_carac else "", image=img_carac, width=28, height=28, fg_color="#2c3e50", hover_color="#9b59b6", command=lambda: self.bcast("game_char_key", "c"))
        self.b2.pack(side="left", padx=2)
        self.parent_gui.bind_tooltip(self.b2, "Ouvrir Caractéristiques")
        
        self.b3 = ctk.CTkButton(self.bot_row, text="S" if not img_sort else "", image=img_sort, width=28, height=28, fg_color="#2c3e50", hover_color="#3498db", command=lambda: self.bcast("game_spell_key", "s"))
        self.b3.pack(side="left", padx=2)
        self.parent_gui.bind_tooltip(self.b3, "Ouvrir Sorts")
        
        self.b4 = ctk.CTkButton(self.bot_row, text="H" if not img_havre else "", image=img_havre, width=28, height=28, fg_color="#2c3e50", hover_color="#2ecc71", command=lambda: self.bcast("game_haven_key", "h"))
        self.b4.pack(side="left", padx=2)
        self.parent_gui.bind_tooltip(self.b4, "Ouvrir Havre-Sac")
        
        self.b5 = ctk.CTkButton(self.bot_row, text="Z" if not img_zaap else "", image=img_zaap, width=28, height=28, fg_color="#2c3e50", hover_color="#f1c40f", command=lambda: threading.Thread(target=self.app.logic.execute_auto_zaap, daemon=True).start())
        self.b5.pack(side="left", padx=2)
        self.parent_gui.bind_tooltip(self.b5, "Auto-Zaap (Ouvre havre-sac et clique le Zaap)")

        self.window.withdraw()

    def bcast(self, config_key, default):
        k = self.app.config.data.get(config_key, default)
        threading.Thread(target=self.app.logic.broadcast_key, args=(k,), daemon=True).start()

    def load_icon(self, filename):
        path = f"skin/{filename}"
        if os.path.exists(path):
            return ctk.CTkImage(light_image=Image.open(path).resize((20, 20), Image.Resampling.LANCZOS), dark_image=Image.open(path).resize((20, 20), Image.Resampling.LANCZOS), size=(20, 20))
        return None

    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    def do_move(self, event):
        self.window.geometry(f"+{self.window.winfo_x() + (event.x - self.x)}+{self.window.winfo_y() + (event.y - self.y)}")
    def stop_move(self, event):
        self.app.config.data["toolbar_x"], self.app.config.data["toolbar_y"] = self.window.winfo_x(), self.window.winfo_y()
        self.app.config.save()
    def on_mode_change(self, choice):
        self.app.logic.set_mode(choice)
        self.app.current_idx = 0
        self.parent_gui.combo_mode.set(choice)
    def show(self): self.window.deiconify()
    def hide(self): self.window.withdraw()


class OrganizerGUI:
    def __init__(self, app_controller):
        self.app = app_controller
        self.root = ctk.CTk()
        self.root.title("Doframe")
        
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = 700
        win_h = min(screen_h - 80, 900) 
        x_pos = int((screen_w / 2) - (win_w / 2))
        y_pos = int((screen_h / 2) - (win_h / 2))
        self.root.geometry(f"{win_w}x{win_h}+{x_pos}+{y_pos}") 
        
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        self.original_app_refresh = self.app.refresh
        
        if os.path.exists("logo.ico"):
            try: self.root.iconbitmap("logo.ico")
            except: pass
                
        self.is_listening = False
        self.is_visible = True 
        cfg = self.app.config.data 
        
        self.toolbar = FloatingToolbar(self.app, self)
        
        self.var_tooltips = ctk.BooleanVar(value=cfg.get("show_tooltips", True))
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes("-topmost", True)
        self.tooltip_lbl = tk.Label(self.tooltip, text="", fg="#ecf0f1", bg="#2c3e50", font=("Segoe UI", 9), padx=6, pady=3, relief="solid", borderwidth=1)
        self.tooltip_lbl.pack()
        self.tooltip.withdraw() 
        
        self.hotkey_btns = {} 
        self.checkbox_vars = {} 

        self.header_f = ctk.CTkFrame(self.root, fg_color="transparent")
        self.header_f.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(self.header_f, text="Doframe", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        
        self.btn_settings = ctk.CTkButton(self.header_f, text="⚙️ Paramètres", fg_color="#34495e", hover_color="#2c3e50", width=120, command=self.open_settings)
        self.btn_settings.pack(side="right")
        self.bind_tooltip(self.btn_settings, "Paramètres du jeu et de la roue")

        self.btn_tuto = ctk.CTkButton(self.header_f, text="🎓 Tuto", fg_color="#8e44ad", hover_color="#9b59b6", width=80, command=self.launch_tutorial)
        self.btn_tuto.pack(side="right", padx=(0, 10))
        self.bind_tooltip(self.btn_tuto, "Voir la vidéo de présentation sur YouTube")

      
        self.btn_kill = ctk.CTkButton(self.header_f, text="🛑 OFF", fg_color="#c0392b", hover_color="#922b21", width=60, command=self.hard_kill_app)
        self.btn_kill.pack(side="right", padx=(0, 10))
        self.bind_tooltip(self.btn_kill, "Shutdown complet : Force la fermeture immédiate de DOFRAME")

        self.frame_mode = ctk.CTkFrame(self.root)
        self.frame_mode.pack(fill="x", padx=15, pady=5)
        
        lbl_ctrl = ctk.CTkLabel(self.frame_mode, text="Contrôler :")
        lbl_ctrl.pack(side="left", padx=10, pady=5)
        
        self.combo_mode = ctk.CTkOptionMenu(self.frame_mode, values=["ALL", "Team 1", "Team 2"], command=self.on_mode_change)
        self.combo_mode.set(cfg.get("current_mode", "ALL"))
        self.combo_mode.pack(side="left", padx=5, pady=5)
        self.bind_tooltip(self.combo_mode, "Cible du focus (Tout le monde ou équipe spécifique)")

        top_container = ctk.CTkFrame(self.root, fg_color="transparent")
        top_container.pack(fill="x", padx=15, pady=5)

        self.frame_keys = ctk.CTkFrame(top_container)
        self.frame_keys.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ctk.CTkLabel(self.frame_keys, text="Raccourcis Clavier", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=6, pady=5)

        self.create_hotkey_row(self.frame_keys, "Précédent", "prev_key", 1, 0, "Focus perso précédent")
        self.create_hotkey_row(self.frame_keys, "Suivant", "next_key", 1, 3, "Focus perso suivant")
        self.create_hotkey_row(self.frame_keys, "Chef", "leader_key", 2, 0, "Reprendre focus sur le Chef")
        self.create_hotkey_row(self.frame_keys, "Clic Multi G.", "sync_key", 2, 3, "Clic gauche synchronisé")
        self.create_hotkey_row(self.frame_keys, "Chasse", "treasure_key", 3, 0, "Copier/Coller auto")
        self.create_hotkey_row(self.frame_keys, "Swap XP", "swap_xp_drop_key", 4, 0, "Clic synchro (XP/Drop)")
        self.create_hotkey_row(self.frame_keys, "Clic Multi D.", "sync_right_key", 3, 3, "Clic droit synchronisé")
        self.create_hotkey_row(self.frame_keys, "Afficher UI", "toggle_app_key", 4, 3, "Masquer/Afficher l'app")

        self.frame_switches = ctk.CTkFrame(top_container)
        self.frame_switches.pack(side="right", fill="both", expand=False, padx=(5, 0))
        ctk.CTkLabel(self.frame_switches, text="Options Globales", font=ctk.CTkFont(weight="bold")).pack(pady=5)

        switch_row2 = ctk.CTkFrame(self.frame_switches, fg_color="transparent")
        switch_row2.pack(fill="x", pady=5)
        self.var_toolbar = ctk.BooleanVar(value=cfg.get("toolbar_active", False))
        self.sw_overlay = ctk.CTkSwitch(switch_row2, text="📌 Overlay", variable=self.var_toolbar, command=self.toggle_toolbar)
        self.sw_overlay.pack(side="left", padx=(15, 5))
        self.bind_tooltip(self.sw_overlay, "Afficher la barre de macros flottante en jeu")
        
        self.var_return = ctk.BooleanVar(value=cfg.get("return_to_leader", True))
        sw_return = ctk.CTkSwitch(switch_row2, text="🔙 Focus Chef", variable=self.var_return, command=self.toggle_return)
        sw_return.pack(side="left", padx=5)
        self.bind_tooltip(sw_return, "Retour automatique sur le chef après une action multi")

        switch_row3 = ctk.CTkFrame(self.frame_switches, fg_color="transparent")
        switch_row3.pack(fill="x", pady=5)
        self.var_spam = ctk.BooleanVar(value=cfg.get("spam_click_active", False))
        sw_spam = ctk.CTkSwitch(switch_row3, text="🖱️ Spam Clic", variable=self.var_spam, command=self.toggle_macros)
        sw_spam.pack(side="left", padx=15)
        self.bind_tooltip(sw_spam, "Maintenez le clic Molette pour spammer les doubles clics")

     
        self.frame_actions_container = ctk.CTkFrame(self.root)
        self.frame_actions_container.pack(fill="x", padx=15, pady=5)
        
       
        ctk.CTkLabel(self.frame_actions_container, text="Actions & Calibrages", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 0))

   
        self.calib_frame = ctk.CTkFrame(self.frame_actions_container, fg_color="transparent")
        self.calib_frame.pack(fill="x", padx=10, pady=5)
        
        btn_calib_chat = ctk.CTkButton(self.calib_frame, text="Calibrer Chat", fg_color="#e67e22", hover_color="#d35400", command=self.start_calib_chat)
        btn_calib_chat.pack(side="left", padx=5, expand=True)
        self.bind_tooltip(btn_calib_chat, "Définir la zone de saisie du chat (Pour Chasse/Invite)")

        btn_calib_xp = ctk.CTkButton(self.calib_frame, text="Calibrer XP/Drop", fg_color="#e67e22", hover_color="#d35400", command=self.start_calib_xp_drop)
        btn_calib_xp.pack(side="left", padx=5, expand=True)
        self.bind_tooltip(btn_calib_xp, "Définir le bouton XP/Drop des challenges")

        btn_calib_zaap = ctk.CTkButton(self.calib_frame, text="Calibrer Havre-Sac", fg_color="#e67e22", hover_color="#d35400", command=self.start_calib_zaap)
        btn_calib_zaap.pack(side="left", padx=5, expand=True)
        self.bind_tooltip(btn_calib_zaap, "Enregistrer la position du Zaap pour chaque personnage")

      
        self.action_frame = ctk.CTkFrame(self.frame_actions_container, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.btn_invite = ctk.CTkButton(self.action_frame, text="Inviter Groupe", fg_color="#8e44ad", hover_color="#9b59b6", command=self.app.logic.execute_group_invite)
        self.btn_invite.pack(side="left", padx=5, expand=True)
        self.bind_tooltip(self.btn_invite, "Auto-invitation de l'équipe via le chat")

        self.btn_close_all = ctk.CTkButton(self.action_frame, text="Fermer Team", fg_color="#c0392b", hover_color="#e74c3c", command=self.close_all_and_refresh)
        self.btn_close_all.pack(side="left", padx=5, expand=True)
        self.bind_tooltip(self.btn_close_all, "Kill instantané de toutes les fenêtres Dofus actives")
        
        btn_reset = ctk.CTkButton(self.action_frame, text="Reset Settings", fg_color="#7f8c8d", hover_color="#95a5a6", command=self.reset_all)
        btn_reset.pack(side="left", padx=5, expand=True)
        self.bind_tooltip(btn_reset, "Remise à zéro de tous les paramètres et raccourcis")

        frame_audio = ctk.CTkFrame(self.root, fg_color="transparent")
        frame_audio.pack(fill="x", padx=15, pady=0)
        lbl_vol = ctk.CTkLabel(frame_audio, text="🔊 Volume Roulette :")
        lbl_vol.pack(side="left", padx=10)
        self.slider_volume = ctk.CTkSlider(frame_audio, from_=0, to=100, command=self.on_volume_change, width=150)
        self.slider_volume.set(cfg.get("volume_level", 50))
        self.slider_volume.pack(side="left", padx=10, pady=10)

     
        self.frame_footer = ctk.CTkFrame(self.root, fg_color="transparent")
        self.frame_footer.pack(side="bottom", fill="x", padx=15, pady=(0, 15))

     
        frame_left = ctk.CTkFrame(self.root)
        frame_left.pack(fill="both", expand=True, padx=15, pady=5)


        pill_frame = ctk.CTkFrame(frame_left, fg_color="#3b4252", corner_radius=8)
        pill_frame.pack(fill="x", padx=5, pady=(5, 10), ipadx=5, ipady=2)


        lbl_accounts = ctk.CTkLabel(pill_frame, text="Comptes actifs", font=ctk.CTkFont(size=13, weight="normal"), text_color="#ecf0f1")
        lbl_accounts.pack(side="left", padx=10, pady=4)


        btn_manage_binds = ctk.CTkButton(pill_frame, text="⚙️", width=28, height=28, 
                                        fg_color="#2c3e50", hover_color="#1a252f", corner_radius=6,
                                        command=self.open_bind_manager)
        btn_manage_binds.pack(side="right", padx=5, pady=4)
        self.bind_tooltip(btn_manage_binds, "Gérer les raccourcis avancés par personnage")


        
        self.scroll_frame = ctk.CTkScrollableFrame(frame_left, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
       
        
        self.btn_refresh = ctk.CTkButton(self.frame_footer, text="Rafraîchir", command=self.original_app_refresh, width=80)
        self.btn_refresh.pack(side="left")
        self.bind_tooltip(self.btn_refresh, "Actualiser la liste des comptes")

        self.btn_sort_win = ctk.CTkButton(self.frame_footer, text="Trier Barre Windows", fg_color="#8e44ad", command=self.trigger_sort_taskbar, width=120)
        self.btn_sort_win.pack(side="left", padx=5)
        self.bind_tooltip(self.btn_sort_win, "Organise les fenêtres dans la barre des tâches selon l'initiative")
        
        self.chk_tooltips = ctk.CTkCheckBox(self.frame_footer, text="Bulles", variable=self.var_tooltips, command=self.toggle_tooltips_setting, width=60)
        self.chk_tooltips.pack(side="left", padx=15)
        
        self.btn_hide = ctk.CTkButton(self.frame_footer, text="Cacher l'UI", command=self.toggle_visibility, fg_color="transparent", border_width=1, width=70)
        self.btn_hide.pack(side="right")

        frame_msg = ctk.CTkFrame(self.root, fg_color="transparent", height=20)
        frame_msg.pack(fill="x", padx=15, pady=(0, 5))
        self.lbl_feedback = ctk.CTkLabel(frame_msg, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_feedback.pack(expand=True)
        
        self.skin_cache = {} 
        
        if self.var_toolbar.get(): self.toolbar.show()

    def hard_kill_app(self):
        """ Force la fermeture immédiate de tout l'arbre de processus de DOFRAME """
        my_pid = os.getpid()
        os.system(f"taskkill /F /PID {my_pid} /T")

    def launch_tutorial(self):
        if not self.app.config.data.get("tutorial_done", False):
            self.app.config.data["tutorial_done"] = True
            self.app.config.save()
            
        rep = messagebox.askyesno(
            "Pas de tutoriel intégré pour le moment",
            "Le créateur de Doframe s'est fait shutdown par Ankama, mais aussi sa vidéo, donc pour le moment il n'y pas de tutoriel."
        )
        if rep:
            webbrowser.open("https://buymeacoffee.com/luframe")

    def open_bind_manager(self):
        """ Ouvre la fenêtre de gestion avancée des binds """
        CharManagerWindow(self) 

    def open_settings(self):
        if not hasattr(self, 'settings_window') or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
        else:
            self.settings_window.deiconify()
            self.settings_window.lift()
            self.settings_window.focus_force()

    def show_temporary_message(self, text, color="#2ecc71"):
        self.lbl_feedback.configure(text=text, text_color=color)
        if hasattr(self, "feedback_timer"):
            self.root.after_cancel(self.feedback_timer)
        self.feedback_timer = self.root.after(2500, lambda: self.lbl_feedback.configure(text=""))

    def change_position(self, name, new_val_str):
        new_index = int(new_val_str) - 1
        self.app.logic.set_account_position(name, new_index)
        self.original_app_refresh()

    def move_row(self, name, direction):
        self.app.logic.move_account(name, direction)
        self.original_app_refresh()

    def trigger_sort_taskbar(self):
        self.app.logic.sort_taskbar()
        self.show_temporary_message("🚀 Les pages ont été rangées avec succès !", "#9b59b6")

    def close_and_refresh(self, name):
        self.app.logic.close_account_window(name)
        time.sleep(0.5) 
        self.original_app_refresh()
        
    def close_all_and_refresh(self):
        self.app.logic.close_all_active_accounts()
        time.sleep(0.5)
        self.original_app_refresh()
        self.show_temporary_message("💥 La team a été fermée !", "#e74c3c")

    def toggle_tooltips_setting(self):
        self.app.config.data["show_tooltips"] = self.var_tooltips.get()
        self.app.config.save()
        if not self.var_tooltips.get():
            self.tooltip.withdraw()

    def show_gui(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.is_visible = True

    def hide_to_tray(self):
        self.root.withdraw()
        self.is_visible = False

    def toggle_visibility(self):
        if self.is_visible:
            self.hide_to_tray()
        else:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force() 
            self.is_visible = True
            
    def toggle_macros(self):
        self.app.config.data["spam_click_active"] = self.var_spam.get() 
        self.app.config.save()

    def toggle_toolbar(self):
        state = self.var_toolbar.get()
        self.app.config.data["toolbar_active"] = state
        self.app.config.save()
        if state: self.toolbar.show()
        else: self.toolbar.hide()

    def toggle_return(self):
        self.app.config.data["return_to_leader"] = self.var_return.get()
        self.app.config.save()

    def on_mode_change(self, choice):
        self.app.logic.set_mode(choice)
        self.app.current_idx = 0
        self.toolbar.combo_mode.set(choice)
        self.app.setup_hotkeys()

    def get_class_image(self, class_name):
        if class_name in self.skin_cache: return self.skin_cache[class_name]
        path = f"skin/{class_name}.png"
        if not os.path.exists(path): return None
        img = ctk.CTkImage(light_image=Image.open(path), dark_image=Image.open(path), size=(24, 24))
        self.skin_cache[class_name] = img
        return img

    def set_leader(self, name):
        self.app.logic.set_leader(name)
        self.original_app_refresh()

    def reset_all(self):
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir tout réinitialiser ?\n\nToutes vos touches seront perdues."):
            self.app.config.reset_settings()
            self.original_app_refresh()

    def show_tooltip(self, text):
        self.tooltip_lbl.config(text=text)
        self.tooltip.deiconify()
        self.tooltip.attributes("-topmost", True)
        self.tooltip.lift()
        self.update_tooltip_pos()

    def update_tooltip_pos(self):
        if self.is_listening:
            x, y = win32api.GetCursorPos()
            self.tooltip.geometry(f"+{x + 20}+{y + 20}")
            self.tooltip.lift()
            self.root.after(10, self.update_tooltip_pos)
        else:
            self.tooltip.withdraw()

    def bind_tooltip(self, widget, text):
        def on_enter(event):
            if self.is_listening or not self.app.config.data.get("show_tooltips", True): return 
            self.tooltip_lbl.config(text=text)
            self.tooltip.deiconify()
            self.tooltip.attributes("-topmost", True)
            self.tooltip.lift()
            x, y = win32api.GetCursorPos()
            self.tooltip.geometry(f"+{x + 15}+{y + 15}")
        def on_leave(event):
            if not self.is_listening: self.tooltip.withdraw()
        def on_motion(event):
            if self.is_listening or not self.app.config.data.get("show_tooltips", True): return
            x, y = win32api.GetCursorPos()
            self.tooltip.geometry(f"+{x + 15}+{y + 15}")

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.bind("<Motion>", on_motion)

    def toggle_team_ui(self, name, btn):
        current_team = self.app.config.data.get("accounts_team", {}).get(name, "Team 1")
        new_team = "Team 2" if current_team == "Team 1" else "Team 1"
        self.app.logic.change_team(name, new_team)
        team_color = "#2980b9" if new_team == "Team 1" else "#c0392b"
        team_hover = "#1f6391" if new_team == "Team 1" else "#922b21" 
        if btn: btn.configure(text="T1" if new_team == "Team 1" else "T2", fg_color=team_color, hover_color=team_hover)

    def refresh_list(self, accounts):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        leader_name = self.app.config.data.get("leader_name", "")
        
        def make_toggle_cmd(n, v_obj):
            return lambda: self.app.logic.toggle_account(n, v_obj.get())
        
        for idx, acc in enumerate(accounts):
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            img = self.get_class_image(acc.get('classe', 'Inconnu'))
            if img: ctk.CTkLabel(row_frame, image=img, text="").pack(side="left", padx=5)
            else: ctk.CTkLabel(row_frame, text="👤").pack(side="left", padx=5) 
            
            var = tk.BooleanVar(value=acc['active'])
            self.checkbox_vars[acc['name']] = var 
            
            chk = ctk.CTkCheckBox(row_frame, text=acc['name'][:20], width=160)
            if acc['active']:
                chk.select()
            else:
                chk.deselect()
                
            chk.configure(command=lambda n=acc['name'], c=chk: self.app.logic.toggle_account(n, bool(c.get())))
            chk.pack(side="left", padx=(5, 0))

            btn_close = ctk.CTkButton(row_frame, text="✖", width=25, fg_color="#c0392b", hover_color="#e74c3c", command=lambda n=acc['name']: self.close_and_refresh(n))
            btn_close.pack(side="right", padx=(2, 5))
            self.bind_tooltip(btn_close, "Fermer la fenêtre")
            
            is_leader = (acc['name'] == leader_name)
            leader_txt = "🌟" if is_leader else "☆"
            leader_color = "#f39c12" if is_leader else "transparent"
            btn_lead = ctk.CTkButton(row_frame, text=leader_txt, width=35, fg_color=leader_color, border_width=1, command=lambda n=acc['name']: self.set_leader(n))
            btn_lead.pack(side="right", padx=2)
            self.bind_tooltip(btn_lead, "Définir comme Chef")

            team_val = acc.get('team', "Team 1")
            team_color = "#2980b9" if team_val == "Team 1" else "#c0392b"
            team_hover = "#1f6391" if team_val == "Team 1" else "#922b21" 
            
            btn_team = ctk.CTkButton(row_frame, text="T1" if team_val == "Team 1" else "T2", width=35, fg_color=team_color, hover_color=team_hover)
            btn_team.configure(command=lambda n=acc['name'], b=btn_team: self.toggle_team_ui(n, b))
            btn_team.pack(side="right", padx=5)
            self.bind_tooltip(btn_team, "Changer l'équipe")

            btn_down = ctk.CTkButton(row_frame, text="▼", width=25, fg_color="#34495e", command=lambda n=acc['name']: self.move_row(n, 1))
            btn_down.pack(side="right", padx=(2, 10))
            self.bind_tooltip(btn_down, "Descendre")
            
            btn_up = ctk.CTkButton(row_frame, text="▲", width=25, fg_color="#34495e", command=lambda n=acc['name']: self.move_row(n, -1))
            btn_up.pack(side="right", padx=2)
            self.bind_tooltip(btn_up, "Monter")

            pos_values = [str(i+1) for i in range(len(accounts))]
            current_pos = str(idx + 1)
            combo_pos = ctk.CTkOptionMenu(row_frame, values=pos_values, width=50, height=24, fg_color="#34495e", command=lambda val, n=acc['name']: self.change_position(n, val))
            combo_pos.set(current_pos)
            combo_pos.pack(side="right", padx=(2, 5))
            self.bind_tooltip(combo_pos, "Position exacte")

    def on_volume_change(self, value): 
        self.app.update_volume(int(value))
    
    def create_hotkey_row(self, parent, label_text, config_key, row, col_offset, tooltip_txt=""):
        lbl = ctk.CTkLabel(parent, text=f"{label_text}:")
        lbl.grid(row=row, column=col_offset, padx=5, sticky="w")
        if tooltip_txt: self.bind_tooltip(lbl, tooltip_txt)
        
        current_val = self.app.config.data.get(config_key, "")
        btn = ctk.CTkButton(parent, text=current_val if current_val else "Aucun", width=80, 
                            command=lambda: self.catch_key(config_key, btn, allow_mouse=True))
        btn.grid(row=row, column=col_offset+1, padx=2, pady=2)
        
        self.hotkey_btns[config_key] = btn 
        
        btn_x = ctk.CTkButton(parent, text="✖", width=25, fg_color="#c0392b", hover_color="#e74c3c", command=lambda: self.clear_key(config_key, btn))
        btn_x.grid(row=row, column=col_offset+2, padx=(0, 10))
        self.bind_tooltip(btn_x, "Effacer le raccourci")

    def catch_key(self, config_key, btn, allow_mouse=False):
        if self.is_listening: return 
        self.is_listening = True
        btn.configure(text="...", fg_color="#f39c12")
        threading.Thread(target=self._listen_hotkey_thread, args=(config_key, btn, allow_mouse), daemon=True).start()

    def _listen_hotkey_thread(self, config_key, btn, allow_mouse):
        captured_key = None
        captured_mods = []
        
        while win32api.GetAsyncKeyState(win32con.VK_LBUTTON) < 0 or win32api.GetAsyncKeyState(win32con.VK_RBUTTON) < 0 or win32api.GetAsyncKeyState(win32con.VK_MBUTTON) < 0:
            time.sleep(0.01)
        time.sleep(0.1) 
        
        def get_current_mods():
            mods = []
            if win32api.GetAsyncKeyState(win32con.VK_CONTROL) < 0: mods.append("ctrl")
            if win32api.GetAsyncKeyState(win32con.VK_MENU) < 0: mods.append("alt")
            if win32api.GetAsyncKeyState(win32con.VK_SHIFT) < 0: mods.append("shift")
            return mods

        if not allow_mouse:
            while True:
                event = keyboard.read_event(suppress=True)
                if event.event_type == keyboard.KEY_DOWN:
                    if event.name not in ['alt', 'ctrl', 'shift', 'maj', 'right alt', 'right ctrl', 'left alt', 'left ctrl', 'menu', 'windows', 'cmd']:
                        captured_mods = get_current_mods()
                        
                        if event.scan_code in SCAN_TO_AZERTY:
                            captured_key = SCAN_TO_AZERTY[event.scan_code]
                        else:
                            captured_key = event.name
                        break
        else:
            def on_key(e):
                nonlocal captured_key, captured_mods
                if e.event_type == keyboard.KEY_DOWN:
                    if e.name not in ['alt', 'ctrl', 'shift', 'maj', 'right alt', 'right ctrl', 'left alt', 'left ctrl', 'menu']:
                        captured_mods = get_current_mods()
                        if e.scan_code in SCAN_TO_AZERTY:
                            captured_key = SCAN_TO_AZERTY[e.scan_code]
                        else:
                            captured_key = e.name
            hook = keyboard.hook(on_key, suppress=True)
            
            while not captured_key:
                if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) < 0: captured_key = "left_click"
                elif win32api.GetAsyncKeyState(win32con.VK_RBUTTON) < 0: captured_key = "right_click"
                elif win32api.GetAsyncKeyState(win32con.VK_MBUTTON) < 0: captured_key = "middle_click"
                elif win32api.GetAsyncKeyState(0x05) < 0: captured_key = "mouse4" 
                elif win32api.GetAsyncKeyState(0x06) < 0: captured_key = "mouse5"
                
                if captured_key:
                    captured_mods = get_current_mods()
                    break
                time.sleep(0.01)
                
            keyboard.unhook(hook)

        if captured_key == "esc":
            final_key = self.app.config.data.get(config_key, "")
        else:
            final_key = "+".join(captured_mods) + "+" + captured_key if captured_mods else captured_key

        time.sleep(0.5)


        self.root.after(0, self.apply_single_hotkey, config_key, final_key, btn)

    def release_modifiers(self):
       
        try:
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        except: pass

    def apply_single_hotkey(self, config_key, new_value, btn):
        self.release_modifiers()
        
        if new_value: 
            for k in list(self.app.config.data.keys()):
                if (k.endswith("_key") or k.endswith("_hotkey")) and k != config_key:
                    if self.app.config.data[k] == new_value:
                        self.app.config.data[k] = ""
                        if k in self.hotkey_btns:
                            self.hotkey_btns[k].configure(text="Aucun", fg_color=["#3a7ebf", "#1f538d"])

        self.app.config.data[config_key] = new_value
        self.app.config.save()
        
        btn.configure(text=new_value if new_value else "Aucun", fg_color=["#3a7ebf", "#1f538d"])
        self.app.setup_hotkeys()
        self.is_listening = False

    def clear_key(self, config_key, btn):
        if self.is_listening: return
        self.apply_single_hotkey(config_key, "", btn)

    def wait_for_calib_or_esc(self):
       
        calib_key = self.app.config.data.get("calib_key", "f4").lower()
        if not calib_key: calib_key = "f4"
        
        while True:
            event = keyboard.read_event(suppress=True)
            if event.event_type == keyboard.KEY_DOWN:
                if event.name == calib_key: return True
                elif event.name == 'esc': return False

    def start_calib_chat(self):
        if self.is_listening: return
        self.is_listening = True
        self.root.withdraw() 
        if self.app.logic.leader_hwnd: 
            self.app.logic.focus_window(self.app.logic.leader_hwnd)
            time.sleep(0.2) 
        threading.Thread(target=self.calibration_chat_sequence, daemon=True).start()
        k = self.app.config.data.get("calib_key", "F4").upper()
        self.show_tooltip(f"Cliquez dans votre chat dofus pour envoyer un message, puis appuyez sur {k} sur la position.\n(Echap pour annuler)")

    def calibration_chat_sequence(self):
        if self.wait_for_calib_or_esc():
            rx, ry = self.app.logic.get_relative_ratio_pos(self.app.logic.leader_hwnd)
            self.app.config.data["macro_positions"]["chat_position"] = [rx, ry]
            self.app.config.save()
            self.root.after(0, lambda: self.show_temporary_message("✅ Chat calibré !", "#2ecc71"))
        self.is_listening = False
        self.root.after(0, self.tooltip.withdraw)
        self.root.after(0, self.show_gui) 

    def start_calib_xp_drop(self):
        if self.is_listening: return
        self.is_listening = True
        self.root.withdraw() 
        if self.app.logic.leader_hwnd: 
            self.app.logic.focus_window(self.app.logic.leader_hwnd)
            time.sleep(0.2)
        threading.Thread(target=self.calibration_xp_drop_sequence, daemon=True).start()
        k = self.app.config.data.get("calib_key", "F4").upper()
        self.show_tooltip(f"Lancez un combat, placez votre souris sur le bouton XP/Drop de fin de combat, puis appuyez sur {k}.\n(Echap pour annuler)")

    def calibration_xp_drop_sequence(self):
        if self.wait_for_calib_or_esc():
            rx, ry = self.app.logic.get_relative_ratio_pos(self.app.logic.leader_hwnd)
            self.app.config.data["macro_positions"]["xp_drop_button"] = [rx, ry]
            self.app.config.save()
            self.root.after(0, lambda: self.show_temporary_message("✅ XP/Drop calibré !", "#2ecc71"))
        self.is_listening = False
        self.root.after(0, self.tooltip.withdraw)
        self.root.after(0, self.show_gui) 

    def start_calib_zaap(self):
        if self.is_listening: return
        active_accounts = self.app.logic.get_cycle_list()
        if not active_accounts: return
        self.is_listening = True
        self.root.withdraw() 
        threading.Thread(target=self.calibration_zaap_sequence, args=(active_accounts,), daemon=True).start()

    def calibration_zaap_sequence(self, active_accounts):
        self.app.config.data["macro_positions"]["zaaps"] = {}
        success = True
        k = self.app.config.data.get("calib_key", "F4").upper()
        
        for acc in active_accounts:
            self.app.logic.focus_window(acc['hwnd'])
            time.sleep(0.2) 
            self.root.after(0, lambda a=acc: self.show_tooltip(f"Allez dans le havre-sac de {a['name']}, placez votre souris sur le haut du Zaap, puis appuyez sur {k}.\n(Echap pour annuler)"))
            
            if not self.wait_for_calib_or_esc():
                self.root.after(0, lambda: self.show_temporary_message("❌ Calibration Zaap annulée.", "#e74c3c"))
                success = False
                break
                
            rx, ry = self.app.logic.get_relative_ratio_pos(acc['hwnd'])
            self.app.config.data["macro_positions"]["zaaps"][acc['name']] = [rx, ry]
            self.root.after(0, lambda a=acc: self.show_temporary_message(f"✅ Zaap de {a['name']} calibré !", "#2ecc71"))
        
        if success:
            self.app.config.save()
            self.root.after(0, lambda: self.show_temporary_message("✅ Calibration Zaap totale terminée !", "#2ecc71"))
            
        self.is_listening = False
        self.root.after(0, self.tooltip.withdraw)
        self.root.after(0, self.show_gui)

    def run(self): self.root.mainloop()

class CharManagerWindow(ctk.CTkToplevel):
    def __init__(self, parent_gui):
        super().__init__(parent_gui.root)
        self.parent = parent_gui
        self.app = parent_gui.app
        self.title("⚙️ Gestionnaire de Binds Avancé DOFRAME")
        self.geometry("620x680")
        self.attributes("-topmost", True)
        self.grab_set() 
        
        self.update_idletasks()
        x = parent_gui.root.winfo_x() + (parent_gui.root.winfo_width() // 2) - (620 // 2)
        y = parent_gui.root.winfo_y() + (parent_gui.root.winfo_height() // 2) - (680 // 2)
        self.geometry(f"+{x}+{y}")

        title_font = ctk.CTkFont(size=18, weight="bold")
        sub_font = ctk.CTkFont(size=14, slant="italic")
        
        frame_header = ctk.CTkFrame(self)
        frame_header.pack(fill="x", padx=15, pady=15)
        
        
        frame_mode = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_mode.pack(fill="x", pady=5)
        ctk.CTkLabel(frame_mode, text="Mode :", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15)
        self.var_mode = ctk.StringVar(value=self.app.config.data.get("advanced_bind_mode", "cycle"))
        seg_mode = ctk.CTkSegmentedButton(frame_mode, values=["cycle", "bind"], variable=self.var_mode, command=self.on_mode_change)
        seg_mode.pack(side="left", padx=5)

       
        frame_prefix = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_prefix.pack(fill="x", pady=5)
        ctk.CTkLabel(frame_prefix, text="Préfixe Global :", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15)
        self.var_mod = ctk.StringVar(value=self.app.config.data.get("advanced_bind_modifier", "ctrl"))
        seg_mod = ctk.CTkSegmentedButton(frame_prefix, values=["aucun", "ctrl", "alt", "shift"], variable=self.var_mod)
        seg_mod.pack(side="left", padx=5)
        
       
        self.frame_desc = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_desc.pack(fill="x", padx=20)
        self.lbl_desc = ctk.CTkLabel(self.frame_desc, text="", font=sub_font, justify="center")
        self.lbl_desc.pack()
        
        self.scroll_list = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.entry_dict = {} 
        self.buttons_dict = {} 

        btn_save = ctk.CTkButton(self, text="💾 Enregistrer les raccourcis", fg_color="#27ae60", hover_color="#2ecc71", command=self.save_all)
        btn_save.pack(pady=20)

        self.update_content()

    def on_mode_change(self, value):
        self.app.config.data["advanced_bind_mode"] = value
        self.app.config.save()
        self.update_content()
        self.app.setup_hotkeys()

    def get_base_key(self, bind_str):
       
        if not bind_str: return ""
        return bind_str.split('+')[-1]

    def catch_key(self, dict_key, btn):
        
        if self.parent.is_listening: return
        self.parent.is_listening = True
        btn.configure(text="...", fg_color="#f39c12")
        threading.Thread(target=self._listen_thread, args=(dict_key, btn), daemon=True).start()

    def _listen_thread(self, dict_key, btn):
        captured = ""
        
        def on_key(e):
            nonlocal captured
            if e.event_type == keyboard.KEY_DOWN:
                if e.name not in ['alt', 'ctrl', 'shift', 'maj', 'right alt', 'right ctrl', 'left alt', 'left ctrl', 'menu', 'windows', 'cmd']:
                    captured = e.name

        hook = keyboard.hook(on_key, suppress=True)
        
        while not captured:
            if win32api.GetAsyncKeyState(0x05) < 0: captured = "mouse4"
            elif win32api.GetAsyncKeyState(0x06) < 0: captured = "mouse5"
            elif win32api.GetAsyncKeyState(0x04) < 0: captured = "middle_click"
            time.sleep(0.01)
            
        keyboard.unhook(hook)
        
        time.sleep(0.3)
        
        
        self.app.gui.root.after(0, self.apply_key, dict_key, captured, btn)

    def apply_key(self, dict_key, key_name, btn):
        self.parent.release_modifiers()
        if key_name == "esc": key_name = ""
        
        self.entry_dict[dict_key] = key_name
        btn.configure(text=key_name.upper() if key_name else "Aucun", fg_color=["#3a7ebf", "#1f538d"])
        self.parent.is_listening = False

    def update_content(self):
        for widget in self.scroll_list.winfo_children(): widget.destroy()
        self.entry_dict = {}
        self.buttons_dict = {}
        
        mode = self.var_mode.get()
        active_list = self.app.logic.get_cycle_list()
        cfg = self.app.config.data

        if mode == "cycle":
            self.lbl_desc.configure(text="Target immuable par place. (ex: Ligne 1 focus le 1er de l'initiative)")
            row_binds = cfg.get("cycle_row_binds", [])
            
            for i in range(8):
                frame_row = ctk.CTkFrame(self.scroll_list)
                frame_row.pack(fill="x", pady=2, padx=5)
                
                current_pseudo = active_list[i]['name'] if i < len(active_list) else "---"
                ctk.CTkLabel(frame_row, text=f"Place n°{i+1}", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15, pady=10)
                ctk.CTkLabel(frame_row, text=f"({current_pseudo})", font=ctk.CTkFont(slant="italic")).pack(side="left", padx=5)
                
                try: full_bind = row_binds[i]
                except: full_bind = ""
                base_key = self.get_base_key(full_bind)
                self.entry_dict[i] = base_key
                
                btn = ctk.CTkButton(frame_row, text=base_key.upper() if base_key else "Aucun", width=80)
                btn.configure(command=lambda k=i, b=btn: self.catch_key(k, b))
                btn.pack(side="right", padx=15, pady=10)
                
                btn_clear = ctk.CTkButton(frame_row, text="✖", width=25, fg_color="#c0392b", hover_color="#e74c3c", command=lambda k=i, b=btn: self.apply_key(k, "esc", b))
                btn_clear.pack(side="right", padx=5)

        elif mode == "bind":
            self.lbl_desc.configure(text="Target fixe par pseudo (Même s'ils changent d'ordre)")
            char_binds = cfg.get("persistent_character_binds", {})
            
            if not active_list:
                ctk.CTkLabel(self.scroll_list, text="Aucun personnage connecté détecté.", text_color="#e74c3c").pack(pady=50)
                return

            for acc in active_list:
                pseudo = acc['name']
                frame_row = ctk.CTkFrame(self.scroll_list)
                frame_row.pack(fill="x", pady=2, padx=5)
                
                img = self.parent.get_class_image(acc.get('classe', 'Inconnu'))
                if img: ctk.CTkLabel(frame_row, text="", image=img).pack(side="left", padx=10, pady=5)
                
                ctk.CTkLabel(frame_row, text=pseudo, font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=5)
                
                full_bind = char_binds.get(pseudo, "")
                base_key = self.get_base_key(full_bind)
                self.entry_dict[pseudo] = base_key
                
                btn = ctk.CTkButton(frame_row, text=base_key.upper() if base_key else "Aucun", width=80)
                btn.configure(command=lambda k=pseudo, b=btn: self.catch_key(k, b))
                btn.pack(side="right", padx=15, pady=10)
                
                btn_clear = ctk.CTkButton(frame_row, text="✖", width=25, fg_color="#c0392b", hover_color="#e74c3c", command=lambda k=pseudo, b=btn: self.apply_key(k, "esc", b))
                btn_clear.pack(side="right", padx=5)

    def save_all(self):
        mode = self.var_mode.get()
        mod_prefix = self.var_mod.get()
        prefix_str = f"{mod_prefix}+" if mod_prefix != "aucun" else ""
        
        cfg = self.app.config.data
        cfg["advanced_bind_modifier"] = mod_prefix 
        
        if mode == "cycle":
            new_binds = []
            for i in range(8):
                base = self.entry_dict.get(i, "").lower().strip()
                new_binds.append(prefix_str + base if base else "")
            cfg["cycle_row_binds"] = new_binds

        elif mode == "bind":
            for pseudo, base in self.entry_dict.items():
                base = base.lower().strip()
                cfg["persistent_character_binds"][pseudo] = prefix_str + base if base else ""
            
        self.app.config.save()
        self.parent.show_temporary_message("✅ Raccourcis enregistrés avec succès !", "#2ecc71")
        self.app.setup_hotkeys() 
        self.destroy()
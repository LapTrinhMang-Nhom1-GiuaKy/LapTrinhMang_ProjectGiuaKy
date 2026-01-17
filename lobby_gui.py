import customtkinter as ctk
from tkinter import messagebox

# Theme matching login_gui
_BG = "#071020"
_ACCENT = "#00f5ff"
_LIST_BG = "#0f1724"
_BTN_BG = "#00d4ff"
_BTN_FG = "#041017"

class LobbyWindow(ctk.CTkToplevel):
    def __init__(self, player_name, master=None, on_invite_callback=None):
        super().__init__(master)
        self.player_name = player_name
        self.on_invite = on_invite_callback
        
        self.title(f"Sảnh Chờ - {player_name}")
        self.geometry("400x500")
        self.configure(bg=_BG)
        # Prevent closing directly to keep connection alive? 
        # Or better: closing this exits the app.
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Header
        self.lbl_title = ctk.CTkLabel(self, text=f"Xin chào, {player_name}!", 
                                      font=("Helvetica", 16, "bold"), text_color=_ACCENT)
        self.lbl_title.pack(pady=10)

        self.lbl_status = ctk.CTkLabel(self, text="Danh sách người chơi online:", 
                                       font=("Helvetica", 12), text_color="white")
        self.lbl_status.pack(pady=(0, 5))

        # List Frame (Scrollable)
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=_LIST_BG, width=350, height=350)
        self.scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.player_widgets = {} # name -> widget

        # Refresh Button
        self.btn_refresh = ctk.CTkButton(self, text="Làm mới", width=100, command=lambda: self.master.event_generate("<<RefreshLobby>>"))
        self.btn_refresh.pack(pady=5)

        self.focus_force()

    def update_list(self, lobby_data_str):
        """
        lobby_data_str format: "Name1:IDLE,Name2:BUSY,..."
        """
        # Clear old widgets
        for w in self.player_widgets.values():
            w.destroy()
        self.player_widgets.clear()

        if not lobby_data_str:
            return

        players = lobby_data_str.split(",")
        for p in players:
            if ":" not in p: continue
            name, status = p.split(":", 1)
            
            # Don't show myself or show differently?
            if name == self.player_name:
                display_text = f"{name} (Bạn)"
                color = "#aaaaaa"
                state = "disabled"
            else:
                display_text = f"{name}"
                color = "white"
                state = "normal"

            # Frame for each row
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            # Name Label
            lbl = ctk.CTkLabel(row_frame, text=display_text, font=("Helvetica", 13), text_color=color, anchor="w")
            lbl.pack(side="left", padx=10)

            # Status Button/Label
            if status == "IDLE":
                status_text = "Mời chơi"
                status_color = "#00ff00" # Green
                btn_state = "normal" if state == "normal" else "disabled"
                fg_color = _BTN_BG
            else:
                status_text = "Đang bận"
                status_color = "#ff0000" # Red
                btn_state = "disabled"
                fg_color = "#555555"

            if name != self.player_name:
                btn = ctk.CTkButton(row_frame, text=status_text, width=80, height=24,
                                    fg_color=fg_color, state=btn_state,
                                    command=lambda n=name: self.invite_click(n))
                btn.pack(side="right", padx=5)
            else:
                # Just show status for self
                lbl_st = ctk.CTkLabel(row_frame, text=status, text_color="#aaaaaa")
                lbl_st.pack(side="right", padx=10)

            self.player_widgets[name] = row_frame

    def invite_click(self, target_name):
        if self.on_invite:
            self.on_invite(target_name)

    def on_close(self):
        if messagebox.askokcancel("Thoát", "Bạn có muốn thoát game không?"):
            self.master.destroy() # Close root -> closes everything
            import sys; sys.exit(0)

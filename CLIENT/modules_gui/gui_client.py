"""
GUI Frontend for Client: two-step flow (Enter -> get key -> paste key -> Login)
Now: encryption key is shown ONLY in console, NOT auto-pasted.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
from client3 import connect_to_server, enter_credentials, confirm_key_and_activate, receive_alerts

class GUIClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Real-Time Alert Monitoring System - Client")
        self.geometry("900x650")
        self.resizable(True, True)
        self.state("zoomed")

        self.client_socket = None
        self.is_connected = False

        self.create_widgets()
        self.configure_tags()

    def create_widgets(self):
        tk.Label(self, text="Client Login", font=("Arial", 16, "bold")).pack(pady=10)

        tk.Label(self, text="Username").pack()
        self.entry_username = tk.Entry(self, width=30)
        self.entry_username.pack(pady=5)
        self.entry_username.bind("<Return>", lambda e: self.entry_password.focus())

        tk.Label(self, text="Password").pack()
        self.entry_password = tk.Entry(self, show="*", width=30)
        self.entry_password.pack(pady=5)

        tk.Label(self, text="Encryption Key (paste here after pressing Enter)").pack()
        self.entry_key = tk.Entry(self, width=50)
        self.entry_key.pack(pady=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        self.btn_enter = tk.Button(button_frame, text="Enter", command=self.enter_credentials)
        self.btn_enter.pack(side="left", padx=10)

        self.btn_login = tk.Button(button_frame, text="Login", command=self.attempt_login, state="disabled")
        self.btn_login.pack(side="left", padx=10)

        self.btn_kill = tk.Button(button_frame, text="Kill Connection", command=self.kill_connection,
                                  state="disabled", bg="#cc0000", fg="white")
        self.btn_kill.pack(side="left", padx=10)

        tk.Label(self, text="Client Console").pack(pady=5)
        self.console = scrolledtext.ScrolledText(self, width=90, height=20, state='disabled', wrap=tk.WORD)
        self.console.pack(pady=5)

    def configure_tags(self):
        self.console.tag_config("high", foreground="red", font=("Arial", 10, "bold"))
        self.console.tag_config("medium", foreground="orange", font=("Arial", 10))
        self.console.tag_config("low", foreground="green", font=("Arial", 10))
        self.console.tag_config("info", foreground="blue", font=("Arial", 10, "italic"))
        self.console.tag_config("error", foreground="red", font=("Arial", 10, "italic"))

    def append(self, message, tag="info"):
        self.console.configure(state='normal')
        self.console.insert(tk.END, message + "\n", tag)
        self.console.configure(state='disabled')
        self.console.yview(tk.END)

    # -------- First button: send credentials, receive key --------
    def enter_credentials(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        if not username or not password:
            messagebox.showwarning("Input Error", "Username and password required!")
            return
        threading.Thread(target=self._enter_thread, args=(username, password), daemon=True).start()

    def _enter_thread(self, username, password):
        try:
            # connect to server
            self.client_socket = connect_to_server()
            self.append("Connected to server.", "info")

            success, payload = enter_credentials(self.client_socket, username, password)
            if not success:
                self.append(payload, "error")
                try:
                    self.client_socket.close()
                except Exception:
                    pass
                self.client_socket = None
                return

            # payload is the key
            key_str = payload
            self.append("Encryption key received from server. Copy and paste it in the Encryption Field to continue.", "info")
            self.append(f"🔑 {key_str}", "info")

            # ✅ Manual entry only: do NOT auto-fill the key field
            # self.entry_key.delete(0, tk.END)
            # self.entry_key.insert(0, key_str)

            # Enable login button (user will paste key manually)
            self.btn_login.config(state="normal")

        except Exception as e:
            self.append(f"Error during Enter: {e}", "error")
            if self.client_socket:
                try:
                    self.client_socket.close()
                except Exception:
                    pass
                self.client_socket = None

    # -------- Second button: confirm key and enable encrypted comm --------
    def attempt_login(self):
        key_str = self.entry_key.get().strip()
        if not key_str:
            messagebox.showwarning("Input Error", "Encryption key required! Paste the key shown above.")
            return
        threading.Thread(target=self._confirm_thread, args=(key_str,), daemon=True).start()

    def _confirm_thread(self, key_str):
        if not self.client_socket:
            self.append("No active connection to server. Press Enter first.", "error")
            return

        success, msg = confirm_key_and_activate(self.client_socket, key_str)
        if not success:
            self.append(msg, "error")
            return

        # success: msg is welcome text (decrypted)
        self.append(msg, "info")

        # disable inputs and enable kill + alerts
        self.entry_username.config(state="disabled")
        self.entry_password.config(state="disabled")
        self.entry_key.config(state="disabled")
        self.btn_login.config(state="disabled")
        self.btn_enter.config(state="disabled")
        self.btn_kill.config(state="normal")
        self.is_connected = True

        # Display alert generation start
        self.append("Generating alerts and waiting for real-time updates from server...", "info")

        # Start alert listener (encrypted)
        threading.Thread(target=receive_alerts, args=(self.client_socket, self), daemon=True).start()

    def kill_connection(self):
        self.is_connected = False
        try:
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
            self.append("Connection terminated by user.", "error")
            self.btn_kill.config(state="disabled")
        except Exception as e:
            self.append(f"Error closing connection: {e}", "error")


def run_gui():
    app = GUIClient()
    app.mainloop()


if __name__ == "__main__":
    run_gui()

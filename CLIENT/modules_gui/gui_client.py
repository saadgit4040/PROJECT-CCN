"""
GUI Frontend for Client (manual credential entry + kill connection)
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
from client3 import connect_to_server, login, receive_alerts, receive_login_pair


class GUIClient(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Real-Time Alert Monitoring System - Client")
        self.geometry("750x580")
        self.resizable(False, False)

        self.client_socket = None
        self.server_user = None
        self.server_pass = None
        self.server_key = None
        self.is_connected = False  # for controlling the alert loop

        # GUI setup
        self.create_widgets()
        self.configure_tags()

        # Connect to server and get login details
        threading.Thread(target=self.show_login_pair, daemon=True).start()

    # ---------------- GUI Setup ---------------- #
    def create_widgets(self):
        tk.Label(self, text="Client Login", font=("Arial", 16, "bold")).pack(pady=10)

        # Username
        tk.Label(self, text="Username").pack()
        self.entry_username = tk.Entry(self, width=30)
        self.entry_username.pack(pady=5)

        # Password
        tk.Label(self, text="Password").pack()
        self.entry_password = tk.Entry(self, show="*", width=30)
        self.entry_password.pack(pady=5)

        # Key
        tk.Label(self, text="Decryption Key").pack()
        self.entry_key = tk.Entry(self, width=50)
        self.entry_key.pack(pady=5)

        # Login + Kill buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        self.btn_login = tk.Button(button_frame, text="Login", command=self.attempt_login)
        self.btn_login.pack(side=tk.LEFT, padx=10)

        self.btn_kill = tk.Button(
            button_frame, text="Kill Connection", command=self.kill_connection, state='disabled', bg="#cc0000", fg="white"
        )
        self.btn_kill.pack(side=tk.LEFT, padx=10)

        # Console
        tk.Label(self, text="Client Console").pack(pady=5)
        self.console = scrolledtext.ScrolledText(self, width=90, height=20, state='disabled', wrap=tk.WORD)
        self.console.pack(pady=5)

    # ---------------- Console Styling ---------------- #
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

    # ---------------- Server Communication ---------------- #
    def show_login_pair(self):
        """
        Connects to server, receives LOGIN_PAIR, prints them in console
        for user to manually type in fields.
        """
        try:
            self.client_socket = connect_to_server()
            self.append("Connected to server successfully.", "info")

            # Receive server credentials and key
            self.server_user, self.server_pass, self.server_key = receive_login_pair(self.client_socket)

            # Show only in console (not in input boxes)
            self.append("\n--- SERVER CREDENTIALS ---", "info")
            self.append(f"Username: {self.server_user}", "info")
            self.append(f"Password: {self.server_pass}", "info")
            self.append(f"Encryption Key: {self.server_key}", "info")
            self.append("-----------------------------\n", "info")

            self.append("Please manually enter the above credentials and key into the fields.", "info")

        except Exception as e:
            self.append(f"Error connecting or receiving login pair: {e}", "error")

    def attempt_login(self):
        """
        Triggered when user clicks Login. Runs login logic.
        """
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        key_str = self.entry_key.get().strip()

        if not username or not password or not key_str:
            messagebox.showwarning("Input Error", "All fields are required!")
            return

        # Threaded login (avoid GUI freeze)
        threading.Thread(target=self.backend_login, args=(username, password, key_str), daemon=True).start()

    def backend_login(self, username, password, key_str):
        """
        Backend login thread.
        """
        try:
            key_bytes = key_str.encode()  # use string as-is
        except Exception:
            self.append("Invalid key format! Make sure you copied it exactly from the server.", "error")
            return

        try:
            success, msg = login(self.client_socket, username, password, key_bytes)
            self.append(msg, "info" if success else "error")

            if success:
                # Disable login fields
                self.entry_username.config(state='disabled')
                self.entry_password.config(state='disabled')
                self.entry_key.config(state='disabled')
                self.btn_login.config(state='disabled')

                # Enable kill button
                self.btn_kill.config(state='normal')

                self.append("\nLogin successful. Receiving live alerts...\n", "info")
                self.is_connected = True

                # Start continuous alert listener
                threading.Thread(target=self.listen_for_alerts, daemon=True).start()
        except Exception as e:
            self.append(f"Login error: {e}", "error")

    def listen_for_alerts(self):
        """
        Keeps receiving alerts until the user kills the connection.
        """
        while self.is_connected:
            try:
                receive_alerts(self.client_socket, self)
            except Exception as e:
                self.append(f"Error receiving alerts: {e}", "error")
                break

    def kill_connection(self):
        """
        Disconnect from server and stop receiving alerts.
        """
        try:
            self.is_connected = False
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None

            self.append("\nConnection terminated by user.\n", "error")
            self.btn_kill.config(state='disabled')
        except Exception as e:
            self.append(f"Error closing connection: {e}", "error")


# ---------------- Launcher ---------------- #
def run_gui():
    app = GUIClient()
    app.mainloop()

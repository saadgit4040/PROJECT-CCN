# modules_gui/gui_test.py
import customtkinter as ctk

def main():
    # Initialize customtkinter
    ctk.set_appearance_mode("dark")  # Options: "light", "dark", "system"
    ctk.set_default_color_theme("blue")  # You can try "green" or "dark-blue"

    # Create window
    app = ctk.CTk()
    app.title("CustomTkinter Test Window")
    app.geometry("500x300")

    # Add some test widgets
    label = ctk.CTkLabel(app, text="✅ CustomTkinter is working!", font=("Arial", 18))
    label.pack(pady=20)

    button = ctk.CTkButton(app, text="Close", command=app.destroy)
    button.pack(pady=10)

    # Run the window
    app.mainloop()

if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import messagebox
import sqlite3
from werkzeug.security import check_password_hash
import subprocess


def draw_vertical_gradient(canvas, width, height, color1, color2):
    r1, g1, b1 = canvas.winfo_rgb(color1)
    r2, g2, b2 = canvas.winfo_rgb(color2)
    r_ratio = (r2 - r1) / height
    g_ratio = (g2 - g1) / height
    b_ratio = (b2 - b1) / height

    for i in range(height):
        nr = int(r1 + (r_ratio * i)) >> 8
        ng = int(g1 + (g_ratio * i)) >> 8
        nb = int(b1 + (b_ratio * i)) >> 8
        color = f'#{nr:02x}{ng:02x}{nb:02x}'
        canvas.create_line(0, i, width, i, fill=color)

def create_login_window():
    window = tk.Tk()
    window.title("Login")
    window.geometry("600x450")  # Increased window size
    window.resizable(False, False)

    # Solid background to match form_frame
    bg_canvas = tk.Canvas(window, width=600, height=450, highlightthickness=0, bg="#1e1e2f")
    bg_canvas.pack(fill="both", expand=True)

    # Titles
    bg_canvas.create_text(300, 80, text="AI Voice Assistant", font=("Helvetica", 24, "bold"), fill="#e2e8f0")  # Larger title font
    bg_canvas.create_text(300, 120, text="Login", font=("Helvetica", 16), fill="#cbd5e1")  # Larger subtitle font

    # Form frame with centered alignment
    form_frame = tk.Frame(window, bg="#1e1e2f", bd=0, highlightthickness=0)
    bg_canvas.create_window(300, 300, window=form_frame)

    # Shared entry style with larger font and padding
    entry_style = {
        "width": 35,  # Increased width
        "bg": "#0f172a",
        "fg": "#f1f5f9",
        "insertbackground": "#f1f5f9",
        "borderwidth": 1,
        "relief": "flat",
        "highlightthickness": 1,
        "highlightbackground": "#334155",
        "highlightcolor": "#334155",
        "font": ("Helvetica", 14)  # Larger font
    }

    # Email field
    email_label = tk.Label(form_frame, text="Email", font=("Helvetica", 14), fg="#f1f5f9", bg="#1e1e2f")
    email_label.grid(row=0, column=0, sticky="w", pady=(0, 10))  # Increased padding
    email_entry = tk.Entry(form_frame, **entry_style)
    email_entry.grid(row=1, column=0, pady=(0, 20))  # Increased padding

    # Password field
    pass_label = tk.Label(form_frame, text="Password", font=("Helvetica", 14), fg="#f1f5f9", bg="#1e1e2f")
    pass_label.grid(row=2, column=0, sticky="w", pady=(0, 10))  # Increased padding
    pass_entry = tk.Entry(form_frame, show="*", **entry_style)
    pass_entry.grid(row=3, column=0, pady=(0, 20))  # Increased padding

    # Error message label (hidden initially)
    error_message = tk.Label(form_frame, text="", font=("Helvetica", 12), fg="red", bg="#1e1e2f")
    error_message.grid(row=4, column=0, pady=(10, 0))

    # Submit button with modern style (smaller and rounded)
    def on_submit():
        email = email_entry.get()
        password = pass_entry.get()

        try:
            conn = sqlite3.connect('database.db')  # Ensure path is correct
            cur = conn.cursor()
            cur.execute("SELECT password FROM users WHERE email = ?", (email,))
            row = cur.fetchone()
            conn.close()

            if row and check_password_hash(row[0], password):
                # Successful login
                error_message.config(text="")
                window.destroy()
                #test.main(email)  # pass email to test.py
                subprocess.Popen(['python', 'main.py', email])
                
            else:
                error_message.config(text="Invalid email or password. Please try again.")
                window.after(3000, lambda: error_message.config(text=""))

        except Exception as e:
            error_message.config(text=f"Login error: {str(e)}")
            window.after(3000, lambda: error_message.config(text=""))
            

    submit_btn = tk.Button(form_frame, text="Submit", command=on_submit,
                           font=("Helvetica", 12), bg="#3b82f6", fg="white",
                           activebackground="#2563eb", activeforeground="white",
                           relief="flat", padx=12, pady=6, bd=0,
                           highlightthickness=0)  # Smaller, modern button with rounded corners
    submit_btn.grid(row=5, column=0, pady=20)  # Adjusted button position for better spacing

    return window


#def run_assistant_window():
    # Start the test.py logic after login
    test.main()  # Assuming test.py has a `main()` function that runs the assistant window


# Demo action
def on_listen_click():
    print("🎙 Listening...")

if __name__ == "__main__":
    login_window = create_login_window()
    login_window.mainloop()

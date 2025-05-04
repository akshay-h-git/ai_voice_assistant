import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk

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

def create_main_window(on_listen_click):
    window = tk.Tk()
    window.title("AI Voice Assistant")
    window.geometry("800x600")
    window.resizable(False, False)

    # Gradient background
    bg_canvas = tk.Canvas(window, width=800, height=600, highlightthickness=0)
    bg_canvas.pack(fill="both", expand=True)
    draw_vertical_gradient(bg_canvas, 800, 600, "#1e293b", "#0f172a")

    # Title
    title_frame = tk.Frame(window, bg="#1e1e2f", bd=0)
    title_label = tk.Label(title_frame, text="AI Voice Assistant", font=("Helvetica", 20, "bold"),
                           fg="#3b82f6", bg="#1e1e2f", padx=10, pady=5)
    title_label.pack()
    bg_canvas.create_window(400, 40, window=title_frame)

    # Description
    desc_frame = tk.Frame(window, bg="#1e1e2f", bd=0)
    description_label = tk.Label(desc_frame, text="Control your PC with your voice", font=("Helvetica", 14),
                                 fg="#94a3b8", bg="#1e1e2f", padx=10, pady=2)
    description_label.pack()
    bg_canvas.create_window(400, 80, window=desc_frame)

    # Output text area position
    output_area_y = 330
    output_height = 20 * 13

    # Shadow frame behind output
    shadow_frame = tk.Frame(window, bg="#0c0c15")
    bg_canvas.create_window(403, output_area_y + 3, window=shadow_frame)

    # Border frame
    output_border = tk.Frame(window, bg="#0f172a", bd=2)
    bg_canvas.create_window(400, output_area_y, window=output_border)

    # Actual output text
    output_area = scrolledtext.ScrolledText(
        output_border, width=60, height=20,
        bg="#0f172a", fg="#f1f5f9",
        insertbackground="#f1f5f9", wrap=tk.WORD,
        borderwidth=0, relief="flat"
    )
    output_area.pack()

    # Mic icon
    try:
        mic_img_raw = Image.open("mic.png").resize((32, 32), Image.Resampling.LANCZOS)
        mic_img = ImageTk.PhotoImage(mic_img_raw)
    except Exception as e:
        mic_img = None
        print("Icon not loaded:", e)

    # Button
    button_container = tk.Canvas(window, width=260, height=70, bg="#0f172a", highlightthickness=0, bd=0)
    shadow = button_container.create_oval(15, 15, 245, 55, fill="#0e0e18", outline="")
    button_shape = button_container.create_oval(10, 10, 240, 50, fill="#3b82f6", outline="")

    if mic_img:
        button_container.image = mic_img
        button_container.create_image(80, 30, image=mic_img)
        button_container.create_text(150, 30, text="Listen", fill="white", font=("Helvetica", 12, "bold"))
    else:
        button_container.create_text(125, 30, text="Listen", fill="white", font=("Helvetica", 12, "bold"))

    def on_hover(event):
        button_container.itemconfig(button_shape, fill="#60a5fa")

    def on_leave(event):
        button_container.itemconfig(button_shape, fill="#3b82f6")

    def animate_click():
        button_container.itemconfig(button_shape, fill="#2563eb")
        window.after(100, lambda: button_container.itemconfig(button_shape, fill="#3b82f6"))

    # Border pulse logic
    pulse_active = tk.BooleanVar(value=False)
    pulse_colors = ["#1e3a8a", "#2563eb"]
    pulse_index = [0]

    def pulse_border():
        if not pulse_active.get():
            output_border.configure(bg="#0f172a")
            return
        output_border.configure(bg=pulse_colors[pulse_index[0]])
        pulse_index[0] = (pulse_index[0] + 1) % len(pulse_colors)
        window.after(500, pulse_border)

    def start_pulsing():
        if not pulse_active.get():
            pulse_active.set(True)
            pulse_border()

    def stop_pulsing():
        pulse_active.set(False)

    def on_click(event):
        if 10 < event.x < 240 and 10 < event.y < 50:
            animate_click()
            start_pulsing()
            on_listen_click()
            window.after(5000, stop_pulsing)  # Demo duration

    button_container.bind("<Enter>", on_hover)
    button_container.bind("<Leave>", on_leave)
    button_container.bind("<Button-1>", on_click)

    # Button position
    button_y = output_area_y + (output_height / 2) + 75 + 35
    bg_canvas.create_window(400, button_y, window=button_container)

    return window, output_area

# Demo action
def on_listen_click():
    print("🎙 Listening...")

if __name__ == "__main__":
    window, output_area = create_main_window(on_listen_click)
    output_area.insert(tk.END, "Python: Initializing Python...\n")
    window.mainloop()

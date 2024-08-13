import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import *
from PIL import Image, ImageTk


class SplashScreen:
    def __init__(self, master):
        self.master = master
        self.master.title("Field Museum Image Parser")
        self.master.geometry("400x400")
        self.master.resizable(False, False)
        master.iconbitmap("images/logo.ico")

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        window_width = 400
        window_height = 400
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        self.master.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        # Adding Field museum images
        img = ImageTk.PhotoImage(Image.open("images/splash_image.png"))
        self.img_label = ttk.Label(self.master, image=img)
        self.img_label.image = img
        self.img_label.pack()

        self.text_label = ttk.Label(self.master, text="Created: By Riley Herbst ")
        self.text_label.pack(pady=20)

        self.text_label2 = ttk.Label(self.master, text="Version: 1.1")
        self.text_label2.pack(pady=10)

        self.master.after(5000, self.close)

    def close(self):
        self.master.destroy()

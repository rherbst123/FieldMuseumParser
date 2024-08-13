import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO


class FullScreenImage:
    def __init__(self, master, image):
        self.master = master
        self.original_image = image
        self.top = tk.Toplevel(master)
        self.top.title("Image Viewer")
        master.iconbitmap("images/logo.ico")

        screen_width = self.top.winfo_screenwidth()
        screen_height = self.top.winfo_screenheight()

        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.top.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.top.resizable(True, True)

        self.canvas = tk.Canvas(self.top, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.top.bind("<Configure>", self.resize_image)
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan)
        self.top.bind("<MouseWheel>", self.zoom)  # For Windows
        self.top.bind("<Button-4>", self.zoom)  # For Linux (scroll up)
        self.top.bind("<Button-5>", self.zoom)  # For Linux (scroll down)
        self.top.bind("<Button-3>", self.close)

        self.scale = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.show_image()

    def show_image(self):
        self.update_image()

    def update_image(self):
        width = self.top.winfo_width()
        height = self.top.winfo_height()

        if width <= 1 or height <= 1:
            self.top.after(100, self.update_image)
            return

        img_ratio = self.original_image.width / self.original_image.height
        if img_ratio > 1:
            new_width = 1000
            new_height = int(1000)
        else:
            new_height = 1000
            new_width = int(1000)

        new_width = max(1, int(new_width * self.scale))
        new_height = max(1, int(new_height * self.scale))

        if self.scale < 1:
            resample_method = Image.Resampling.LANCZOS
        else:
            resample_method = Image.Resampling.BICUBIC

        resized_image = self.original_image.resize(
            (new_width, new_height), resample_method
        )
        self.photo = ImageTk.PhotoImage(resized_image)

        self.canvas.delete("all")
        self.canvas.create_image(
            width // 2 + self.pan_x,
            height // 2 + self.pan_y,
            image=self.photo,
            anchor=tk.CENTER,
            tags="image",
        )

    def resize_image(self, event):
        self.update_image()

    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def pan(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.pan_x = self.canvas.canvasx(0)
        self.pan_y = self.canvas.canvasy(0)

    def zoom(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        factor = 0.9 if event.delta < 0 else 1.1
        self.scale *= factor
        self.scale = max(0.01, min(self.scale, 5.0))
        self.canvas.scale("all", x, y, factor, factor)
        self.pan_x *= factor
        self.pan_y *= factor
        self.update_image()

    def close(self, event=None):
        self.top.destroy()

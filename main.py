import ttkbootstrap as ttk
from image_processor_gui import ImageProcessorGUI
from splash_screen import SplashScreen


def main():
    # Create the main application window but don't show it yet
    root = ttk.Window(themename="darkly")
    app = ImageProcessorGUI(root)

    # Create and show splash screen
    splash = ttk.Toplevel(root)
    splash_app = SplashScreen(splash)

    def show_main_window():
        splash.destroy()
        root.deiconify()

    # Couldnt figure out how to do the timing so this is how it be
    root.after(3500, show_main_window)

    # Hide the main window initially
    root.withdraw()

    # Start the main event loop
    root.mainloop()


if __name__ == "__main__":
    main()

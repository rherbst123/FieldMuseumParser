import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import *
import os
import base64
import anthropic
import requests
from PIL import Image, ImageTk
from io import BytesIO
import subprocess
import sys
from image_viewer import FullScreenImage
from ttkbootstrap.icons import Icon
from csv_processor_gui import CSVProcessor
import threading
import queue
import os


class ImageProcessorGUI:

    def __init__(self, master):
        self.master = master
        master.title("Field Museum Herbarium Parser")
        master.geometry("800x800")
        master.iconbitmap("images/logo.ico")

        self.current_image_index = 0
        self.processed_images = []
        self.processed_outputs = []
        self.output_file = ""

        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()

        input_frame = ttk.LabelFrame(master, text="Input Settings")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="URL's of Images").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.url_file_entry = ttk.Entry(input_frame, width=50)
        self.url_file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(
            input_frame,
            bootstyle="success",
            text="Browse",
            command=self.browse_url_file,
        ).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(input_frame, text="API Key File:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.api_key_entry = ttk.Entry(input_frame, width=50)
        self.api_key_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(
            input_frame,
            bootstyle="success",
            text="Browse",
            command=self.browse_api_key_file,
        ).grid(row=1, column=2, padx=5, pady=5)

        # Setting Default Folder for prompts
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_prompt_folder = os.path.join(script_dir, "Inputs", "prompts")

        ttk.Label(input_frame, text="Prompt Folder:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.prompt_folder_entry = ttk.Entry(input_frame, width=50)
        self.prompt_folder_entry.insert(
            0, default_prompt_folder
        )  # Set the default folder path
        self.prompt_folder_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(
            input_frame,
            bootstyle="success",
            text="Browse",
            command=self.browse_prompt_folder,
        ).grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(input_frame, text="Prompt:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.prompt_var = tk.StringVar()
        self.prompt_dropdown = ttk.Combobox(
            input_frame, textvariable=self.prompt_var, width=47
        )
        self.prompt_dropdown.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(
            input_frame,
            bootstyle="success",
            text="Refresh",
            command=self.refresh_prompts,
        ).grid(row=3, column=2, padx=5, pady=5)

        ttk.Label(input_frame, text="Output File:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        self.output_file_entry = ttk.Entry(input_frame, width=50)
        self.output_file_entry.grid(row=4, column=1, padx=5, pady=5)
        ttk.Button(
            input_frame, bootstyle="success", text="Save As", command=self.save_as
        ).grid(row=4, column=2, padx=5, pady=5)

        ttk.Button(
            master,
            bootstyle="success",
            text="Process Images",
            command=self.process_images,
        ).pack(pady=5)

        output_frame = ttk.LabelFrame(master, text="Output")
        output_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.image_label = ttk.Label(output_frame)
        self.image_label.pack(side="left", padx=10, pady=10)

        text_frame = ttk.Frame(output_frame)
        text_frame.pack(side="right", fill="both", expand=True)

        self.output_text = tk.Text(text_frame, wrap="word", width=40, height=10)
        self.output_text.pack(padx=10, pady=10, fill="both", expand=True)

        self.save_button = ttk.Button(
            text_frame, bootstyle="success", text="Save Edits", command=self.save_edits
        )
        self.save_button.pack(pady=10)

        nav_frame = ttk.Frame(master)
        nav_frame.pack(pady=10)

        self.prev_button = ttk.Button(
            nav_frame,
            bootstyle="success",
            text="Previous",
            command=self.show_previous_image,
            state=tk.DISABLED,
        )
        self.prev_button.grid(row=0, column=0, padx=5, pady=4)

        self.next_button = ttk.Button(
            nav_frame,
            bootstyle="success",
            text="Next",
            command=self.show_next_image,
            state=tk.DISABLED,
        )
        self.next_button.grid(row=0, column=1, padx=5, pady=4)

        self.final_output = tk.Text(master, wrap="word", width=80, height=10)
        self.final_output.pack(padx=10, pady=5, fill="both", expand=True)

        self.toggle_theme_button = ttk.Button(
            nav_frame,
            bootstyle="success",
            text="Toggle Theme",
            command=self.toggle_theme,
        )
        self.toggle_theme_button.grid(row=0, column=2, padx=5, pady=4)

        self.toggle_theme_button2 = ttk.Button(
            nav_frame,
            bootstyle="success",
            text="CSV Processing",
            command=self.open_csv_processor,
        )
        self.toggle_theme_button2.grid(row=0, column=3, padx=5, pady=4)

    def browse_url_file(self):
        file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        self.url_file_entry.delete(0, tk.END)
        self.url_file_entry.insert(0, file)

    def browse_api_key_file(self):
        file = filedialog.askopenfilename()
        self.api_key_entry.delete(0, tk.END)
        self.api_key_entry.insert(0, file)

    def browse_prompt_folder(self):
        folder = filedialog.askdirectory()
        self.prompt_folder_entry.delete(0, tk.END)
        self.prompt_folder_entry.insert(0, folder)
        self.refresh_prompts()

    def refresh_prompts(self):
        prompt_folder = self.prompt_folder_entry.get()
        if not prompt_folder:
            messagebox.showwarning("Warning", "Please select a prompt folder first.")
            return
        prompt_files = [f for f in os.listdir(prompt_folder) if f.endswith(".txt")]
        self.prompt_dropdown["values"] = prompt_files
        if prompt_files:
            self.prompt_dropdown.set(prompt_files[0])

    def save_as(self):
        file = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text files", "*.txt")]
        )
        if file:
            self.output_file_entry.delete(0, tk.END)
            self.output_file_entry.insert(0, file)
            self.output_file = file

    def process_images(self):
        url_file = self.url_file_entry.get()
        output_file = self.output_file_entry.get()
        api_key_file = self.api_key_entry.get()
        prompt_folder = self.prompt_folder_entry.get()
        selected_prompt = self.prompt_var.get()

        if not all(
            [url_file, output_file, api_key_file, prompt_folder, selected_prompt]
        ):
            messagebox.showerror("Error", "All fields must be filled.")
            return

        self.output_file = output_file

        try:
            with open(api_key_file, "r", encoding="utf-8") as api_file:
                api_key = api_file.read().strip()
        except UnicodeDecodeError:
            with open(api_key_file, "r") as api_file:
                api_key = api_file.read().strip()

        prompt_path = os.path.join(prompt_folder, selected_prompt)
        try:
            with open(prompt_path, "r", encoding="utf-8") as prompt_file:
                prompt_text = prompt_file.read().strip()
        except UnicodeDecodeError:
            messagebox.showerror(
                "AHHHHH ERROR",
                f"Unable to read the prompt file: {prompt_path}. Please make sure no special characters are in prompt and keep it NEAT!!",
            )
            return

        try:
            with open(url_file, "r", encoding="utf-8") as url_file:
                urls = url_file.readlines()
        except UnicodeDecodeError:
            with open(url_file, "r") as url_file:
                urls = url_file.readlines()

        self.processed_images.clear()
        self.processed_outputs.clear()
        self.current_image_index = 0

        # Create and start the worker thread
        worker_thread = threading.Thread(
            target=self.process_images_thread, args=(urls, api_key, prompt_text)
        )
        worker_thread.start()

        # Start a periodic check for results
        self.master.after(100, self.check_results)

    # TODO containerize this so that we can add support for Chat Gpt 4o AND Local Models. Each will have their own files.

    # Part 2 of script. Made it threaded becuase of hook up and (Not Responding in GUI)
    def process_images_thread(self, urls, api_key, prompt_text):
        client = anthropic.Anthropic(api_key=api_key)

        for index, url in enumerate(urls):
            url = url.strip()
            try:
                response = requests.get(url)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))

                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

                message = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=2500,
                    temperature=0,
                    system="You are an assistant that has a job to extract text from an image and parse it out. Only include the text that is relevant to the image.",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": base64_image,
                                    },
                                },
                            ],
                        }
                    ],
                )

                output = self.format_response(
                    f"Image {index + 1}", message.content, url
                )
                self.result_queue.put((image, output))

            except requests.exceptions.RequestException as e:
                error_message = f"Error processing image {index + 1}: {str(e)}"
                self.result_queue.put((None, error_message))

        # Signal that all processing is complete
        self.result_queue.put((None, None))

    def check_results(self):
        try:
            image, output = self.result_queue.get_nowait()
            if image is None and output is None:
                # All processing is complete
                self.show_completion_message(self.output_file)
                return

            if image:
                self.processed_images.append(image)
            self.processed_outputs.append(output)
            self.final_output.insert(tk.END, output + "\n" + "=" * 50 + "\n")

            if len(self.processed_images) == 1:
                self.show_image(0)
                self.prev_button.config(state=tk.NORMAL)
                self.next_button.config(state=tk.NORMAL)

        except queue.Empty:
            pass

        # Schedule the next check
        self.master.after(100, self.check_results)

    def format_response(self, image_name, response_data, url):
        text_block = response_data[0].text
        lines = text_block.split("\n")

        formatted_result = f"{image_name}\n"
        formatted_result += f"URL: {url}\n\n"
        formatted_result += "\n".join(lines)

        return formatted_result

    def display_image(self, image):
        display_image = image.copy()
        display_image.thumbnail((200, 300))
        photo = ImageTk.PhotoImage(display_image)

        self.image_label.config(image=photo)
        self.image_label.image = photo

        self.image_label.bind("<Button-1>", lambda event: self.open_full_screen(image))

    def open_full_screen(self, image):
        FullScreenImage(self.master, image)

    def show_image(self, index):
        self.current_image_index = index
        self.display_image(self.processed_images[index])
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, self.processed_outputs[index])

    def show_previous_image(self):
        if self.current_image_index > 0:
            self.save_current_output()
            self.show_image(self.current_image_index - 1)

    def show_next_image(self):
        if self.current_image_index < len(self.processed_images) - 1:
            self.save_current_output()
            self.show_image(self.current_image_index + 1)

    def save_current_output(self):
        self.processed_outputs[self.current_image_index] = self.output_text.get(
            1.0, tk.END
        )

    def show_completion_message(self, output_file):
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(self.final_output.get("1.0", tk.END))

        msg_box = tk.messagebox.askyesno(
            "Processing Complete",
            f"All images processed. Results saved to {output_file}.\n\n"
            "Would you like to open the directory containing the output file?",
        )
        if msg_box:
            self.open_output_directory(output_file)

    def open_output_directory(self, output_file):
        output_dir = os.path.dirname(os.path.abspath(output_file))
        if sys.platform == "win32":
            os.startfile(output_dir)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", output_dir])
        else:
            subprocess.Popen(["xdg-open", output_dir])

    def save_edits(self):
        if not self.output_file:
            messagebox.showerror("Error", "No output file specified.")
            return

        self.save_current_output()

        self.final_output.delete(1.0, tk.END)
        for output in self.processed_outputs:
            self.final_output.insert(tk.END, output + "\n" + "=" * 50 + "\n")

        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(self.final_output.get("1.0", tk.END))
            messagebox.showinfo("Success", f"Edits saved to {self.output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save edits: {str(e)}")

    def toggle_theme(self):
        current_theme = self.master.style.theme_use()
        if "dark" in current_theme:
            self.master.style.theme_use("morph")
        else:
            self.master.style.theme_use("darkly")

    # TODO - Add Functionalty of old csv processing script

    def open_csv_processor(self):
        CSVProcessor(self.master)

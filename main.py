import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk, ImageOps, UnidentifiedImageError
from moviepy.editor import VideoFileClip, AudioFileClip
from tkinterdnd2 import TkinterDnD, DND_FILES

# Constants
SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"]
SUPPORTED_VIDEO_FORMATS = ["mp4", "avi", "mkv", "mov", "wmv"]
SUPPORTED_AUDIO_FORMATS = ["mp3", "wav", "aac", "flac"]
DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "converted")

# Converter App
class RosConversorApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("RosConversor")
        self.geometry("1200x700")
        self.resizable(False, False)

        self.file_paths = []
        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

        self.configure(bg="#1e1e1e")  # Darker outer background
        self.create_widgets()
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_event)

    def create_widgets(self):
        # Drop Area
        self.drop_area = ctk.CTkFrame(self, width=1100, height=100, corner_radius=10, fg_color="#4a4a4a")  # Slightly lighter drop area
        self.drop_area.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        self.drop_area_label = ctk.CTkLabel(self.drop_area, text="Drag and drop files here or click 'Browse Files'", font=ctk.CTkFont(size=16))
        self.drop_area_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Browse Button
        self.browse_button = ctk.CTkButton(self, text="Browse Files", command=self.browse_files)
        self.browse_button.place(relx=0.4, rely=0.2, anchor=tk.CENTER)

        # Open Converted Folder Button
        self.open_folder_button = ctk.CTkButton(self, text="Open Converted Folder", command=self.open_converted_folder)
        self.open_folder_button.place(relx=0.6, rely=0.2, anchor=tk.CENTER)

        # File List Area
        self.file_list_frame = ctk.CTkScrollableFrame(self, width=1100, height=400, fg_color="#3a3a3a", corner_radius=10)  # Medium gray frame
        self.file_list_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    def browse_files(self):
        files = filedialog.askopenfilenames(title="Select Files")
        for file in files:
            if os.path.isfile(file):
                self.add_file(file)

    def add_file(self, file_path):
        if file_path in self.file_paths:
            messagebox.showinfo("Duplicate File", f"The file '{os.path.basename(file_path)}' is already in the list.")
            return

        self.file_paths.append(file_path)
        self.display_file(file_path)

    def display_file(self, file_path):
        ext = os.path.splitext(file_path)[1][1:].lower()
        file_type = self.detect_file_type(ext)
        if not file_type:
            messagebox.showerror("Unsupported Format", f"The file '{os.path.basename(file_path)}' is not supported.")
            return

        file_frame = ctk.CTkFrame(self.file_list_frame, fg_color="#525252", corner_radius=10, height=50)  # Slightly lighter file frame
        file_frame.pack(pady=5, padx=10, fill="x")

        file_label = ctk.CTkLabel(file_frame, text=os.path.basename(file_path), font=ctk.CTkFont(size=14))
        file_label.pack(side="left", padx=10)

        format_options = self.get_conversion_formats(file_type, ext)
        format_menu = ctk.CTkOptionMenu(file_frame, values=format_options)
        format_menu.set(format_options[0])
        format_menu.pack(side="left", padx=10)

        convert_button = ctk.CTkButton(file_frame, text="Convert", command=lambda: self.start_conversion(file_path, format_menu.get(), file_frame))
        convert_button.pack(side="right", padx=10)

    def detect_file_type(self, ext):
        if ext in SUPPORTED_IMAGE_FORMATS:
            return "image"
        elif ext in SUPPORTED_VIDEO_FORMATS:
            return "video"
        elif ext in SUPPORTED_AUDIO_FORMATS:
            return "audio"
        return None

    def get_conversion_formats(self, file_type, current_format):
        if file_type == "image":
            return [fmt for fmt in SUPPORTED_IMAGE_FORMATS if fmt != current_format]
        elif file_type == "video":
            return [fmt for fmt in SUPPORTED_VIDEO_FORMATS if fmt != current_format]
        elif file_type == "audio":
            return [fmt for fmt in SUPPORTED_AUDIO_FORMATS if fmt != current_format]

    def start_conversion(self, file_path, output_format, file_frame):
        threading.Thread(target=self.convert_file, args=(file_path, output_format, file_frame)).start()

    def convert_file(self, file_path, output_format, file_frame):
        try:
            ext = os.path.splitext(file_path)[1][1:].lower()
            output_file = os.path.join(DEFAULT_OUTPUT_DIR, f"{os.path.splitext(os.path.basename(file_path))[0]}.{output_format}")

            if ext in SUPPORTED_IMAGE_FORMATS:
                with Image.open(file_path) as img:
                    img.save(output_file, format=output_format.upper())
            elif ext in SUPPORTED_VIDEO_FORMATS:
                clip = VideoFileClip(file_path)
                clip.write_videofile(output_file, codec='libx264')
                clip.close()
            elif ext in SUPPORTED_AUDIO_FORMATS:
                clip = AudioFileClip(file_path)
                clip.write_audiofile(output_file)
                clip.close()

            file_frame.configure(fg_color="green")
            messagebox.showinfo("Conversion Complete", f"The file has been converted to {output_format}.")
        except Exception as e:
            file_frame.configure(fg_color="red")
            messagebox.showerror("Conversion Error", f"Failed to convert {os.path.basename(file_path)}:\n{str(e)}")

    def drop_event(self, event):
        files = self.tk.splitlist(event.data)
        for file in files:
            if os.path.isfile(file):
                self.add_file(file)

    def open_converted_folder(self):
        if os.path.exists(DEFAULT_OUTPUT_DIR):
            os.startfile(DEFAULT_OUTPUT_DIR)
        else:
            messagebox.showerror("Error", "Converted folder not found.")

if __name__ == "__main__":
    app = RosConversorApp()
    app.mainloop()

import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from fpdf import FPDF
import threading
import queue
from tempfile import NamedTemporaryFile
import tempfile
import fitz

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

def compress_image(image):
    quality_dict = {'High': 50, 'Medium': 35, 'Low': 20}
    quality = quality_dict[quality_combo.get()]

    # Get the dimensions of the image
    width, height = image.size

    # Get the watermark cutoff percentage from the entry widget
    watermark_percentage = float(watermark_entry.get()) / 100

    # Define the area to crop (excluding the bottom percentage)
    crop_area = (0, 0, width, height - int(height * watermark_percentage))

    # Crop the image
    cropped_image = image.crop(crop_area)

    kindle_resolution = (1236, 1648)  # Resolution for Kindle Paperwhite model M2L3EK
    image_resized = cropped_image.resize(kindle_resolution, Image.ANTIALIAS)
    return image_resized, quality

def count_images(directory):
    total = 0
    for folder_name in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, folder_name)):
            for file in os.listdir(os.path.join(directory, folder_name)):
                if file.endswith('.jpg'):
                    total += 1
    return total

def convert_images_to_pdf(queue):
    base_dir = input_dir_entry.get()
    output_path = output_dir_entry.get()

    total_images = count_images(base_dir)
    processed_images = 0

    pdf_paths = []

    # Define the width and height in mm based on the 72 dpi conversion
    kindle_width_mm = 1236 * 0.352778
    kindle_height_mm = 1648 * 0.352778

    for folder_name in os.listdir(base_dir):
        if not os.path.isdir(os.path.join(base_dir, folder_name)):
            continue

        pdf = FPDF(orientation='P', unit='mm', format=(kindle_width_mm, kindle_height_mm))
        pdf.set_auto_page_break(auto=False, margin=0)

        for file in natural_sort(os.listdir(os.path.join(base_dir, folder_name))):
            if not file.endswith('.jpg'):
                continue

            img_path = os.path.join(base_dir, folder_name, file)
            img = Image.open(img_path)

            if img.size == (0, 0):
                img.close()
                continue

            img, quality = compress_image(img)

            # Create a temporary file
            with NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                img.save(tmp_file, format='JPEG', quality=quality)
                temp_path = tmp_file.name

            pdf.add_page()
            pdf.image(temp_path, x=0, y=0, w=kindle_width_mm, h=kindle_height_mm)

            # Remove the temporary file
            os.unlink(temp_path)

            # Close the image
            img.close()

            processed_images += 1
            progress = 100 * processed_images / total_images
            queue.put(('progress', progress), block=True)  # Block if the queue is full

        output_name = os.path.basename(os.path.normpath(base_dir)) + '-' + folder_name + '.pdf'
        pdf_path = os.path.join(tempfile.gettempdir(), output_name)
        pdf.output(pdf_path)
        pdf_paths.append(pdf_path)

    merged_pdf = fitz.open()
    for pdf_path in pdf_paths:
        merged_pdf.insert_pdf(fitz.open(pdf_path))

    output_name = os.path.basename(os.path.normpath(base_dir)) + '.pdf'
    pdf_path = os.path.join(output_path, output_name)
    merged_pdf.save(pdf_path, garbage=4, deflate=True)

    queue.put(('done', None))

def start_conversion():
    folder_label.pack()
    file_label.pack()
    status_label.pack()
    progress_bar.pack()

    convert_button.config(state='disabled')

    thread = threading.Thread(target=convert_images_to_pdf, args=(update_queue,))
    thread.start()
    root.after(100, update_labels)

def select_input_dir():
    directory = filedialog.askdirectory()
    input_dir_entry.delete(0, tk.END)
    input_dir_entry.insert(tk.END, directory)

    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(tk.END, directory)

def select_output_dir():
    directory = filedialog.askdirectory()
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(tk.END, directory)

def update_labels():
    try:
        message, data = update_queue.get(block=False)
        if message == 'folder':
            folder_label.config(text="Processing folder: " + data)
        elif message == 'file':
            file_label.config(text="Processing file: " + data)
        elif message == 'progress':
            progress_bar['value'] = data
        elif message == 'done':
            folder_label.pack_forget()
            file_label.pack_forget()
            status_label.pack_forget()
            progress_bar.pack_forget()

            convert_button.config(state='normal')

            messagebox.showinfo("Info", "Processing Complete.")
            return
    except queue.Empty:
        pass

    root.after(100, update_labels)

root = tk.Tk()
root.title("Manga Converter")
root.geometry("500x200")

frame1 = ttk.Frame(root)
frame1.pack()

input_dir_button = ttk.Button(frame1, text="Input Directory", command=select_input_dir)
input_dir_button.pack(side=tk.LEFT)

input_dir_entry = ttk.Entry(frame1, width=50)
input_dir_entry.pack(side=tk.LEFT)

frame2 = ttk.Frame(root)
frame2.pack()

output_dir_button = ttk.Button(frame2, text="Output Directory", command=select_output_dir)
output_dir_button.pack(side=tk.LEFT)

output_dir_entry = ttk.Entry(frame2, width=50)
output_dir_entry.pack(side=tk.LEFT)

frame3 = ttk.Frame(root)
frame3.pack()

quality_label = ttk.Label(frame3, text="Quality:")
quality_label.pack(side=tk.LEFT)

quality_combo = ttk.Combobox(frame3, values=["High", "Medium", "Low"], state="readonly")
quality_combo.pack(side=tk.LEFT)
quality_combo.current(2)  # Default value set to "Medium"

watermark_label = ttk.Label(frame3, text="Watermark cutoff %:")
watermark_label.pack(side=tk.LEFT)

watermark_entry = ttk.Entry(frame3, width=5)
watermark_entry.pack(side=tk.LEFT)
watermark_entry.insert(tk.END, "6.85")  # Default value

convert_button = ttk.Button(root, text="Convert", command=start_conversion)
convert_button.pack()

folder_label = ttk.Label(root, text="")
file_label = ttk.Label(root, text="")
status_label = ttk.Label(root, text="Processing, please wait...")

progress_bar = ttk.Progressbar(root, mode='determinate', maximum=100)
update_queue = queue.Queue()

root.mainloop()

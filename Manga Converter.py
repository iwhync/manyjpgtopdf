import os
import re
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import Image
from fpdf import FPDF
import threading
import queue

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key = alphanum_key)

def count_images(directory):
    total = 0
    for folder in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, folder)):
            for file in os.listdir(os.path.join(directory, folder)):
                if file.endswith('.jpg'):
                    total += 1
    return total

def convert_images_to_pdf(queue):
    base_dir = input_dir_entry.get()
    output_path = output_dir_entry.get()

    total_images = count_images(base_dir)
    processed_images = 0

    pdf = FPDF()

    for folder in natural_sort(os.listdir(base_dir)):
        queue.put(('folder', folder))

        if not os.path.isdir(os.path.join(base_dir, folder)):
            continue

        for file in natural_sort(os.listdir(os.path.join(base_dir, folder))):
            queue.put(('file', file))

            if not file.endswith('.jpg'):
                continue

            img = Image.open(os.path.join(base_dir, folder, file))

            if img.size == (0, 0):
                img.close()
                continue

            pdf.add_page()

            width, height = img.size
            aspect = width / height

            pdf_width = pdf.w
            pdf_height = pdf.h - 2*pdf.b_margin
            img_width = pdf_width
            img_height = pdf_width / aspect

            if img_height > pdf_height:
                img_width = pdf_height * aspect
                img_height = pdf_height

            pdf.image(os.path.join(base_dir, folder, file), x = pdf.l_margin, y = pdf.t_margin, w=img_width, h=img_height)

            img.close()

            processed_images += 1
            progress = 100 * processed_images / total_images
            queue.put(('progress', progress))

    output_name = os.path.basename(os.path.normpath(base_dir)) + '.pdf'
    pdf_path = os.path.join(output_path, output_name)
    pdf.output(pdf_path)

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

convert_button = ttk.Button(root, text="Convert", command=start_conversion)
convert_button.pack()

folder_label = ttk.Label(root, text="")
file_label = ttk.Label(root, text="")
status_label = ttk.Label(root, text="Processing, please wait...")

progress_bar = ttk.Progressbar(root, mode='determinate', maximum=100)
update_queue = queue.Queue()

root.mainloop()

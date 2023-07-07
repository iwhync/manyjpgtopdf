import os
import re
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import Image
from fpdf import FPDF
import threading

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key = alphanum_key)

def convert_images_to_pdf(progress_bar, status_label):
    base_dir = input_dir_entry.get()
    output_path = output_dir_entry.get()
    
    # Create a PDF object
    pdf = FPDF()

    # Iterate over each folder in the directory
    for folder in natural_sort(os.listdir(base_dir)):
        # Ensure we're only looking at folders
        if not os.path.isdir(os.path.join(base_dir, folder)):
            continue

        # Iterate over each file in the folder
        for file in natural_sort(os.listdir(os.path.join(base_dir, folder))):
            # Ensure we're only looking at .jpg files
            if not file.endswith('.jpg'):
                continue

            # Open the image file
            img = Image.open(os.path.join(base_dir, folder, file))

            # Check if the image file is blank
            if img.size == (0, 0):
                img.close()
                continue

            # Add a page to the PDF
            pdf.add_page()

            # Set the aspect ratio of the image
            width, height = img.size
            aspect = width / height

            # Determine the height and width of the image
            pdf_width = pdf.w
            pdf_height =pdf.h - 2*pdf.b_margin
            img_width = pdf_width
            img_height = pdf_width / aspect

            if img_height > pdf_height:
                img_width = pdf_height * aspect
                img_height = pdf_height

            # Add the image to the page
            pdf.image(os.path.join(base_dir, folder, file), x = pdf.l_margin, y = pdf.t_margin, w=img_width, h=img_height)

            # Close the image file
            img.close()

    # Save the PDF
    output_name = os.path.basename(os.path.normpath(base_dir)) + '.pdf'
    pdf_path = os.path.join(output_path, output_name)
    pdf.output(pdf_path) 

    progress_bar.stop()
    status_label.pack_forget()
    messagebox.showinfo("Info", "Processing Complete.")

def start_conversion():
    status_label.pack()
    progress_bar.start()
    thread = threading.Thread(target=convert_images_to_pdf, args=(progress_bar, status_label))
    thread.start()

def select_input_dir():
    directory = filedialog.askdirectory()
    input_dir_entry.delete(0, tk.END)
    input_dir_entry.insert(tk.END, directory)

def select_output_dir():
    directory = filedialog.askdirectory()
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(tk.END, directory)

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

status_label = ttk.Label(root, text="Processing, please wait...")

progress_bar = ttk.Progressbar(root, mode='indeterminate')
progress_bar.pack()

root.mainloop()

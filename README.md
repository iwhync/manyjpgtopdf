Manga Converter


Manga Converter is a Python application that converts images from multiple directories into a single PDF file. It provides a simple Graphical User Interface (GUI) to select input and output directories, and to start the conversion process.

Requirements
You'll need to have the following Python libraries installed to run this script:

tkinter for the GUI
PIL (Pillow) for handling images
fpdf for creating the PDF file
os and re for handling file paths and sorting
threading for running the conversion process in the background
You can install the necessary libraries using pip:

Copy code
pip install pillow fpdf
Tkinter is part of the standard library, so it should already be installed if you have Python. The os, re, and threading modules are also part of the standard library.

How to use
Run the script. A window titled "Manga Converter" will open.
Click the "Input Directory" button to open a file dialog. Navigate to the directory that contains the folders of images you want to convert and click OK.
Click the "Output Directory" button to open a file dialog. Navigate to the directory where you want to save the output PDF file and click OK.
Click the "Convert" button to start the conversion process. A progress bar will appear and start moving back and forth, and a message saying "Processing, please wait..." will appear. These are to indicate that the program is still running, even if it takes a while.
Once the conversion is complete, a message box will appear saying "Processing Complete.". The output PDF file will be saved in the selected output directory with the same name as the input directory.
Note
This program assumes that each folder in the input directory contains image files with the extension .jpg. Images are added to the PDF in alphanumeric order, so make sure your images are named correctly. Images with size (0, 0) are ignored. Also, the program only processes directories, any files in the root of the input directory will be ignored.

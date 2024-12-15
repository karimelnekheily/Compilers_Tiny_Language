import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import Parser
import subprocess
from node import *
from Parser import *

file_path = ""
def browse_file():
    global file_path
    file_path = filedialog.askopenfilename()
    print(file_path)
    if file_path:
        with open(file_path, 'r') as f:
            input_field.config(state='normal')
            input_field.delete(1.0, tk.END)  # Clear the Text widget first
            input_field.insert(tk.END, f.read())  # Insert the new data
            input_field.config(state='disabled')

scanErrorMsg = ""
def scan_file():
    global file_path
    global scanErrorMsg
    # Get the directory of the Python script
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Locate files when running as a PyInstaller executable
    if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller bundle
        current_dir = sys._MEIPASS  # Temporary directory where files are extracted
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))

    # Paths to Scanner.exe and jre folder
    exe_path = os.path.join(current_dir, "Scanner.exe")
    jre_path = os.path.join(current_dir, "jre")

    if file_path:
        output_file = os.path.join(os.path.dirname(file_path), "output.txt")
        args = [file_path, output_file]

        # Set the environment to use the bundled JRE
        env = os.environ.copy()
        env["JAVA_HOME"] = jre_path  # Ensure Scanner.exe uses the bundled JRE
        env["PATH"] = jre_path + os.pathsep + env["PATH"]

        # Run Scanner.exe with the updated environment
        result = subprocess.run([exe_path] + args, capture_output=True, text=True, env=env)

        # Path to the .exe in the same directory
    # exe_path = os.path.join(current_dir, "Scanner.exe")
    # if file_path:
    #     output_file = os.path.join(os.path.dirname(file_path), "output.txt")
    #     args = [file_path, output_file]
    #     result = subprocess.run([exe_path] + args, capture_output=True, text=True)
        if result.stdout:
            display_string(result.stdout)
            scanErrorMsg = result.stdout
        print("Output:", result.stdout)
        print("Errors:", result.stderr)
        if output_file:
            with open(output_file, 'r') as f:
                input_field.config(state='normal')
                input_field.delete(1.0, tk.END)  # Clear the Text widget first
                input_field.insert(tk.END, f.read())  # Insert the new data
                input_field.config(state='disabled')

errorState = False # global variable states if there is an error
def generate_canvas():
    global list_of_tokens
    global errorState
    errorState = False
    input_content = input_field.get("1.0", "end")
    graph_area.delete("all")
    Parser.list_of_tokens = split_input(input_content)
    print(Parser.list_of_tokens)
    root_node = program()
    if root_node.isError:
        errorState = True
        display_string(root_node.data)
    else:
        draw_canvas(root_node, 100, 50, 100, 100)


def display_string(text):
    # graph_area.create_text(300, 20, text=text, anchor="center" , fill="red", font=("Helvetica", 12))
    graph_area.delete("all")
    canvas_width = graph_area.winfo_width()
    canvas_height = graph_area.winfo_height()
    font_size = min(canvas_width // 20, canvas_height // 20)
    graph_area.create_text(canvas_width // 2, canvas_height // 2, text=text, anchor="center", fill="red",
                           font=("Helvetica", font_size))


def split_input(input_content):
    return [tuple(item.strip() for item in line.split(','))
            for line in input_content.split('\n') if line.strip()]


def draw_canvas(node: Node, x: int, y: int, spacing_x: int, spacing_y: int) -> int:
    # Accumulate x for correct horizontal positioning
    child_x = x
    child_y = y + spacing_y
    for child in node.children:
        graph_area.create_line(x, y - 5, child_x, child_y - 5, fill="white")
        child_x = draw_canvas(child, child_x, child_y, spacing_x, spacing_y) + spacing_x
    if (len(node.children) >= 1):
        child_x -= spacing_x

    if node.next:
        next_x = child_x + spacing_x
        next_y = y
        graph_area.create_line(x + 20, y, next_x - 20, next_y, fill="white")
        child_x = draw_canvas(node.next, next_x, next_y, spacing_x, spacing_y)

    # Differentiate square and oval with background and border colors
    if node.is_square:
        graph_area.create_rectangle(
            x - 30, y - 30, x + 30, y + 30, fill="white", outline="red"
        )
    else:
        graph_area.create_oval(
            x - 40, y - 20, x + 40, y + 20, fill="white", outline="blue"
        )

    graph_area.create_text(x, y, text=node.data, anchor="center")
    return child_x


# Update the text size when the canvas size changes
def update_text_size(event):
    if errorFlag:
        display_string(errorNode.data)
    elif errorState:
        display_string(scanErrorMsg)


# Update the scroll region when the canvas size changes
def configure_scroll_region(event):
    graph_area.configure(scrollregion=graph_area.bbox("all"))


root = tk.Tk()
root.title("Tiny Language Parser")

# Apply the dark mode theme
root.configure(bg='#2c2c2c')
style = ttk.Style(root)
style.theme_use('clam')
style.configure('TLabel', background='#2c2c2c', foreground='white')
style.configure('TButton', background='#4c4c4c', foreground='white', borderwidth=0)

# Create the input text field
# Create a Text widget for multiline input
input_field = tk.Text(root, wrap="word", font=('Courier', 12),
                      bg='#2c2c2c', fg='white', insertbackground='white',
                      width=30,
                      highlightbackground='white', highlightcolor='white', highlightthickness=2)
input_field.grid(row=0, column=0, padx=10, pady=10, sticky='ns')
input_field.config(state='disabled')

'''My Test code for scrollable canvas'''
# Create the graph area with scrollbars
graph_frame = tk.Frame(root, bg='#2c2c2c')
graph_frame.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky='nsew')

# Create the canvas
graph_area = tk.Canvas(graph_frame, bg='#2c2c2c')
graph_area.grid(row=0, column=0, sticky='nsew')

# Create the scrollbars
h_scrollbar = tk.Scrollbar(graph_frame, orient=tk.HORIZONTAL, command=graph_area.xview)
h_scrollbar.grid(row=1, column=0, sticky='ew')
v_scrollbar = tk.Scrollbar(graph_frame, orient=tk.VERTICAL, command=graph_area.yview)
v_scrollbar.grid(row=0, column=1, sticky='ns')

# Configure the canvas to use the scrollbars
graph_area.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

# Make the canvas expandable
graph_frame.rowconfigure(0, weight=1)
graph_frame.columnconfigure(0, weight=1)

graph_area.bind("<Configure>", configure_scroll_region)
# displays string if error
if errorFlag or errorState:
    graph_area.bind("<Configure>", update_text_size)

'''Andrew's code use it if mine blows up'''
# # Create the graph area
# graph_area = tk.Canvas(graph_frame, bg='#2c2c2c')
# graph_area.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky='nsew')

# Create the "Browse" button
browse_button = ttk.Button(root, text="Browse", command=browse_file)
browse_button.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

# Create the "Draw" button
draw_button = ttk.Button(root, text="Draw", width=40, command=generate_canvas)
draw_button.grid(row=1, column=2, padx=10, pady=10, sticky='nsew')

# Create the "Scan" button
draw_button = ttk.Button(root, text="Scan", width=40, command=scan_file)
draw_button.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')

# Create the logo image
logo_image = Image.open("logo.png")
logo_image = logo_image.resize((150, 77), resample=Image.BICUBIC)
logo_photo = ImageTk.PhotoImage(logo_image)
logo_label = ttk.Label(root, image=logo_photo, background='#2c2c2c')
logo_label.grid(row=1, column=3, padx=10, pady=10, sticky='nsew')

# Make the labels and buttons resize with the window
root.rowconfigure(0, weight=1)

# root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

root.mainloop()

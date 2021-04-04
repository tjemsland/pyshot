#!/usr/bin/env python3

from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from subprocess import run
from datetime import datetime
from os import path

HOME = path.expanduser("~")
cache_file = HOME+"/.cache/pyshot"
preview_size = 500
max_cached = 20
tmp_num = 0
def time_string():
	ct = datetime.now()
	return f"{ct.day:02d}{ct.month:02d}{ct.year}-" + \
	f"{ct.hour:02d}{ct.minute:02d}{ct.second:02d}"

def string_to_integer(string):
	try:
		return int(string)
	except:
		return 0




class Win(Tk):
	"""https://stackoverflow.com/questions/29641616/drag-window-when-using-overrideredirect"""
	def __init__(self,master=None):
		Toplevel.__init__(self,master)
		self.overrideredirect(True)
		self._offsetx = 0
		self._offsety = 0
		self.bind('<Button-1>',self.clickwin)
		self.bind('<B1-Motion>',self.dragwin)
	def dragwin(self,event):
		x = self.winfo_pointerx() - self._offsetx
		y = self.winfo_pointery() - self._offsety
		self.geometry('+{x}+{y}'.format(x=x,y=y))

	def clickwin(self,event):
		self._offsetx = event.x
		self._offsety = event.y



# Default parameters
save_path = HOME+"/Pictures/Screenshots"
filename = f"pyshot-{time_string()}.png"



## Window objects
window = Tk()
window.title("Pyshot")
selected = IntVar()
rad1 = Radiobutton(window,text='Full', value=1, variable=selected)
rad2 = Radiobutton(window,text='Window', value=2, variable=selected)
rad3 = Radiobutton(window,text='Selection', value=3, variable=selected)
file_string = StringVar()
toggled = IntVar()
toggled2 = IntVar()
tog = Checkbutton(window, text="Multiuse", variable=toggled)
tog2 = Checkbutton(window, text="Preview", variable=toggled2)
txt1 = Entry(window, width=50, textvariable=file_string)
delay_string = StringVar()
delay_entry = Entry(window, width=5, textvariable=delay_string)
delay_label = Label(window, text="Delay (s):")

# Create cache if not already existing
run("touch "+cache_file, shell=True)
# Read cache file
cache = open(path.relpath(cache_file), "r")
content = cache.read().split("\n")
if len(content) < 5: # File corrupted or not existing
	print(f"Creating new cache file '{cache_file}'.")
	cache.close(); cache = open(path.relpath(cache_file), "w")
	cache.truncate()
	run("mkdir "+save_path, shell=True)
	cache.write(save_path+"\n1\n0\n0\n0")
	cache.close(); cache = open(path.relpath(cache_file), "r")	
	content = cache.read().split("\n")
save_path = content[0]
selected.set(int(content[1]))
delay_string.set(content[2])
toggled.set(int(content[3]))
toggled2.set(int(content[4]))
file_string.set(save_path+"/"+filename)

# Main button GO!
def clicked():
	global tmp_num 
	window.withdraw()
	mode = selected.get()
	file = file_string.get()
	ext = file.split(".")[-1]
	tmp = HOME+f"/.cache/pyshot-tmp{tmp_num}."+ext
	tmp_num  += 1
	if tmp_num >= max_cached: tmp_num = 0
	print("Saving ", tmp)
	delay_string.set(string_to_integer(delay_string.get()))
	delay = int(delay_string.get())
	if (mode == 1):
		run(f"scrot {tmp} -d {delay}", shell=True)
	elif (mode == 2):
		run(f"scrot {tmp} -u -d {delay}", shell=True)
	elif (mode == 3):
		run(f"scrot {tmp} -s -d {delay}", shell=True)

	if not toggled.get() == 0: window.deiconify()

	keep_flag = True
	# Preview
	if (toggled2.get() == 1):
		from PIL import Image, ImageTk
		# Preview window
		preview = Win()
		preview.overrideredirect(True)
		preview.title("Preview")
		#canvas.pack()
		# Open Image
		img = Image.open(path.relpath(tmp))
		# Find dimensions
		width, height = img.size
		# Find resized dimensions
		if height > width:
			width = int(preview_size*width/float(height))
			height = preview_size 
		else:
			height = int(preview_size*height/float(width))
			width = preview_size
		canvas = Canvas(preview, width=width, height=height)
		# Resize and define Tk image
		img = ImageTk.PhotoImage(img.resize((width, height)))
		# Show image
		canvas.create_image(0, 0, anchor=NW, image=img)
		
		# Buttons
		def do_keep():
			global keep_flag
			keep_flag = True
			preview.destroy()
			if toggled.get() == 0: window.destroy()
			else: window.deiconify()
			print(f"and moving it to {file}")
			run(f"mv {tmp} {file}", shell=True)
		btn_keep = Button(preview, text="Keep!", command=do_keep)
		def do_not_keep(): 
			global keep_flag
			keep_flag=False
			preview.destroy()
			window.deiconify()
		btn_delete = Button(preview, text="Try again!", command=do_not_keep)
		
		# Text
		text = StringVar()
		text.set(file)
		preview_text = Message(preview, textvariable=text, width=preview_size*0.9)

		# Setup
		canvas.grid(column=0, row=0, columnspan=2)
		preview_text.grid(column=0, row=1, columnspan=2)
		btn_keep.grid(column=0, row=2)
		btn_delete.grid(column=1, row=2)

		preview.mainloop()
	else:
		print(f"and moving it to {file}")
		run(f"mv {tmp} {file}", shell=True)
		if toggled.get() == 0: window.destroy()
btn = Button(window, text="Go!", command=clicked)

# Open file GUI button
def open_file():
	title = "Save as"
	#initdir = save_path
	initdir = file_string.get().rsplit("/", 1)[0] 
	filetypes = (("png","*.png"),("jpg","*.jpg"),("all files","*"))
	file_choice = filedialog.asksaveasfilename(initialdir=initdir,
		title=title,filetypes=filetypes)
	if len(file_choice) > 0:
		file_string.set(file_choice)	
btn_file = Button(window, text="Choose file", command=open_file)

# Window setup
rad1.grid(column=0, row=0)
rad2.grid(column=1, row=0)
rad3.grid(column=2, row=0)
btn.grid(column=2, row=3)
txt1.grid(column=0, columnspan=3, row=1)
btn_file.grid(column=3, row=1)
tog.grid(column=0, row=3)
tog2.grid(column=1, row=3)
delay_entry.grid(column=4, row=0)
delay_label.grid(column=3, row=0)
window.mainloop()

# Save state for next use
with open(path.relpath(cache_file), "w") as f:
	f.truncate()
	# Find folder
	folder = file_string.get().rsplit("/", 1)[0]
	screenshot_type = str(selected.get())
	delay = str(string_to_integer(delay_string.get()))
	multiuse = str(toggled.get())
	preview = str(toggled2.get())
	f.write(f"{folder}\n{screenshot_type}\n{delay}\n{multiuse}\n{preview}")

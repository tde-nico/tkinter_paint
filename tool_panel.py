import customtkinter as ctk
from settings import *
from PIL import Image
from tkinter import Canvas

class ToolPanel(ctk.CTkToplevel):
	def __init__(self, parent, brush_float, color_string, erase_bool, clear_canvas):
		super().__init__()
		self.geometry('200x300')
		self.title('')
		self.resizable(False, False)
		self.iconbitmap('empty.ico')
		self.attributes('-topmost', True)
		self.protocol('WM_DELETE_WINDOW', self.close_app)
		self.parent = parent

		# layout 
		self.columnconfigure((0,1,2), weight = 1, uniform = 'a')
		self.rowconfigure(0, weight = 2, uniform = 'a')
		self.rowconfigure(1, weight = 3, uniform = 'a')
		self.rowconfigure((2,3), weight = 1, uniform = 'a')

		# widgets 
		BrushPreview(self, color_string, brush_float, erase_bool)
		ColorSliderPanel(self, color_string, erase_bool)
		BrushSizeSlider(self, brush_float)
		ColorPanel(self,color_string, erase_bool)
		DrawBrushButton(self, erase_bool)
		EraserButton(self, erase_bool)
		ClearAllButton(self, clear_canvas,erase_bool)

	def close_app(self):
		self.parent.quit()

class BrushPreview(Canvas):
	def __init__(self, parent, color_string, brush_float, erase_bool):
		super().__init__(master = parent, background = BRUSH_PREVIEW_BG, bd = 0, highlightthickness = 0, relief = 'ridge')
		self.grid(row = 0, column = 1, columnspan = 2, sticky = 'nsew')

		# data 
		self.color_string = color_string
		self.brush_float = brush_float
		self.erase_bool = erase_bool

		# canvas setup
		self.x = 0
		self.y = 0
		self.max_length = 0

		# trace
		self.brush_float.trace('w', self.update)
		self.color_string.trace('w', self.update)
		self.erase_bool.trace('w', self.update)

		self.bind('<Configure>', self.setup)

	def setup(self, event):
		self.x = event.width / 2
		self.y = event.height / 2
		self.max_length = (event.height / 2) * 0.8
		self.update()

	def update(self, *args):
		self.delete('all')
		current_radius = self.max_length * self.brush_float.get()
		color = f'#{self.color_string.get()}' if not self.erase_bool.get() else BRUSH_PREVIEW_BG
		outline_color = f'#{self.color_string.get()}' if not self.erase_bool.get() else 'black'
		self.create_oval(
			self.x - current_radius,
			self.y - current_radius, 
			self.x + current_radius,
			self.y + current_radius, 
			fill = color, 
			outline = outline_color,
			dash = 20)

class ColorSliderPanel(ctk.CTkFrame):
	def __init__(self, parent, color_string, erase_bool):
		super().__init__(master = parent)
		self.grid(row = 0, column = 0, sticky = 'nsew', padx = 5, pady = 5)

		# data 
		self.color_string = color_string
		self.r_int = ctk.IntVar(value = self.color_string.get()[0])
		self.g_int = ctk.IntVar(value = self.color_string.get()[1])
		self.b_int = ctk.IntVar(value = self.color_string.get()[2])
		self.color_string.trace('w', self.set_color)
		self.erase_bool = erase_bool

		# layout 
		self.rowconfigure((0,1,2), weight = 1, uniform = 'a')
		self.columnconfigure(0, weight = 1, uniform = 'a')

		# widgets 
		ctk.CTkSlider(self, from_ = 0, to = 15, number_of_steps = 16, command = lambda value: self.set_single_color('r', value),variable = self.r_int, button_color = SLIDER_RED, button_hover_color = SLIDER_RED).grid(column = 0, row = 0, padx = 2)
		ctk.CTkSlider(self, from_ = 0, to = 15, number_of_steps = 16, command = lambda value: self.set_single_color('g', value),variable = self.g_int, button_color = SLIDER_GREEN, button_hover_color = SLIDER_GREEN).grid(column = 0, row = 1, padx = 2)
		ctk.CTkSlider(self, from_ = 0, to = 15, number_of_steps = 16, command = lambda value: self.set_single_color('b', value),variable = self.b_int, button_color = SLIDER_BLUE, button_hover_color = SLIDER_BLUE).grid(column = 0, row = 2, padx = 2)

	def set_single_color(self, color, value):
		current_color_list = list(self.color_string.get()) #F00 -> ['F', '0', '0']

		if color == 'r': current_color_list[0] = COLOR_RANGE[int(value)] # ['9', '0', '0']
		elif color == 'g': current_color_list[1] = COLOR_RANGE[int(value)]
		elif color == 'b': current_color_list[2] = COLOR_RANGE[int(value)]
		self.color_string.set(f'{"".join(current_color_list)}')# ['9', '0', '0'] -> '900'

		self.erase_bool.set(False)

	def set_color(self, *args):
		self.r_int.set(COLOR_RANGE.index(self.color_string.get()[0])) # ??? 0 -> F / 0 -> 15
		self.g_int.set(COLOR_RANGE.index(self.color_string.get()[1])) # ???
		self.b_int.set(COLOR_RANGE.index(self.color_string.get()[2])) # ???

class ColorPanel(ctk.CTkFrame):
	def __init__(self, parent, color_string, erase_bool):
		super().__init__(master = parent, fg_color = 'transparent')
		self.grid(row = 1, column = 0, columnspan = 3, pady = 5, padx = 5)
		self.color_string = color_string

		# layout
		self.rowconfigure([row for row in range(COLOR_ROWS)], weight = 1, uniform = 'a')
		self.columnconfigure([col for col in range(COLOR_COLS)], weight = 1, uniform = 'a')

		# widgets 
		for row in range(COLOR_ROWS):
			for col in range(COLOR_COLS):
				color = COLORS[row][col]
				ColorFieldButton(self, row, col, color, self.pick_color, erase_bool)

	def pick_color(self, color):
		self.color_string.set(color)

class ColorFieldButton(ctk.CTkButton):
	def __init__(self, parent, row, col, color, pick_color, erase_bool):
		super().__init__(
			master = parent, 
			text = '', 
			fg_color = f'#{color}', 
			hover_color = f'#{color}',
			corner_radius = 1,
			command = self.click_handler)
		self.grid(row = row, column = col, padx = 0.4, pady = 0.4)

		self.pick_color = pick_color
		self.color = color
		self.erase_bool = erase_bool

	def click_handler(self):
		self.pick_color(self.color)
		self.erase_bool.set(False)

class BrushSizeSlider(ctk.CTkFrame):
	def __init__(self, parent, brush_float):
		super().__init__(master = parent)
		self.grid(row = 2, column = 0, columnspan = 3, sticky = 'nsew', pady = 5, padx = 5)
		ctk.CTkSlider(self, variable = brush_float, from_ = 0.2, to = 1).pack(fill = 'x', expand = True, padx = 5)

class Button(ctk.CTkButton):
	def __init__(self, parent, image_path, col, func):
		image = ctk.CTkImage(light_image = Image.open(image_path), dark_image = Image.open(image_path))
		super().__init__(master = parent,command = func, text = '', image = image, fg_color = BUTTON_COLOR, hover_color = BUTTON_HOVER_COLOR)
		self.grid(row = 3, column = col, sticky = 'nsew', padx = 5, pady = 5)

class DrawBrushButton(Button):
	def __init__(self, parent, erase_bool):
		super().__init__(parent = parent, image_path = 'images/brush.png', col = 0, func = self.activate_paint)
		self.erase_bool = erase_bool
		self.erase_bool.trace('w', self.update_state)

	def activate_paint(self):
		self.erase_bool.set(False)

	def update_state(self, *args):
		if not self.erase_bool.get(): # active
			self.configure(fg_color = BUTTON_ACTIVE_COLOR)
		else: # passive
			self.configure(fg_color = BUTTON_COLOR)

class EraserButton(Button):
	def __init__(self, parent, erase_bool):
		super().__init__(parent = parent, image_path = 'images/eraser.png', col = 1, func = self.activate_erase)
		self.erase_bool = erase_bool
		self.erase_bool.trace('w', self.update_state)

	def activate_erase(self):
		self.erase_bool.set(True)

	def update_state(self, *args):
		if self.erase_bool.get(): # active
			self.configure(fg_color = BUTTON_ACTIVE_COLOR)
		else: # passive
			self.configure(fg_color = BUTTON_COLOR)

class ClearAllButton(Button):
	def __init__(self, parent, clear_canvas, erase_bool):
		super().__init__(parent = parent, image_path = 'images/clear.png', col = 2, func = self.clear_all)

		self.clear_canvas = clear_canvas
		self.erase_bool = erase_bool

	def clear_all(self):
		self.clear_canvas()
		self.erase_bool.set(False)

#!/usr/bin/env python
"""
Calendar.py - darkliquid <darkliquid@darkliquid.co.uk>, 2005

Simple, adesklets calendar script:
Basically, this should simply grab the output
of the calendar.month() function and display
on the screen using the fonts defined from the
config file. Eventually, I plan to add more
functionality to this so that different fonts
for various parts can be altered and then who knows?

"""
import adesklets
import math
import xml.dom.minidom
import calendar
import datetime

have_tkinter=False

try:
	from Tkinter import *
	have_tkinter=True
except ImportError:
	have_tkinter=False
from os import getenv, spawnlp, P_NOWAIT
from os.path import join, dirname

class Config(adesklets.ConfigFile):
	"""
	This is Calendar.py desklet configuration file;
	"""

	cfg_default = { 'heading_font': 'Vera',
					'heading_font_size': 14,
					'heading_font_color': '000000',
					'heading_bg_color': 'FFFFFF',
					'heading_border_color': '000000',
					'day_font': 'Vera',
					'day_font_size': 12,
					'day_font_color': '000000',
					'day_bg_color': 'AAAAAA',
					'day_border_color': '000000',
					'date_font': 'Vera',
					'date_font_size': 12,
					'date_font_color': 'AAAAAA',
					'date_bg_color': '555555',
					'date_border_color': '000000',
					'date_past_font': 'Vera',
					'date_past_font_size': 12,
					'date_past_font_color': 'AAAAAA99',
					'date_past_bg_color': '55555599',
					'date_past_border_color': '00000099',
					'date_today_font': 'VeraBd',
					'date_today_font_size': 12,
					'date_today_font_color': 'FFFFFF',
					'date_today_bg_color': '555555',
					'date_today_border_color': '000000',
					'cell_padding': 2,
					'first_day_of_week': 0,
					'delay': 3600,
					'month_offset': 0,
					'year_offset': 0,
					'month_offset_negative': False,
					'year_offset_negative': False }

	def __init__(self,id,filename):
		adesklets.ConfigFile.__init__(self,id,filename)

	def color(self,string):
		colors = [eval('0x%s' % string[i*2:i*2+2]) for i in range(len(string)/2)]
		if (len(colors) != 4): colors += [255]
		return colors

#------------------------------------------------------------------------------

class CalendarDesklet(object):
	"""
	Class that generates a calendar on the desktop
	This is a base class from which themes can inherit
	"""

	def __init__(self, config):
		""" Does things that should be done at instantisation """
		self.config = config
		self._month_offset = 0
		self._year_offset = 0

	def __call__(self):
		""" Build todays calendar, set up fonts and stuff """

		self._month_offset = self.config['month_offset']
		if (self.config['month_offset_negative']):
			self._month_offset = self._month_offset * -1
		self._year_offset = self.config['year_offset']
		if (self.config['year_offset_negative']):
			self._year_offset = self._year_offset * -1
		self.update()

		# Load cell attributes
		self._heading_font = adesklets.load_font('%s/%d' % (self.config['heading_font'],
															self.config['heading_font_size']))

		self._heading_font_color = (self.config.color(self.config['heading_font_color']))
		self._heading_bg_color = (self.config.color(self.config['heading_bg_color']))
		self._heading_border_color = (self.config.color(self.config['heading_border_color']))

		self._day_font = adesklets.load_font('%s/%d' % (self.config['day_font'],
														self.config['day_font_size']))

		self._day_font_color = (self.config.color(self.config['day_font_color']))
		self._day_bg_color = (self.config.color(self.config['day_bg_color']))
		self._day_border_color = (self.config.color(self.config['day_border_color']))

		self._date_font = adesklets.load_font('%s/%d' % (self.config['date_font'],
														 self.config['date_font_size']))

		self._date_font_color = (self.config.color(self.config['date_font_color']))
		self._date_bg_color = (self.config.color(self.config['date_bg_color']))
		self._date_border_color = (self.config.color(self.config['date_border_color']))

		self._date_today_font = adesklets.load_font('%s/%d' % (self.config['date_today_font'],
														 self.config['date_today_font_size']))

		self._date_today_font_color = (self.config.color(self.config['date_today_font_color']))
		self._date_today_bg_color = (self.config.color(self.config['date_today_bg_color']))
		self._date_today_border_color = (self.config.color(self.config['date_today_border_color']))

		self._date_past_font = adesklets.load_font('%s/%d' % (self.config['date_past_font'],
														 self.config['date_past_font_size']))

		self._date_past_font_color = (self.config.color(self.config['date_past_font_color']))
		self._date_past_bg_color = (self.config.color(self.config['date_past_bg_color']))
		self._date_past_border_color = (self.config.color(self.config['date_past_border_color']))

		# Get other calendar attributes
		self._cell_padding = self.config['cell_padding']

		# Set up window properties
		adesklets.window_set_transparency(True)
		adesklets.menu_add_separator()
		adesklets.menu_add_item('Configure')
		if have_tkinter:
			adesklets.menu_add_separator()
			adesklets.menu_add_item('Add_DateNote')
			adesklets.menu_add_item('Edit_DateNote')
			adesklets.menu_add_item('Remove_DateNotes')
		adesklets.menu_add_separator()
		adesklets.menu_add_item('Prev_Month')
		adesklets.menu_add_item('Next_Month')
		adesklets.menu_add_item('Prev_Year')
		adesklets.menu_add_item('Next_Year')
		adesklets.window_show()

	def __buildcal(self, cal):
		""" Build a given calendar in a usable format """
		cal_list = cal.splitlines()
		new_cal = []
		temp_list = []

		for row in xrange(0,len(cal_list)):
			if (row == 0):
				new_cal.append(cal_list[row:row+1][0].strip())
			else:
				for col in xrange(0,21,3):
					temp_list.append(cal_list[row:row+1][0][col:col+3].strip())
				new_cal.append(temp_list)
				temp_list = []

		return new_cal

	def __getcellsize(self):
		"""
		This function determines the minimum required cell size to display
		the characters within a cell without overlapping into other cells.
		It determines this by finding the maximum widths and heights in the
		list of cell data (ie: day numbers or days names). It then takes the
		maximum of the final max width and height and returns that (we want
		square cells, right?)
		"""
		
		old_w = 0
		old_h = 0
		w = 0
		h = 0


		for font in xrange(self._heading_font,self._date_past_font+1):
			adesklets.context_set_font(font)

			for row in xrange(1,len(self._cal)):
				for col in xrange(0,7):
					if (len(self._cal[row:row+1][0][col:col+1][0]) > 0):
						old_w,old_h = adesklets.get_text_size(self._cal[row:row+1][0][col:col+1][0])
						w=max(w,old_w)
						h=max(h,old_h)

		return (max(w,h) + self._cell_padding + 1)

	def __render_heading_cell(self,cell):
		# Set up a drawing buffer for the heading
		buffer = adesklets.create_image(self._calsize,self._cellsize)
		adesklets.context_set_image(buffer)
		adesklets.context_set_blend(False)
		adesklets.context_set_color(0,0,0,0)
		adesklets.image_fill_rectangle(0,0,self._calsize,self._cellsize)
		adesklets.context_set_blend(True)

		# Draws the heading background
		adesklets.context_set_color(*self._heading_bg_color)
		adesklets.image_fill_rectangle(self._cell_padding, self._cell_padding,
										   (self._calsize - self._cell_padding), (self._cellsize - self._cell_padding))

		# Draws the heading border
		adesklets.context_set_color(*self._heading_border_color)
		adesklets.image_draw_rectangle(self._cell_padding, self._cell_padding,
									  (self._calsize - self._cell_padding), (self._cellsize - self._cell_padding))

		# Draws the heading text
		adesklets.context_set_font(self._heading_font)
		x, y = adesklets.get_text_size(cell)
		adesklets.context_set_color(*self._heading_font_color)
		adesklets.text_draw(((self._calsize / 2) - (x / 2)),((self._cellsize / 2) - (y / 2)),cell)

		# Blend heading image into main buffer
		adesklets.context_set_image(self._buffer)
		adesklets.blend_image_onto_image(buffer,1,0,0,self._calsize,(self._cellsize + self._cell_padding + 2),
										 0,0,self._calsize,(self._cellsize + self._cell_padding + 2))
		adesklets.free_image(buffer)


	def __render_day_cell(self, cell, col):
		# Set up a drawing buffer for the day cell
		buffer = adesklets.create_image(self._cellsize, self._cellsize)
		adesklets.context_set_image(buffer)
		adesklets.context_set_blend(False)
		adesklets.context_set_color(0,0,0,0)
		adesklets.image_fill_rectangle(0,0,self._cellsize,self._cellsize)
		adesklets.context_set_blend(True)

		# Draws the day cell background
		adesklets.context_set_color(*self._day_bg_color)
		adesklets.image_fill_rectangle(self._cell_padding, self._cell_padding,
										   (self._cellsize - self._cell_padding), (self._cellsize - self._cell_padding))

		# Draws the day cell border
		adesklets.context_set_color(*self._day_border_color)
		adesklets.image_draw_rectangle(self._cell_padding, self._cell_padding,
									  (self._cellsize - self._cell_padding), (self._cellsize - self._cell_padding))

		# Draws the day cell text
		adesklets.context_set_font(self._day_font)
		x, y = adesklets.get_text_size(cell)
		adesklets.context_set_color(*self._day_font_color)
		adesklets.text_draw(((self._cellsize / 2) - (x / 2)),((self._cellsize / 2) - (y / 2)),cell)

		# Blend day cell image into main buffer
		adesklets.context_set_image(self._buffer)
		adesklets.blend_image_onto_image(buffer,1,0,0,self._cellsize,self._cellsize,
										 (col * self._cellsize),self._cellsize,self._cellsize,self._cellsize)
		adesklets.free_image(buffer)

	def __render_date_cell(self, cell, col, row):
		# Set up a drawing buffer for the date
		buffer = adesklets.create_image(self._cellsize, self._cellsize)
		adesklets.context_set_image(buffer)
		adesklets.context_set_blend(False)
		adesklets.context_set_color(0,0,0,0)
		adesklets.image_fill_rectangle(0,0,self._cellsize,self._cellsize)
		adesklets.context_set_blend(True)

		# Draws the date cell background
		if (int(cell) == int(datetime.date.today().day)):
			adesklets.context_set_color(*self._date_today_bg_color)
		elif (int(cell) < int(datetime.date.today().day)):
			adesklets.context_set_color(*self._date_past_bg_color)
		else:
			adesklets.context_set_color(*self._date_bg_color)
		if self._month_offset<0 or self._year_offset<0:
			adesklets.context_set_color(*self._date_past_bg_color)
		elif self._month_offset>0 or self._year_offset>0:
			adesklets.context_set_color(*self._date_bg_color)

		adesklets.image_fill_rectangle(self._cell_padding, self._cell_padding,
										   (self._cellsize - self._cell_padding), (self._cellsize - self._cell_padding))

		# Draws the date cell border
		if (int(cell) == int(datetime.date.today().day)):
			adesklets.context_set_color(*self._date_today_border_color)
		elif (int(cell) < int(datetime.date.today().day)):
			adesklets.context_set_color(*self._date_past_border_color)
		else:
			adesklets.context_set_color(*self._date_border_color)
		if self._month_offset<0 or self._year_offset<0:
			adesklets.context_set_color(*self._date_past_border_color)
		elif self._month_offset>0 or self._year_offset>0:
			adesklets.context_set_color(*self._date_border_color)

		adesklets.image_draw_rectangle(self._cell_padding, self._cell_padding,
									  (self._cellsize - self._cell_padding), (self._cellsize - self._cell_padding))

		# Draws the date cell text
		if (int(cell) == int(datetime.date.today().day)):
			adesklets.context_set_font(self._date_today_font)
			adesklets.context_set_color(*self._date_today_font_color)
		elif (int(cell) < int(datetime.date.today().day)):
			adesklets.context_set_font(self._date_past_font)
			adesklets.context_set_color(*self._date_past_font_color)
		else:
			adesklets.context_set_font(self._date_font)
			adesklets.context_set_color(*self._date_font_color)
		if self._month_offset<0 or self._year_offset<0:
			adesklets.context_set_font(self._date_past_font)
			adesklets.context_set_color(*self._date_past_font_color)
		elif self._month_offset>0 or self._year_offset>0:
			adesklets.context_set_font(self._date_font)
			adesklets.context_set_color(*self._date_font_color)

		x, y = adesklets.get_text_size(cell)
		adesklets.text_draw(((self._cellsize / 2) - (x / 2)),((self._cellsize / 2) - (y / 2)),cell)

		# Blend date cell image into main buffer
		adesklets.context_set_image(self._buffer)
		adesklets.blend_image_onto_image(buffer,1,0,0,self._cellsize,self._cellsize,
										 (col * self._cellsize),(row * self._cellsize),self._cellsize,self._cellsize)
		adesklets.free_image(buffer)

	def display(self):
		"""
		The main drawing routine
		"""
		# Get cell dimensions
		self._cellsize = self.__getcellsize()
		adesklets.context_set_image(0)

		# Calc calendar dimensions
		self._calsize = (self._cellsize * 7)

		# Set up a buffer
		self._buffer = adesklets.create_image(self._calsize,self._calsize+self._cellsize)
		adesklets.context_set_image(self._buffer)
		adesklets.context_set_blend(False)
		adesklets.context_set_color(0,0,0,0)
		adesklets.image_fill_rectangle(0,0,self._calsize,self._calsize)
		adesklets.context_set_blend(True)

		# Draw heading
		self.__render_heading_cell(self._cal[0:1][0])

		# Draw the days
		for col in xrange(0,7):
			self.__render_day_cell(self._cal[1:2][0][col:col+1],col)

		# This draws the rest
		for row in xrange(2,len(self._cal)):
			for col in xrange(0,7):
				if (len(self._cal[row:row+1][0][col:col+1][0]) > 0):
					self.__render_date_cell(self._cal[row:row+1][0][col:col+1][0], col, row)
				
		# Resize window and put everything on foreground
		adesklets.context_set_image(0)
		if self._calsize != adesklets.image_get_width() or self._calsize+self._cellsize != adesklets.image_get_height():
			adesklets.window_resize(self._calsize,self._calsize+self._cellsize)
		adesklets.context_set_blend(False)
		adesklets.blend_image_onto_image(self._buffer,1,0,0,self._calsize,self._calsize+self._cellsize,0,0,self._calsize,self._calsize+self._cellsize)
		adesklets.free_image(self._buffer)

	def update(self):
		calendar.setfirstweekday(int(self.config['first_day_of_week']))
		now = datetime.date.today()

		if ((now.month+self._month_offset)>12):
			self._month_offset=1-now.month
			self._year_offset+=1
		if ((now.month+self._month_offset)<1):
			self._month_offset=12-now.month
			self._year_offset-=1

		year = now.year+self._year_offset
		month =  now.month+self._month_offset
		print year, month
		print self._year_offset, self._month_offset

		self._cal = self.__buildcal(calendar.month(year, month))

	def get_date_from_coords(self,x,y):
		col = x/self._cellsize
		row = y/self._cellsize

		if (row > 1):
			try:
				if (self._cal[row:row+1][0][col:col+1][0] != ''):
					return [self._cal[row:row+1][0][col:col+1][0],self._cal[0].split(" ")[0],self._cal[0].split(" ")[1]]
			except IndexError:
				return -1
			else:
				return -1
		else:
			return -1

	def set_month_offset(self, offset, type=None):
		if type == None:
			self._month_offset = offset
		elif type == "-":
			self._month_offset -= offset
		elif type == "+":
			self._month_offset += offset
		self.update()
		self.display()

	def set_year_offset(self, offset, type=None):
		if type == None:
			self._year_offset = offset
		elif type == "-":
			self._year_offset -= offset
		elif type == "+":
			self._year_offset += offset
		self.update()
		self.display()


#-----------------------------------------------------------------------------
if have_tkinter:
	class EntryBox:
		""" Simple text entry box for adding/editing/displaying datenotes """
		def __init__(self,title,text_entry):
			# Add time edit box later
			self.root = Tk()
			self.root.title(title)
			self.return_text=""
			self.frame = Frame(self.root)
			self.frame.pack()
			self.textedit = Text(self.frame)
			self.textedit.insert(END, text_entry)
			self.textedit.pack(side=TOP)
			self.button = Button(self.frame, text = "Save", command=self.quit)
			self.button.pack(side=BOTTOM)
	
		def __call__(self):
			self.root.mainloop()
			# Add return of time edit box data later
			return self.return_text
			
		def quit(self):
			self.return_text = self.textedit.get(1.0, END)
			self.root.destroy()

#-----------------------------------------------------------------------------

class DateNotes:
	""" The class parses and generates the dates.xml file which contains
		all the todos, reminders, etc
		It provides methods to get the current entries for a given date and
		methods to add and remove entries. """
	def __init__(self):
		self._doc=""
		self._root=""
		self.__update()

	def remove_whitespace_nodes(self, node, unlink=False):
		"""Removes all of the whitespace-only text decendants of a DOM node.
    
		When creating a DOM from an XML source, XML parsers are required to
		consider several conditions when deciding whether to include
		whitespace-only text nodes. This function ignores all of those
		conditions and removes all whitespace-only text decendants of the
		specified node. If the unlink flag is specified, the removed text
		nodes are unlinked so that their storage can be reclaimed. If the
		specified node is a whitespace-only text node then it is left
		unmodified."""
    
		remove_list = []
		for child in node.childNodes:
			if child.nodeType == xml.dom.Node.TEXT_NODE and	not child.data.strip():
				remove_list.append(child)
			elif child.hasChildNodes():
				self.remove_whitespace_nodes(child, unlink)
		for node in remove_list:
			node.parentNode.removeChild(node)
			if unlink:
				node.unlink()


	def __update(self):
		try:
			self._doc = xml.dom.minidom.parse(join(dirname(__file__),("dates_id"+str(adesklets.get_id())+".xml")))
		except IOError:
			self._doc =  xml.dom.minidom.Document()
			self._doc.appendChild(self._doc.createElement("datenotes"))
			temp = open(join(dirname(__file__),("dates_id"+str(adesklets.get_id())+".xml")),"w")
			temp.write(self._doc.toxml())
			temp.close()
		self._root = self._doc.getElementsByTagName("datenotes")[0]
		self.remove_whitespace_nodes(self._doc)

	def __save(self):
		self.remove_whitespace_nodes(self._doc)
		temp = open(join(dirname(__file__),("dates_id"+str(adesklets.get_id())+".xml")), "w")
		temp.write(self._doc.toxml())
		temp.close()
		self._doc.unlink()
		self.__update()

	def __getYearElementByYear(self,year):
		year_list = self._doc.getElementsByTagName("year")
		for element in year_list:
			if int(element.attributes['id'].value) == int(year):
				return element
		return -1

	def __getMonthElementByMonthAndYear(self, month, year):
		root = self.__getYearElementByYear(year)
		if root==-1:
			return -1
		month_list = root.getElementsByTagName("month")
		for element in month_list:
			if element.attributes['id'].value == month:
				return element
		return root

	def addEntry(self, day, month, year, time, text):
		entry = self._doc.createElement("entry")
		entry.setAttribute("day",str(day))
		entry.setAttribute("time",str(time))
		entry.appendChild(self._doc.createTextNode(str(text)))
		
		parent = self.__getMonthElementByMonthAndYear(month, year)
		node=None
		
		if parent == -1:
			parent = self._doc.createElement("year")
			parent.setAttribute("id", str(year))
			self._root.appendChild(parent)

		if parent.tagName=="year":
			temp = self._doc.createElement("month")
			temp.setAttribute("id", month)
			parent.appendChild(temp)
			node=temp
		
		if node==None:
			node=parent

		changed=False

		if node.hasChildNodes():
			for child in node.childNodes:
				if child.nodeType == xml.dom.Node.ELEMENT_NODE:
					if child.tagName == "entry":
						if int(child.attributes['day'].value) == int(day) and int(child.attributes['time'].value) == int(time):
							child.childNodes[0] = self._doc.createTextNode(text)
							changed=True

		if changed==False:
			node.appendChild(entry)

		self.__save()

	def removeEntry(self, day, month, year, time):
		node = self.__getMonthElementByMonthAndYear(month, year)
		if node != -1:
			if node.hasChildNodes():
				for child in node.childNodes:
					if child.nodeType == xml.dom.Node.ELEMENT_NODE:
						if child.tagName == "entry":
							if int(child.attributes['day'].value) == int(day) and int(child.attributes['time'].value) == int(time):
								child.parentNode.removeChild(child)
								child.unlink()

		self.__save()

	def getEntries(self, day, month, year):

		entry_list = []

		node = self.__getMonthElementByMonthAndYear(month, year)
		if node != -1:
			if node.hasChildNodes():
				for child in node.childNodes:
					if child.nodeType == xml.dom.Node.ELEMENT_NODE:
						if child.tagName == "entry":
							if int(child.attributes['day'].value) == int(day):
								entry_list.append(child)

		return_dict = {}

		for entry in entry_list:
			return_dict[entry.attributes['time'].value] = entry.childNodes[0].data

		return return_dict
								

#-----------------------------------------------------------------------------

class Events(adesklets.Events_handler):
	"""
	The usual Events handling class
	"""

	def __init__(self, basedir):
		if len(basedir)==0:
			self.basedir='.'
		else:
			self.basedir=basedir
		adesklets.Events_handler.__init__(self)

	def __del__(self):
		adesklets.Events_handler.__del__(self)

	def ready(self):
		# Do initialisation stuff here
		# Get the config file
		self.config=Config(adesklets.get_id(),
						   join(self.basedir,'config.txt'))

		# Send the config data to the Calendar class
		self.calendar_desklet = CalendarDesklet(self.config)
		self.calendar_desklet()

		# Start up datesnotes class
		self.datenotes = DateNotes()

		# Set up initial date values
		self.day, self.month, self.year = 0,0,0

	def alarm(self):
		"""
		Refresh the display as needed
		"""
		self.block()
		self.calendar_desklet.update()
		self.calendar_desklet.display()
		if have_tkinter:
			now = datetime.date.today()
			year = now.year
			month = calendar.month(now.year,now.month).strip().split()[0].strip()
			day = now.day
			note_dict = self.datenotes.getEntries(day, month, year)
			# Eventually will check if the entries time has passed when settable times are written
			# Remember, the time is the key
			for key in note_dict.keys():
				entrybox = EntryBox(str(day)+" "+month+" "+str(year),note_dict[key])
				entry = entrybox()
		self.unblock()
		return max(self.config['delay'],60)	

	def menu_fire(self, delayed, menu_id, item):
		if item=='Configure':
			editor=getenv('EDITOR')
			if editor:
				self._execute('xterm -e %s ' % editor +
							  join(self.basedir,'config.txt'))
		if have_tkinter:
			if item=='Add_DateNote':
				if self.day != 0:
					self.block()
					entrybox = EntryBox(self.day+" "+self.month+" "+self.year,"Enter note here")
					entry = entrybox()
					if entry != "":
						# Use time edit box value later
						self.datenotes.addEntry(self.day,self.month,self.year,10,entry)
					self.unblock()
			if item=='Remove_DateNotes':
				if self.day != 0:
					self.block()
					# Replace this later with a new Tcl/Tk dialogue that lists the available
					# entries to delete.
					self.datenotes.removeEntry(self.day,self.month,self.year,10)
					self.unblock()
			if item=='Edit_DateNote':
				if self.day != 0:
					self.block()
					note_dict = self.datenotes.getEntries(self.day, self.month, self.year)
					# This is an ugly hack way of doing things put here as a place holder, do something
					# similar to the planned removal dialogue, but list ones available for editing
					for key in note_dict.keys():
						entrybox = EntryBox(self.day+" "+self.month+" "+self.year,note_dict[key])
						entry = entrybox()
						if entry != "":
							# Use time edit box value later
							self.datenotes.addEntry(self.day,self.month,self.year,10,entry)
					self.unblock()
		if item=='Prev_Month':
			self.calendar_desklet.set_month_offset(1,'-')
		if item=='Next_Month':
			self.calendar_desklet.set_month_offset(1,'+')
		if item=='Prev_Year':
			self.calendar_desklet.set_year_offset(1,'-')
		if item=='Next_Year':
			self.calendar_desklet.set_year_offset(1,'+')


	def motion_notify(self, delayed, x, y):
		coords = self.calendar_desklet.get_date_from_coords(x,y)
		if coords != -1:
			self.day, self.month, self.year = coords
		else:
			self.day = 0

	def _execute(self,command):
		spawnlp(P_NOWAIT, command.split()[0], *command.split())

#------------------------------------------------------------------------------
# Start running
Events(dirname(__file__)).pause()


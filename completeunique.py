#!/usr/bin/python

"""
	completeunique -- list verses with unique first words
	Copyright (C) 2011 Jeff Sharkey, http://jsharkey.org
	
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.
	
	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.
	
	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import simplejson, re, itertools

from reportlab.lib import units, pagesizes, colors, styles
from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, Frame
from reportlab.platypus import BaseDocTemplate, PageTemplate, NextPageTemplate, PageBreak

INPUTFILE = "bodytext.json"
BOOK, CHAPTER, SECTION, VERSE, TEXT = ("BOOK", "CHAPTER", "SECTION", "VERSE", "TEXT")

WORD_CLASS = u"[\w'\u2019-]"
re_first_word = re.compile(r'(%s+)\b' % WORD_CLASS)


# load all chapter events
events = []
with open(INPUTFILE, 'r') as input:
	for line in input.readlines():
		events.extend(simplejson.loads(line))



# a grouping of verses
class Group:
	def __init__(self, name):
		self.name = name
		self.first_words = {}

	# report seeing a firstword and verse in this group
	def report_word(self, first_word, verse):
		if first_word not in self.first_words:
			self.first_words[first_word] = []
		self.first_words[first_word].append(verse)

	# strip our entire list of firstwords down to only unique ones
	def make_unique(self):
		unique = {}
		for key, value in self.first_words.iteritems():
			if len(value) == 1:
				unique[key] = value
		self.first_words = unique

	# return a sorted list for later printing
	def printable(self):
		keys = self.first_words.keys()
		keys.sort()
		output = [ self.first_words[key][0] for key in keys ]
		output = [ (ref, verse[:20]) for ref, verse in output ] 
		return output



books = []
chapters = []
sections = []

events = [(e['event'],e['data']) for e in events]
for event, data in events:
	if event == BOOK:
		book_group = Group(data)
		books.append(book_group)
	elif event == CHAPTER:
		chapter = data
		chapter_group = Group(chapter)
		chapters.append(chapter_group)
	elif event == SECTION:
		section_group = Group(data)
		sections.append(section_group)
	elif event == VERSE:
		ref = "%s:%s" % (chapter, data)
	elif event == TEXT:
		first_word = re_first_word.search(data)
		if first_word is not None:
			first_word = first_word.group(1).upper()
			book_group.report_word(first_word, (ref, data))
			chapter_group.report_word(first_word, (ref, data))
			section_group.report_word(first_word, (ref, data))


for group in books: group.make_unique()
for group in chapters: group.make_unique()
for group in sections: group.make_unique()


# do actual printing
margin = 0.5*units.inch
page_width = pagesizes.letter[0]-(margin*2)
col_width = (page_width/2)-margin

def make_table(printable):
	style = TableStyle()
	style.add('VALIGN', (0,0), (-1,-1), 'TOP')
	style.add('GRID', (0,0), (-1,-1), 1, colors.black)
	table = Table(printable, [col_width*0.4,col_width*0.6])
	table.setStyle(style)
	return table

def make_title(document, title):
	style = styles.getSampleStyleSheet()["Normal"]
	document.append(Spacer(0, margin/3))
	document.append(Paragraph('<b>%s</b>' % (title), style))
	document.append(Spacer(0, margin/3))


document = []

def dumpset(title, set):
	make_title(document, title)
	for item in set:
		if item is None: continue
		make_title(document, '<i>%s</i>' % (item.name))
		document.append(make_table(item.printable()))

dumpset("Unique across a book", books)
document.append(PageBreak())
dumpset("Unique across a chapter", chapters)
document.append(PageBreak())
dumpset("Unique across a section", sections)


# build pdf output
doc = BaseDocTemplate("out_completeunique.pdf", pagesize=pagesizes.letter, topMargin=margin,
	leftMargin=margin, bottomMargin=margin, rightMargin=margin)

# make default two-column output
frame1 = Frame(doc.leftMargin, doc.bottomMargin, col_width, doc.height, id='col1')
frame2 = Frame(doc.leftMargin+col_width+margin, doc.bottomMargin, col_width, doc.height, id='col2')
doc.addPageTemplates([PageTemplate(id='twocolumn',frames=[frame1,frame2])])

doc.build(document)


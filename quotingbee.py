#!/usr/bin/python

"""
	quotingbee -- generate random quoting bee
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

import simplejson, re, random

from reportlab.lib import units, pagesizes, colors, styles
from reportlab.platypus import Table, TableStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph

TITLE = "Set 1"

# number of verses to select for set
SET_SIZE = 100
# minimum word count in each verse
MIN_WORDS = 25
# maximum word count in each verse
MAX_WORDS = 40
# minimum distance between two consecutive verses
MIN_DISTANCE = 100


INPUTFILE = "bodytext.json"
CHAPTER, SECTION, VERSE, TEXT = ("CHAPTER", "SECTION", "VERSE", "TEXT")

# load all chapter events
events = []
with open(INPUTFILE, 'r') as input:
	for line in input.readlines():
		events.extend(simplejson.loads(line))

WORD_CLASS = u"[\w'\u2019-]"
re_word = re.compile(r'\b%s+\b' % WORD_CLASS)

# pick out verses within size limits
verses = []
verse_num = 0
chapter = None; verse = None
for event in events:
	if event['event'] == CHAPTER:
		chapter = event['data']
	elif event['event'] == VERSE:
		verse = event['data']
		verse_num += 1
	elif event['event'] == TEXT and chapter is not None and verse is not None:
		ref = "%s:%s" % (chapter, verse)
		text = event['data']
		wordcount = len(re_word.findall(text))
		if MIN_WORDS < wordcount and wordcount < MAX_WORDS:
			verses.append((verse_num, ref, text))


print "only", len(verses), "of", verse_num, "verses met length constraints"


# make random selection of verses
selected = []
last_num = -MIN_DISTANCE
while len(selected) < SET_SIZE:
	test = random.choice(verses)
	test_num = test[0]
	
	# avoid if not enough distance
	if abs(last_num - test_num) < MIN_DISTANCE:
		continue
	
	verses.remove(test)
	selected.append(test)
	last_num = test_num


# do actual printing
margin = 0.5*units.inch
width = pagesizes.letter[0]-(margin*2)

text_style = styles.getSampleStyleSheet()["Normal"]
text_style.leading *= 1.3

def verse_to_table(verse):
	global text_style
	num, ref, text = verse
	return (ref, Paragraph(text, text_style))

def header(canvas, doc):
	global margin
	canvas.saveState()
	canvas.setFont('Helvetica-Bold',11)
	canvas.drawString(margin, pagesizes.letter[1] - margin*1.2, "%s: verses %d-%d words long, at least %d verses apart" % (TITLE, MIN_WORDS, MAX_WORDS, MIN_DISTANCE))
	canvas.drawString(margin, margin, "Page %d" % (doc.page))
	canvas.restoreState()

# convert verses into pdf paragraphs
selected = map(verse_to_table, selected)

# build pdf table
style = TableStyle()
style.add('VALIGN', (0,0), (-1,-1), 'TOP')
style.add('GRID', (0,0), (-1,-1), 1, colors.black)
table = Table(selected, [width*0.2,width*0.8])
table.setStyle(style)

# build pdf output
doc = SimpleDocTemplate("out_quotingbee.pdf", pagesize=pagesizes.letter, topMargin=margin*1.5,
        leftMargin=margin, bottomMargin=margin*1.5, rightMargin=margin)
doc.build([table], onFirstPage=header, onLaterPages=header)


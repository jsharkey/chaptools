#!/usr/bin/python

"""
	oflist -- generate "of something" lists
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

import simplejson, re

from reportlab.lib import units, pagesizes, colors, styles
from reportlab.platypus import Table, TableStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph

INPUTFILE = "bodytext.json"
CHAPTER, SECTION, VERSE, TEXT = ("CHAPTER", "SECTION", "VERSE", "TEXT")

WORD_CLASS = u"[\w'\u2019-]"
re_of_block = re.compile(r"\b(%s+)\s+of\s+(%s+)\b" % (WORD_CLASS, WORD_CLASS), re.IGNORECASE)

# load all chapter events
events = []
with open(INPUTFILE, 'r') as input:
	for line in input.readlines():
		events.extend(simplejson.loads(line))


# collect all verses
verses = []
chapter = None; verse = None
for event in events:
	if event['event'] == CHAPTER:
		chapter = event['data']
	elif event['event'] == VERSE:
		verse = event['data']
	elif event['event'] == TEXT and chapter is not None and verse is not None:
		ref = "%s:%s" % (chapter, verse)
		verses.append((ref, event['data']))


def find_matches(key):
	matches = []
	for ref, verse in verses:
		for match in re_of_block.finditer(verse):
			matches.append((match, ref, verse))
	
	matches.sort(key=key)
	return matches



of_something = find_matches(lambda match: match[0].group(1).lower())
something_of = find_matches(lambda match: match[0].group(2).lower())


def match_to_table(match, splitBefore):
	match, ref, verse = match
	if splitBefore:
		before = verse[:match.end(1)]
		after = verse[match.end(1):]
	else:
		before = verse[:match.start(2)]
		after = verse[match.start(2):]
	
	before = before.strip()[-40:]
	after = after.strip()[:40]
	return (ref, before, after)

def match_to_table_before(match):
	return match_to_table(match, True)

def match_to_table_after(match):
	return match_to_table(match, False)



# do actual printing
margin = 0.5*units.inch
width = pagesizes.letter[0]-(margin*2)

# convert matches into pdf paragraphs
style = styles.getSampleStyleSheet()["Normal"]
of_something = map(match_to_table_after, of_something)
something_of = map(match_to_table_before, something_of)

# build pdf table
def buildTable(data):
        style = TableStyle()
        style.add('VALIGN', (0,0), (-1,-1), 'TOP')
        style.add('GRID', (0,0), (-1,-1), 1, colors.black)
        style.add('ALIGN', (1,0), (1,-1), 'RIGHT')
        table = Table(data, [width*0.2,width*0.4,width*0.4])
        table.setStyle(style)
        return table

# build pdf output
doc = SimpleDocTemplate("out_of_something.pdf", pagesize=pagesizes.letter, topMargin=margin,
        leftMargin=margin, bottomMargin=margin, rightMargin=margin)
doc.build([buildTable(of_something)])

doc = SimpleDocTemplate("out_something_of.pdf", pagesize=pagesizes.letter, topMargin=margin,
        leftMargin=margin, bottomMargin=margin, rightMargin=margin)
doc.build([buildTable(something_of)])


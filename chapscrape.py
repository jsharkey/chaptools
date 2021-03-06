#!/usr/bin/python

"""
	chapscrape -- script to scrape chapters for analysis
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

import urllib, urllib2, simplejson, sys, re
import BeautifulSoup as bs


BOOKS = [
	#"John": range(1, 22)
	("Hebrews", range(1, 14)),
	("1 Peter", range(1, 6)),
	("2 Peter", range(1, 4))
]

OUTPUTFILE = "bodytext.json"

BOOK, CHAPTER, SECTION, VERSE, TEXT = ("BOOK", "CHAPTER", "SECTION", "VERSE", "TEXT")

re_ignore = re.compile(r'The earliest manuscripts and many other ancient witnesses')
re_replace = re.compile(r'\[\[\[/woj\]\]\]')

def build_event(event, data):
	return {'event':event,'data':data}

def skip_subtree(tag):
	while not tag.nextSibling:
		tag = tag.parent
	return tag.nextSibling

output = open(OUTPUTFILE, 'w')

for book, chapters in BOOKS:
	simplejson.dump([build_event(BOOK, book)], output)
	output.write('\n')
	for chapter in chapters:
		print "scraping", book, chapter,
		sys.stdout.flush()
		
		url = "http://www.biblegateway.com/passage/?search=%s+%d&version=NIV&interface=print" % (urllib.quote_plus(book), chapter)
		soup = bs.BeautifulSoup(urllib2.urlopen(url), convertEntities=bs.BeautifulSoup.ALL_ENTITIES)
		
		start = soup.first('div', attrs={'class':'result-text-style-normal text-html '})
		end = soup.first('div', attrs={'class':'footnotes'})
		
		events = []
		activeText = None
		
		tag = start
		while tag != end and tag is not None:
			if isinstance(tag, bs.NavigableString):
				if re_ignore.search(tag.string) is None:
					string = re_replace.sub('', tag.string)
					if activeText is None:
						activeText = build_event(TEXT, "")
						events.append(activeText)
					activeText['data'] += string
			
			if isinstance(tag, bs.Tag):
				attrs = dict(tag.attrs)
				if tag.name == 'div' and 'heading' in attrs['class']:
					tag = skip_subtree(tag)
					activeText = None
					continue
				elif tag.name == 'span' and 'chapternum' in attrs['class']:
					events.append(build_event(CHAPTER, tag.text))
					events.append(build_event(VERSE, "1"))
					tag = skip_subtree(tag)
					activeText = None
					continue
				elif tag.name == 'h3':
					events.append(build_event(SECTION, tag.text))
					tag = skip_subtree(tag)
					activeText = None
					continue
				elif tag.name == 'sup' and 'versenum' in attrs['class']:
					events.append(build_event(VERSE, tag.text))
					tag = skip_subtree(tag)
					activeText = None
					continue
				elif tag.name == 'sup' and 'footnote' in attrs['class']:
					tag = skip_subtree(tag)
					continue
				elif tag.name == 'sup' and 'crossreference' in attrs['class']:
					tag = skip_subtree(tag)
					if isinstance(tag, bs.NavigableString):
						tag.string = tag.string.lstrip()
					continue
				else:
					pass
			
			tag = tag.next
		
		versecount = len([event for event in events if event['event'] is VERSE])
		print "and found", versecount, "verses"
		simplejson.dump(events, output) # indent=4
		output.write('\n')

output.close()

print "done, scraped chapters written to", OUTPUTFILE


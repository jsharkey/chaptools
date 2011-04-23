#!/usr/bin/python

"""
	uniquelist -- find unique words
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

INPUTFILE = "chapscrape.json"
CHAPTER, SECTION, VERSE, TEXT = ("CHAPTER", "SECTION", "VERSE", "TEXT")

input = open(INPUTFILE, 'r')

re_compound = re.compile(u"['\u2019]", re.UNICODE)
#re_boundary = re.compile(r'[^\w\s]')
re_word = re.compile(r'\b([\w-]+)\b')

words = {}

for events in input.readlines():
	events = simplejson.loads(events)
	for event in events:
		if event['event'] == TEXT:
			body = event['data'].upper()
			body = re_compound.sub('', body)
			#body = re_boundary.sub(' ', body)
			for word in re_word.findall(body):
				if word not in words:
					words[word] = 0
				words[word] += 1

def dump_words(words):
	words.sort()
	print '\n'.join(words)


once = [word for word, count in words.iteritems() if count == 1]
twice = [word for word, count in words.iteritems() if count == 2]
thrice = [word for word, count in words.iteritems() if count == 3]

#dump_words(once)

print "words mentioned once", len(once)
print "words mentioned twice", len(twice)
print "words mentioned thrice", len(thrice)

input.close()



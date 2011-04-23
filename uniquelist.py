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

# when true, count duplicate words inside single verse as unique
ALLOW_DUPE_INSIDE_VERSE = False

INPUTFILE = "bodytext.json"
CHAPTER, SECTION, VERSE, TEXT = ("CHAPTER", "SECTION", "VERSE", "TEXT")

re_compound = re.compile(u"['\u2019]", re.UNICODE)
re_word = re.compile(r'\b([\w-]+)\b')

class WordCount:
	def __init__(self):
		self.words = {}
	
	def discover(self, word, count=1):
		if word not in self.words:
			self.words[word] = 0
		self.words[word] += count
	
	def combine(self, another):
		for word, count in another.words.iteritems():
			if ALLOW_DUPE_INSIDE_VERSE:
				self.discover(word)
			else:
				self.discover(word, count)

# load all chapter events
events = []
with open(INPUTFILE, 'r') as input:
	for line in input.readlines():
		events.extend(simplejson.loads(line))


words = WordCount()
verse_words = WordCount()

for event in events:
	if event['event'] == VERSE:
		words.combine(verse_words)
		verse_words = WordCount()
	elif event['event'] == TEXT:
		body = event['data'].upper()
		body = re_compound.sub('', body)
		for word in re_word.findall(body):
			verse_words.discover(word)

# and combine last verse
words.combine(verse_words)


def dump_words(words):
	words.sort()
	print '\n'.join(words)


once = [word for word, count in words.words.iteritems() if count == 1]
twice = [word for word, count in words.words.iteritems() if count == 2]
thrice = [word for word, count in words.words.iteritems() if count == 3]

#dump_words(once)

print "words mentioned once", len(once)
print "words mentioned twice", len(twice)
print "words mentioned thrice", len(thrice)



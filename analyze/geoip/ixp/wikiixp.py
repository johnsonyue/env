import urllib
import os
import signal
import HTMLParser
import sys

class WikiRefParser(HTMLParser.HTMLParser):

#Parser for Wiki IXP list.
class WikiIXPParser(HTMLParser.HTMLParser):
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.lines=[]
		self.line=[]
		self.td_cnt=0
		self.is_body=False
		self.is_td=False
		self.is_link=False
		self.is_sup=False
		self.td=""
	
	def handle_starttag(self, tag, attrs):
		if (not self.is_body and tag == "tbody"):
			self.is_body = True
		
		if (self.is_body and tag == "td"):
			self.is_td = True
			self.td_cnt += 1
		
		if (self.is_body and self.td_cnt == 3 and tag == "a"):
			self.is_link = True
		if (self.is_body and tag == "sup"):
			self.is_sup = True
		
	def handle_endtag(self, tag):
		if (self.is_body and tag == "tr"):
			if (len(self.line) == 1):
				return
			region=self.line[0]
			country_city=self.line[1]
			name=self.line[2]
			if (len(self.line) == 4):
				ixf_region=self.line[3] #ixf stands for Internet Exchange Federation (IX-F)
			else:
				ixf_region=""
			self.lines.append("%s|%s|%s|%s" % (region, country_city, name, ixf_region))
			self.line=[]
			self.td_cnt=0
			
		if (self.is_td and tag == "td"):
			self.is_td = False
			self.line.append(self.td)
			self.td=""
		
		if (self.is_link and tag == "a"):
			self.is_link = False
		if (self.is_sup and tag == "sup"):
			self.is_sup = False
		
	def handle_data(self, data):
		if (self.is_td):
			self.td+=data
		if (self.is_link and not self.is_sup):
			self.td+="["+data+"]"

def parse_ref():
	parser = WikiRefParser()
	parser.feed(open("wiki-ref.html",'rb').read())

def parse_ixp():
	parser = WikiIXPParser()
	parser.feed(open("list-of-ixp.html",'rb').read())
	for l in parser.lines:
		print l

def main(argv):
	parse_ixp()

if __name__ == "__main__":
	main(sys.argv)

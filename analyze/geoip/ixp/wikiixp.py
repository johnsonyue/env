import urllib
import os
import signal
import HTMLParser
import sys
import re

class WikiRefParser(HTMLParser.HTMLParser):
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.cites={}
		self.cite_cnt=0
		self.span_cnt=0
		self.link=""
		self.line=""
		self.is_li=False
		self.is_ref=False
		self.is_cite=False
		self.is_link=False

	def handle_starttag(self, tag, attrs):
		if (tag == "li"):
			self.is_li = True
			self.cite_cnt += 1
		if (self.is_li and tag == "cite"):
			self.is_cite = True
		if (self.is_li and tag == "span"):
			for k,v in attrs:
				if k == "class" and v == "reference-text":
					self.is_ref = True
					break
		if (self.is_ref and tag == "span"):
			self.span_cnt += 1
		
		if (self.is_cite and tag == "a"):
			self.is_link = True
			self.link = ""
			for k,v in attrs:
				if k == "href":
					self.link = v
		
	def handle_endtag(self, tag):
		if (self.is_li and tag == "li"):
			self.is_li = False
			self.cites[self.cite_cnt] = self.line
			self.line = ""
		
		if (self.is_cite and tag == "cite"):
			self.is_cite = False
			self.link = ""
		if (self.is_ref and tag == "span"):
			self.span_cnt -= 1
			if self.span_cnt == 0:
				self.is_ref = False
				self.link = ""
		
		if (self.is_link and tag == "a"):
			self.is_link = False
	def handle_data(self, data):
		if ((self.is_cite or self.is_ref) and self.is_link):
			self.line += "["+data+"]"+" <"+self.link+">"
		elif (self.is_cite or self.is_ref):
			self.line += data

#Parser for Wiki IXP list.
class WikiIXPParser(HTMLParser.HTMLParser):
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.lines=[]
		self.line=[]
		self.root="https://en.wikipedia.org"
		self.link=""
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
			self.link = ""
			for k,v in attrs:
				if k == "href":
					self.link = v
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
			self.td+="["+data+"]"+" <"+self.root+self.link+">"

def parse_ref():
	parser = WikiRefParser()
	parser.feed(open("wiki-ref.html",'rb').read())
	return parser.cites

def parse_ixp(cites):
	parser = WikiIXPParser()
	parser.feed(open("list-of-ixp.html",'rb').read())
	for l in parser.lines:
		fields=l.split('|')
		name=fields[2]
		t=re.findall("\[\d+\]",name)
		if len(t) != 0:
			index = int(t[0].replace('[','').replace(']',''))
			fields[2] = name.replace(t[0], cites[index])
		line=""
		for f in fields:
			line+=f+"|"
		print line.strip("|")

def main(argv):
	cites=parse_ref()
	parse_ixp(cites)

if __name__ == "__main__":
	main(sys.argv)

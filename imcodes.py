#!/usr/bin/python
"""Module docstring.

This serves as a long usage message.
"""

import markdown
import yaml
import re
import sys
import getopt
import os
import shutil
import fnmatch
from jinja2 import Environment, PackageLoader, evalcontextfilter
from zipfile import ZipFile

def zip_dir(zipname, dir_to_zip):
	dir_to_zip_len = len(dir_to_zip.rstrip(os.sep)) + 1
	with ZipFile(zipname, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
		for dirname, subdirs, files in os.walk(dir_to_zip):
			for filename in files:
				path = os.path.join(dirname, filename)
				entry = path[dir_to_zip_len:]
				zf.write(path, entry)

def copytree(src, dst, ignore=None):
	for item in os.listdir(src):
		s = os.path.join(src, item)
		d = os.path.join(dst, item)
		if os.path.isdir(s):
			shutil.copytree(s, d, ignore)
		else:
			shutil.copy2(s, d)

class TimelineParser:
	RE = re.compile('@(\d\d):(\d\d):\n(.*?)(?:\n\n|\s*$)', re.S)	
	def __init__(self, isCode):
		self.code = isCode;
	def parse(self, content):
		blocks = RE.findall(content)
		keyframes = [];
		for block in blocks:
			timeInSeconds = int(block[0]) * 60 + int(block[1])
			content = block[2]
			if self.code:
				keyframes.append([timeInSeconds, content])
			else:
				html = markdown.markdown(content)
				keyframes.append([timeInSeconds, html])
		return keyframes

class Layout:
	def __init__(self, env, yamlBlock, basePath, template):
		self.env = env
		self.info = {}
		self.basePath = basePath
		for prop in ['Title', 'CodeContents', 'Timeline', 'TextContents', 'Video']:
			try:
				self.info[prop] = yamlBlock[prop]
			except:
				self.info[prop] = ''
		self.template = env.get_template(template)		
	def generate(self):
		return self.template.render(
			title=self.info["Title"])
	def getTimeline(self, isCode):
		try:
			f = open(self.basePath + '/' + self.info["Timeline"], 'r')
			keyframes = TimelineParser(isCode).parse(f.read())
			f.close()
			return keyframes
		except:
			return []	
	def getMarkdown(self):
		try:
			f = open(self.basePath + '/' + self.info["TextContents"], 'r')
			contents = markdown.markdown(f.read())
			f.close()
			return contents
		except:
			return ''	
	def getCode(self):
		try:
			return self.info["CodeContents"]
		except:
			return ''

class VideoAndCodeLayout(Layout):
	def __init__(self, yamlBlock, basePath, env):
		Layout.__init__(self, env, yamlBlock, basePath, 'VideoAndCode.html')	
	def generate(self):
		return self.template.render(
			keyframes=self.getTimeline(True), 
			code=self.getCode(),
			video=self.videoUrl, 
			title=self.title)
	
class VideoLayout(Layout):
	def __init__(self, yamlBlock, basePath, env): 
		Layout.__init__(self, env, yamlBlock, basePath, 'Video.html')	
	def generate(self):
		return self.template.render(
			video=self.info['Video'],
			title=self.info['Title'])
	
class TextLayout(Layout):
	def __init__(self, yamlBlock, basePath, env):
		Layout.__init__(self, env, yamlBlock, basePath, 'Text.html')	
	def generate(self):
		return self.template.render(
			contents=self.getMarkdown(),
			title=self.info['Title'])
	
class CodeLayout(Layout):
	def __init__(self, yamlBlock, basePath, env): 
		Layout.__init__(self, env, yamlBlock, basePath, 'Code.html')	
	def generate(self):
		return self.template.render(
			code=self.getCode(), 
			title=self.info['Title'])
	
class VideoAndTextLayout(Layout):
	def __init__(self, yamlBlock, basePath, env): 
		Layout.__init__(self, env, yamlBlock, basePath, 'VideoAndText.html')	
	def generate(self):	
		return self.template.render(
			contents=self.getMarkdown(), 
			keyframes=self.getTimeline(False),
			video=self.info['Video'],
			title=self.info['Title'])
	
class TextAndCodeLayout(Layout):
	def __init__(self, yamlBlock, basePath, env): 
		Layout.__init__(self, env, yamlBlock, basePath, 'TextAndCode.html')	
	def generate(self):
		return self.template.render(
			code=self.getCode(), 
			contents=self.getMarkdown(),
			title=self.info['Title'])

def renderStep(s, env, index, basePath, outDir):	
	layout = TextLayout(s, basePath, env)
	layoutType = 'TextLayout'
	try:
		layoutType = s['Layout'];
	except:
		pass
	stepHTML = "<!DOCTYPE html><html></html>"
	if layoutType == 'Text':		
		pass
	elif layoutType == 'Video':
		layout = VideoLayout(s, basePath, env)	
	elif layoutType == 'Code':
		layout = CodeLayout(s, basePath, env)		
	elif layoutType == 'VideoAndText':
		layout = VideoAndTextLayout(s, basePath, env)
	elif layoutType == 'TextAndCode':
		layout = TextAndCodeLayout(s, basePath, env)
	elif layoutType == 'VideoAndCode':
		layout = VideoAndCodeLayout(s, basePath, env)
	f = open(outDir + '/step' + str(index) + '.html', 'w')
	f.write(layout.generate())
	f.close()
	
env = Environment(loader=PackageLoader('imcodes', 'templates'));
env.globals = {
	"SCRIPTS": 
		["http://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js",
		 "http://cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/codemirror.js",
		 "http://cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/mode/javascript/javascript.min.js",
		 "http://cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/mode/python/python.min.js",
	   "skulpt/skulpt.js",
		 "skulpt/skulpt-stdlib.js"],
	"STYLES":
		["http://yui.yahooapis.com/pure/0.5.0/pure-min.css",
		 "http://maxcdn.bootstrapcdn.com/font-awesome/4.2.0/css/font-awesome.min.css",
	   "http://cdnjs.cloudflare.com/ajax/libs/codemirror/4.6.0/codemirror.min.css".
		 "common.css"]
};

def generate(yamlFile, inDir, outDir):
	# Load the YAML info
	f = open(inDir + '/' + yamlFile, 'r')
	moduleYaml = yaml.load(f.read())
	f.close()	
	env.globals["numSteps"] = len(moduleYaml['Steps']);
	#WTF
	env.globals["range"] = range
 	# Render index.html
	index = Layout(env, moduleYaml, inDir, "index.html")
	f = open(outDir + '/index.html', 'w')
	f.write(index.generate())
	f.close()
	
	
	# Render each step
	for i,s in enumerate(moduleYaml['Steps']):
		renderStep(s, env, i, inDir, outDir)
  # Copy over anything that isn't yaml or markdown
	copytree(inDir, outDir, ignore=shutil.ignore_patterns('*.imcodes', '*.md', '*.markdown', '*.yaml'))

def findYaml(directory):
	for file in os.listdir(directory):
		if fnmatch.fnmatch(file, '*.imcodes'):
			return file
	return ''

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "ho:", ["help", "output"])
	except getopt.error, msg:
		print msg
		print "for help use -h / --help"
		sys.exit(2)
	# process options
	outFile = "module"
	inFile = ''
	for o, a in opts:
		if o in ("-h", "--help"):
			print __doc__
			sys.exit(0)
		if o in ("-o", "--output"):
			outFile = a
	# process arguments
	for arg in args:
		inFile = arg
	if inFile == '':
		print 'Must have an input file as zip'
		print "For help use -h/--help"
		sys.exit(0)	
	tmpIn = inFile + '.tmpdir'
	if not os.path.exists(tmpIn):
		os.makedirs(tmpIn)
	tmpOut = outFile + '.tmpdir'
	if not os.path.exists(tmpOut):
		os.makedirs(tmpOut)
	ZipFile(inFile, 'r').extractall(tmpIn)
	generate(findYaml(tmpIn), tmpIn, tmpOut)
	shutil.make_archive(outFile, 'zip', tmpOut)
	shutil.rmtree(tmpIn)
	shutil.rmtree(tmpOut)

if __name__ == "__main__":
    main()
	
	


	

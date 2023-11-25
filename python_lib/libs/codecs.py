# FILEPATH: /c:/Users/karan/aeap-speech-to-text/lib/codecs.js
# BEGIN: ed8c6549bwf9
import utils
class Codec:
	def __init__(self, name, sampleRate, attributes):
		self.name = name
		self.sampleRate = sampleRate
		self.attributes = attributes

supported = [
	Codec("ulaw", 8000, []),
	Codec("slin16", 16000, []),
	Codec("opus", 48000, []),
]

def equal(obj1, obj2):
	return obj1.name == obj2.name

def to_string(objs):
	if not isinstance(objs, list):
		objs = [objs]
	
	return ", ".join([o.name for o in objs])

class Codecs:
	def __init__(self, options):
		self.codecs = options.get("codecs", supported)
		self.selected = self.codecs[0]  # Default to first in list
	
	def first(self, codecs):
		try:
			res = utils.first(self.codecs, codecs, equal)
			
			if res:
				return res
		except Exception as e:
			pass
		
		raise Exception("Codec {} not supported".format(to_string(codecs)))

# END: ed8c6549bwf9
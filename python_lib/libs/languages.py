import utils

module.exports = {
	Languages,
}
# FILEPATH: /c:/Users/karan/aeap-speech-to-text/lib/languages.py
# BEGIN: ed8c6549bwf9


class Languages:
	supported = [
		"en-US",
	]

	def __init__(self, options):
		self.languages = options.get("languages", self.supported)
		self.languages = utils.intersect(self.supported, self.languages)
		self.selected = self.languages[0] if self.languages else None

	def first(self, languages):
		try:
			res = utils.first(self.languages, languages)
			if res:
				return res
		except Exception:
			pass

		raise Exception(f"Language {languages} not supported")

# END: ed8c6549bwf9

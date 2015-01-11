# coding: utf-8

import logging
import flask
import flask_config
import datetime
from flask import request, render_template

app = flask.Flask(__name__)
app.static_folder = "templates"
app.SEND_FILE_MAX_AGE_DEFAULT = 0


@app.route('/results', methods=['POST'])
def results():
	# set some defaults
	word_count = 0
	sentence_count = 0
	syllable_count = 0
	readling_level = 0
	pronoun_counter = {
						'singular_i':0,'singular_you':0,
						'plural_we':0,'plural_you':0,
						'singular_kk':0,'singular_kvk':0,'singular_hv':0,
						'plural_kk':0,'plural_kvk':0,'plural_hv':0
					}
	
	# get the blob of text
	if 'text' in request.form:
		text_is = request.form['text']
		
		# get the word count
		word_count = len(text_is.split(' '))
		for i in text_is.lower().split(' '):
			# naïve syllable counter counts every non-diplong vowel combination
			# This will fail with a few specific types of words
			# - Abbreviations: GSM, km (kilometer), t.d.
			# - Foreign Words: Tokyo
			
			word = i.replace(u'í','').replace(u'ý','').replace(u'á','').replace(u'é','').replace(u'ó','').replace(u'ö','').replace(u'ú','').replace(u'æ','')
			syllable_count += (len(i)-len(word))
			word = i.replace('au','').replace('ei','').replace('ey','')
			syllable_count += ((len(i)-len(word))/2)
			word_non_dipthongs = word.replace('a','').replace('u','').replace('e','').replace('i','')
			syllable_count += (len(word)-len(word_non_dipthongs))
			
			# Experimental:
			# This is not perfect, without a Part of Speach parser, there are a few collisions between regular words
			# The plural you also has collions in terms so they have been omitted.
			if i in [u'ég',u'mér',u'mig','mín']:
				pronoun_counter['singular_i'] += 1
			if i in [u'þú',u'þig',u'þér',u'þín']:
				pronoun_counter['singular_you'] += 1
			if i in [u'við','okkur','okkar']:
				pronoun_counter['plural_we'] += 1
			if i in [u'þið','ykkur','ykkar']:
				pronoun_counter['plural_you'] += 1
			if i in [u'hann','honum','hans']:
				pronoun_counter['singular_kk'] += 1
			if i in [u'hún','hana','henni','hennar']:
				pronoun_counter['singlar_kvk'] += 1
			if i in [u'það',u'því',u'þess']:
				pronoun_counter['singular_hv'] += 1
			if i in [u'þeir',u'þá']:
				pronoun_counter['plural_kk'] += 1
			if i in [u'þær']:
				pronoun_counter['plural_kvk'] += 1
			if i in [u'þau']:
				pronoun_counter['plural_hv'] += 1
		
		# Convert all punctuation to full-stop, split on full-stops
		sentences = text_is.replace('!','.').replace('?','.').split('.')
		for i in sentences:
			if len(i) > 0:
				sentence_count += 1
				
		
		readling_level = 206.835 - (1.015 * (float(word_count)/sentence_count)) - (84.6 * (float(syllable_count)/word_count))

	return render_template('results.html', word_count=word_count, sentence_count=sentence_count, syllable_count=syllable_count, readling_level=readling_level,pronoun_counter=pronoun_counter)

	
@app.route('/')
def home():
	# Displays the page to post an icelandic text blob
	return render_template('home.html')

if __name__ == '__main__':
	# Set up logging to stdout, which ends up in Heroku logs
	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(logging.WARNING)
	app.logger.addHandler(stream_handler)

	app.debug = True
	app.run(host='0.0.0.0', port=flask_config.port)

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
	
	# get the blob of text
	if 'text' in request.form:
		text_is = request.form['text']
		
		# get the word count
		word_count = len(text_is.split(' '))
		for i in text_is.lower().split(' '):
			# naïve syllable counter counts every non-diplong vowel combination
			word = i.replace(u'í','').replace(u'ý','').replace(u'á','').replace(u'é','').replace(u'ó','').replace(u'ö','').replace(u'ú','')
			syllable_count += (len(i)-len(word))
			word = i.replace('au','').replace('ei','').replace('ey','')
			syllable_count += ((len(i)-len(word))/2)
			word_non_dipthongs = word.replace('a','').replace('u','').replace('e','').replace('i','')
			syllable_count += (len(word)-len(word_non_dipthongs))
			
			
		
		# Convert all punctuation to full-stop, split on full-stops
		sentences = text_is.replace('!','.').replace('?','.').split('.')
		for i in sentences:
			if len(i) > 0:
				sentence_count += 1
				
		
		readling_level = 206.835 - (1.015 * (float(word_count)/sentence_count)) - (84.6 * (float(syllable_count)/word_count))

	return render_template('results.html', word_count=word_count, sentence_count=sentence_count, syllable_count=syllable_count, readling_level=readling_level)

	
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

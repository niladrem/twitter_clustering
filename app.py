from flask import Flask, config, render_template, request
import genieclust
import psycopg2
from psycopg2 import Error
import pandas as pd
import re
from flair.models import TextClassifier
from flair.data import Sentence
from segtok.segmenter import split_single
import numpy as np
import argparse
import psycopg2

from scripts import placeholderPlot, processing, clustering

app = Flask(__name__)

@app.route('/callback', methods=['POST', 'GET'])
def cb():
	data = request.args.get('data')



	data = np.array(data.split(';'))
	for i in range(len(data)):
		if data[i] == '':
			data[i] = 0


	weight_dict = {
			"follow": int(data[4]),
            "retweet": int(data[5]),
            "like": int(data[6]),
            "mention": int(data[7]),
            "quote": int(data[8]),
            "reply": int(data[9]),
            "friend": int(data[10])
			}
	us, rel = processing.getDBData() #przekazujemy data[0], todo
	user_map = processing.createUserMapping(us)
	X = processing.createX(rel, user_map, weight_dict)
	X_id = user_map.X_id
	gen = genieclust.Genie(int(data[1]), affinity="precomputed", gini_threshold=float(data[2]))
	labels = gen.fit_predict(X)

	if (data[3] == '0'):
		return placeholderPlot.heatmap(X, labels.tolist())
	else:
		return placeholderPlot.bubble(labels.tolist(), int(data[1]))
   
@app.route('/')
def index():
	return render_template('index.html',  graphJSON=placeholderPlot.empty_plot())

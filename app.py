from flask import Flask, config, render_template, request, send_file, redirect, url_for
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
from glob import glob
from io import BytesIO
from zipfile import ZipFile
import os
import sys
import json
from scripts import processing


app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/charts', methods=['POST', 'GET'])
def process_data():
	data = request.args.get('data')

	data = np.array(data.split(';'))
	if data[0] == '':
		data[0] = '*'

	weight_dict = {
			"follow": int(data[3]),
			"retweet": int(data[4]),
			"like": int(data[5]),
			"mention": int(data[6]),
			"quote": int(data[7]),
			"reply": int(data[8]),
			"friend": int(data[9])
			}

	us, rel = processing.getDBData(query=data[0])

	user_map = processing.createUserMapping(us)
	if data[10] == 'false':
		X = processing.createX(rel, user_map, weight_dict)
	else: X = processing.createX(rel, user_map, weight_dict, True)
	X_id = user_map.X_id
	gen = genieclust.Genie(int(data[1]), affinity="precomputed", gini_threshold=float(data[2]))
	labels = gen.fit_predict(X)

	# for bubblechart
	cluster_size=[0]*int(data[1])
	for i in range(len(labels)):
		cluster_size[labels[i]]+=1
	cluster_size = list(filter((1).__ne__, cluster_size))
	cluster_size2 = pd.DataFrame(cluster_size)
	cluster_size2.to_csv('data/temp/cluster_size.csv', header=False, index=False)

	# for heatmap
	Xi = pd.DataFrame(X)
	Xi['labels'] = labels
	Xi = Xi.set_index('labels')
	Xi.columns = labels
	Xi.sort_index(axis=0).sort_index(axis=1)
	Xser = []
	for i in range(len(Xi)):
		for j in range(len(Xi)):
			Xser.append([i, j, Xi.iat[i, j]])
	Xser = pd.DataFrame(Xser)
	Xser.to_csv('data/temp/Xser.csv', header=False, index=False)

	labels = pd.DataFrame(labels)
	us = pd.concat([us, labels], axis=1)
	us.rename(columns={0:'cluster'}, inplace=True)

	np.savetxt("data/X.csv", X, delimiter=",", newline="\n")
	user_map.to_csv("data/user_map.csv")
	us.to_csv("data/users.csv")
	rel.to_csv("data/relations.csv")

	return redirect(url_for('index'))


@app.route('/download')
def download_file():

	target = 'data'

	stream = BytesIO()
	with ZipFile(stream, 'w') as zf:
		for file in glob(os.path.join(target, '*.csv')):
			zf.write(file, os.path.basename(file))
	stream.seek(0)

	return send_file(stream, as_attachment=True, attachment_filename='twitter_data.zip')


@app.route('get_heat_data', methods=['POST'])
def get_heat_data():
	data = []
	try:
		data = pd.read_csv('data/temp/Xser.csv', header=None)
		data = data.values.tolist()
	except:
		print("heat data not found")

	return json.dumps(data)


@app.route('get_cluster_size', methods=['POST'])
def get_cluster_size():
	cluster_size = []
	try:
		cluster_size = pd.read_csv('data/temp/cluster_size.csv', header=None)
		cluster_size = cluster_size[0].values.tolist()
	except:
		print("cluster_size not found")

	return json.dumps(cluster_size)
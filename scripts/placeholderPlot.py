import pandas as pd
import json
import plotly
import plotly.express as px
import numpy as np

def heatmap(X, labels):
	X = pd.DataFrame(X)
	X['labels'] = labels
	X = X.set_indexes('labels')
	X.columns = labels
	X.sort_index(axis=0).sort_index(axis=1)

	fig = px.imshow(df)
	fig.update_yaxes(visible=False, showticklabels=False)
	fig.update_xaxes(visible=False, showticklabels=False)
	graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return graphJSON

def bubble(labels, n_cluster):
	lcount = []
	for i in range (n_cluster):
		lcount.append(labels.count(i))

	df = pd.DataFrame(np.random.rand(n_cluster, 2))
	df.columns = ['x', 'y']
	df['size'] = lcount
	fig = px.scatter(df, x = 'x', y = 'y', size = 'size', color = 'size', size_max = 50)
	fig.update_yaxes(visible=False, showticklabels=False)
	fig.update_xaxes(visible=False, showticklabels=False)
	graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return graphJSON

def empty_plot():
	fig = px.scatter(pd.DataFrame([[0, 0]]))
	fig.update_yaxes(visible=False, showticklabels=False)
	fig.update_xaxes(visible=False, showticklabels=False)
	graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return graphJSON
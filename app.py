from flask import Flask, config, render_template, request

from scripts import placeholderPlot

app = Flask(__name__)

@app.route('/callback', methods=['POST', 'GET'])
def cb():
    return placeholderPlot.gm(request.args.get('data'))
   
@app.route('/')
def index():
    return render_template('index.html',  graphJSON=placeholderPlot.gm())

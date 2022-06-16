from flask import Flask
from flask import request
from flask import jsonify
from flask import abort
import requests
import json
import os

app = Flask(__name__)

def response_filter(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  return response

@app.errorhandler(404)
def resource_not_found(e):
  return response_filter(jsonify(error=str(e))), 404

@app.errorhandler(503)
def resource_not_available(e):
  return response_filter(jsonify(error=str(e))), 503

@app.route('/', methods = ['GET'])
def queryEndpoint():
  query = request.args.get('q')
  if query is None or query == "":
    return abort(404)
  url = f"{os.environ['SPDY_BE']}?q={query}"
  try:
    return response_filter(jsonify(json.loads(requests.get(url).content)))
  except:
    return abort(503)

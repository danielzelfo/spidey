from flask import Flask
from flask import request
from flask import jsonify
from flask import abort
from Query import Query

app = Flask(__name__)
query = Query()

def response_filter(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  return response

@app.errorhandler(404)
def resource_not_found(e):
  return response_filter(jsonify(error=str(e))), 404

@app.route('/', methods = ['GET'])
def queryEndpoint():
    querystr = request.args.get('q')
    if querystr is None:
        abort(404)
    if querystr == "":
        return response_filter(jsonify([]))
    res, time = query.getQueryResults(querystr)
    res = query.getDocumentsInfo([r[0] for r in res])
    return response_filter(jsonify({
        "results": res,
        "time": time
    }))

if __name__ == "__main__":
    app.run(host='0.0.0.0')
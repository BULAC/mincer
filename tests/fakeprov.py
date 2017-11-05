#!/usr/bin/env python3

# Convenient constant for HTTP status codes
try:
    # Python 3.5+ only
    from HTTPStatus import OK, BAD_REQUEST
except Exception as e:
    from http.client import OK, BAD_REQUEST

# To create a web server c.f. http://flask.pocoo.org/
from flask import Flask

# The web application named after the main file itself
# TODO: use a factory instead
app = Flask(__name__)


# TODO: put this in the generic route /fake/<param>
@app.route("/canary")
# @app.route("/<string:param>")
def canary():
    return "Pew Pew", OK

# @app.route("/fake/<string:query>")
# def serve_any_query(query):
#     if query == 
#     return 

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5555)

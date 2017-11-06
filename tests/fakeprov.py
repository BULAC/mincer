#!/usr/bin/env python3
"""
Dummy server used to test Mincer on all usecase.
"""

# Convenient constant for HTTP status codes
try:
    # Python 3.5+ only
    from HTTPStatus import OK, BAD_REQUEST
except Exception as e:
    from http.client import OK, BAD_REQUEST

# To create a web server c.f. http://flask.pocoo.org/
from flask import Flask

# The web application named after the main file itself
app = Flask(__name__)


@app.route("/fake/<string:query>")
def serve_any_query(query):
    if query == "canary":
        return '<div class="result">Pew Pew</div>', OK

    return BAD_REQUEST


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5555)

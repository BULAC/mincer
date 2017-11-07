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

from urllib.parse import unquote_plus

# To create a web server c.f. http://flask.pocoo.org/
from flask import Flask

# The web application named after the main file itself
app = Flask(__name__)


@app.route("/fake/<string:query>")
def serve_any_query(query):
    clean_query = unquote_plus(query)

    if clean_query == "canary":
        return '<div class="result">Pew Pew</div>', OK
    elif clean_query == "search with multiple results":
        return '<div class="result">'\
            '<div>Result number 1</div>'\
            '<div>Result number 2</div>'\
            '<div>Result number 3</div>'\
            '</div>', OK
    elif clean_query == "search with links":
        return '<div class="result">'\
            '<div><a href="/some/doc.html">1st link</a></div>'\
            '<div><a href="/some/place">2nd link</a></div>'\
            '<div><a href="/some/dir/">3rd link</a></div>'\
            '<div><a href="some/direct/link">4th link</a></div>'\
            '</div>', OK

    return BAD_REQUEST


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5555)

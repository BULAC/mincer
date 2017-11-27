#!/usr/bin/env python3
"""
Mincer: stuff your websites with the best ingredients

Mincer is a web server used to extract results from one web service by parsing
its html result page.

Mincer is developed for the `BULAC
<http://www.bulac.fr/bulac-in-english/who-are-we/>`_ library in Paris.
"""

__author__ = "Pierre-Yves Martin <pym.aldebaran@gmail.com>"
__copyright__ = "Copyright (C) 2017 GIP BULAC"
__license__ = "GNU AGPL V3"

# This file is part of Mincer.
#
# Mincer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mincer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Mincer.  If not, see <http://www.gnu.org/licenses/>.

# To decode form-encoded values
from urllib.parse import unquote_plus

# To manipulate path
import os

# To create a web server c.f. http://flask.pocoo.org/
from flask import Flask

# To analyse recieved requests
from flask import request

# To display messages
from flask import flash

# To redirect to another page
from flask import redirect

# To retrieve the url corresponding to a specific route
from flask import url_for

# Flask application context all purpose variable
from flask import g

# For rendering Jinja2 HTML template as pages
from flask import render_template

# For easy redirecting to error page
from flask import abort

# For easy database ~ python binding c.f. http://www.sqlalchemy.org/
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy

# To manipulate HTML DOM using JQuery query syntax
from pyquery import PyQuery

# HTTP library for Python, safe for human consumption
# See http://docs.python-requests.org/en/master/
import requests

# A Python slugify application that handles unicode.
# See https://github.com/un33k/python-slugify
from slugify import slugify

# Convenient constant for HTTP status codes
try:
    # Python 3.5+ only
    from HTTPStatus import OK, NOT_FOUND, INTERNAL_SERVER_ERROR, BAD_REQUEST
except Exception as e:
    from http.client import OK, NOT_FOUND, INTERNAL_SERVER_ERROR, BAD_REQUEST

# Html extraction tools
from mincer import utils

# The web application named after the main file itself
app = Flask(__name__)

# Config of the application

# Secret key in order to use cookies
app.secret_key = "5609f915316fa83ec278e4136989c4"

# Default values
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{path}".format(
    path=os.path.join(app.instance_path, 'mincer.db'))

# If we want to overload the setting with a config file
app.config.from_envvar('MINCER_SETTINGS', silent=True)

# Add the database support to our application
db = SQLAlchemy(app)


class HtmlClasses(object):
    """HTML classes used when generating returned HTML contents."""

    """Class used to embed returned content when we have no results."""
    NO_RESULT = "no-result"

    """Class used to embed returned content when we have some results."""
    RESULT = "some-results"


# TODO: Add a selectors_to_remove list of selector that target nodes to remove


class Provider(db.Model):
    """A web data provider for Mincer.

    It can be a search provider or a book list provider."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    slug = db.Column(db.String, unique=True, nullable=False)
    remote_url = db.Column(db.String, unique=False, nullable=False)
    result_selector = db.Column(db.String, unique=False, nullable=False)
    no_result_selector = db.Column(db.String, unique=False, nullable=False, default="")
    no_result_content = db.Column(db.String, unique=False, nullable=False, default="")

    def __init__(self, **kwargs):
        assert "slug" not in kwargs, "slug is auto-computed and must not be provided"

        # Add the slug param since it is built from name
        kwargs["slug"] = slugify(kwargs["name"])

        super(Provider, self).__init__(**kwargs)


class Dependency(db.Model):
    """A javascript or CSS dependency of Mincer app.

    We put this information in the database in order to easily update it
    without altering the code.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    url = db.Column(db.String, unique=False, nullable=False)
    sha = db.Column(db.String, unique=False, nullable=False)


class DatabaseError(Exception):
    """Raised if an non repairable error occured while dealing with database."""
    pass


def init_db():
    """Remove everything from database and then nitialize it with the SQL schema.

    This function must be called at least once before using the database in any way.

    See `Flask-SQLAlchemy Tutorial - A Minimal Application
    <http://flask-sqlalchemy.pocoo.org/2.3/quickstart/#a-minimal-application>`_
    """
    if not os.path.exists(app.instance_path):
        raise DatabaseError(
            "Impossible to create or access database."
            "The instance path {path} used to store "
            "the database does not exist.".format(path=app.instance_path)
            )

    # TODO: create a backup of the database

    # First clean the meta data
    db.drop_all()
    db.create_all()

    # Then clean the data
    Provider.query.delete()
    Dependency.query.delete()
    db.session.commit()

    # Give valid defaults for dependencies
    jquery = Dependency(
        name="jquery-js",
        url="https://code.jquery.com/jquery-3.2.1.min.js",
        sha="sha384-PsH8R72JQ3SOdhVi3uxftmaW6Vc51MKb0q5P2rRUpPvrszuE4W1povHYgTpBfshb")
    popper = Dependency(
        name="popper-js",
        url="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.3/umd/popper.min.js",
        sha="sha384-vFJXuSJphROIrBnz7yo7oB41mKfc8JzQZiCq4NCceLEaO4IHwicKwpJf9c9IpFgh")
    bootstrapjs = Dependency(
        name="bootstrap-js",
        url="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/js/bootstrap.min.js",
        sha="sha384-alpBpkh1PFOepccYVYDB4do5UnbKysX5WZXm3XxPqe5iKTfUKjNkCk9SaVuEZflJ")
    bootstrapcss = Dependency(
        name="bootstrap-css",
        url="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css",
        sha="sha384-PsH8R72JQ3SOdhVi3uxftmaW6Vc51MKb0q5P2rRUpPvrszuE4W1povHYgTpBfshb")

    dependencies = [jquery, popper, bootstrapjs, bootstrapcss]
    db.session.add_all(dependencies)
    db.session.commit()


def load_sample_db():
    """Load some basic providers to the database for test purpose.

    This function needs :function:`init_db` to be called first.
    """
    # Create the providers
    koha_search = Provider(
        name="koha search",
        remote_url="https://koha.bulac.fr/cgi-bin/koha/opac-search.pl?idx=&q={param}&branch_group_limit=",
        result_selector="#userresults .searchresults",
        no_result_selector=".span12 p",
        no_result_content="Aucune réponse trouvée dans le catalogue BULAC.")
    koha_booklist = Provider(
        name="koha booklist",
        remote_url="https://koha.bulac.fr/cgi-bin/koha/opac-shelves.pl?op=view&shelfnumber={param}&sortfield=title",
        result_selector="#usershelves .searchresults")

    providers = [
        koha_search,
        koha_booklist]

    # Add them to the database
    db.session.add_all(providers)

    # Commit the transaction
    db.session.commit()

    return providers


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database via command line.

    See `Flask Tutorial - Creating The Database
    <http://flask.pocoo.org/docs/0.12/tutorial/dbinit/>`_
    """
    try:
        init_db()
    except DatabaseError as e:
        print(e)
        print('*** Database NOT initialized!!!')
    else:
        print('*** Database initialized.')


@app.cli.command('loadsampledb')
def loadsampledb_command():
    """Load some basic providers to the database via command line."""
    try:
        load_sample_db()
    except DatabaseError as e:
        print(e)
        print('*** Sample providers NOT loaded!!!')
        print('    > Did you initialize the database first?')
    else:
        print('*** Sample providers loaded.')


@app.errorhandler(sqlalchemy.exc.OperationalError)
def handle_db_operational_error(err):
    # Improve the error message with revelent advice
    if "unable to open database file" in str(err)\
            or "no such table" in str(err):
        msg = "{err} - check if you initialized the database using mincer.init_db() function.".format(err=err)
    else:
        msg = str(err)

    app.logger.error(msg)

    # Let's prevent any database inconsistencies !
    db.session.rollback()

    abort(INTERNAL_SERVER_ERROR, msg)


@app.route("/")
def home():
    """
    Provide a home page of the server.

    .. :quickref: Home; The home page
    """
    return render_template(
        "home.html",
        dependencies={e.name: e for e in Dependency.query.all()},
        providers=Provider.query.order_by(Provider.slug).all(),
        title="Mincer",
        subtitle="Home")


@app.route("/status")
def status():
    """
    Provide a status page showing if all the adaptation works.

    .. :quickref: Status; Get status of all providers
    """
    return render_template(
        "status.html",
        dependencies={e.name: e for e in Dependency.query.all()},
        providers=Provider.query.order_by(Provider.slug).all(),
        title="Mincer",
        subtitle="Status report")


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    """
    Provide an admin page to easily update the JS and CSS dependency.

    .. :quickref: Admin; Configure the application
    """
    if request.method == "POST":
        # Check if we have only the correct keys from the form
        ADMIN_KEYS = frozenset({
            "jquery-js",
            "jquery-js-sha",
            "popper-js",
            "popper-js-sha",
            "bootstrap-js",
            "bootstrap-js-sha",
            "bootstrap-css",
            "bootstrap-css-sha"})
        FORM_KEYS = frozenset([k for k in request.form.keys()])
        if ADMIN_KEYS != FORM_KEYS:
            app.logger.error(
                "Form data provided %s do not match"
                " form data expected %s.",
                FORM_KEYS,
                ADMIN_KEYS
                )
            return "", BAD_REQUEST

        # TODO: check if the url and sha are valid

        # TODO: check for errors
        q = Dependency.query
        jquery_js = q.filter(Dependency.name == "jquery-js").one()
        jquery_js.url = request.form["jquery-js"]
        jquery_js.sha = request.form["jquery-js-sha"]

        popper_js = q.filter(Dependency.name == "popper-js").one()
        popper_js.url = request.form["popper-js"]
        popper_js.sha = request.form["popper-js-sha"]

        bootstrap_js = q.filter(Dependency.name == "bootstrap-js").one()
        bootstrap_js.url = request.form["bootstrap-js"]
        bootstrap_js.sha = request.form["bootstrap-js-sha"]

        bootstrap_css = q.filter(Dependency.name == "bootstrap-css").one()
        bootstrap_css.url = request.form["bootstrap-css"]
        bootstrap_css.sha = request.form["bootstrap-css-sha"]

        db.session.commit()

        # TODO: send a message and display a result page
        flash("Config updated successfully!", "alert-success")

    # GET : We just display the page
    return render_template(
        "admin.html",
        title="Mincer",
        subtitle="Administration",
        dependencies={e.name: e for e in Dependency.query.all()})


@app.route("/status/<string:provider_slug>")
def provider_status(provider_slug):
    # Retrieve the provider from database
    provider = Provider.query.filter(Provider.slug == provider_slug).first()
    if not provider:
        app.logger.error(
            'Provider %s was requested for status but this provider name '
            'does not exist.',
            provider_slug)
        abort(NOT_FOUND)

    return render_template(
        "provider_status.html",
        dependencies={e.name: e for e in Dependency.query.all()},
        provider=provider,
        title=provider.name,
        subtitle="Status report")


# TODO: test this !!!!
@app.route("/example/<string:provider_slug>", methods=['GET', 'POST'])
def example(provider_slug):
    # Method POST
    if request.method == "POST":
        # Check if we have only the correct keys from the form
        if 'search' not in request.form.keys():
            app.logger.error("Form data missing the 'search' key.")
            return "", BAD_REQUEST

        return redirect(
            url_for(
                "providers",
                provider_slug=provider_slug,
                param=request.form['search']))

    # method GET

    # Retrieve the provider from database
    provider = Provider.query.filter(Provider.slug == provider_slug).first()
    # Return the page with no search
    return render_template(
        "example.html",
        dependencies={e.name: e for e in Dependency.query.all()},
        provider=provider,
        title=provider.name,
        subtitle="Test query")


@app.route("/providers/<string:provider_slug>/<string:param>")
@utils.add_response_headers({"Access-Control-Allow-Origin": "*"})
def providers(provider_slug, param):
    """
    Retrieve a search result list from the KOHA server of the BULAC.

    :query string provider_slug: slugified name of the provider as registered
        in the database in the database.
    :query string param: parameter of the request already url encoded
        (meaning space and special char are replaced see `urllib
        <https://docs.python.org/3.6/library/urllib.html>`_ for reference). It
        could be a search query, an list id... all depend of the context. It
        will be transfered to the final provider url registered in the
        database.

    :status 200: everything was ok
    :status 404: when no `param` is provided

    .. :quickref: Search; Retrieve search result list from KOHA
    """
    # Retrieve the provider from database
    provider = Provider.query.filter(Provider.slug == provider_slug).first()
    if not provider:
        app.logger.error(
            'Provider %s was asked for "%s" but this provider name '
            'does not exist.',
            provider_slug,
            unquote_plus(param))
        abort(NOT_FOUND)

    # Build the full remote url by replacing param
    full_remote_url = provider.remote_url.format(param=param)

    # Extract the base url from the full url
    remote_host = utils.get_base_url(full_remote_url)

    # Get the content of the page
    # HACK: we force copy the accept-language from the recieved request
    #       see: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language
    page = requests.get(
        full_remote_url,
        headers={'accept-language': 'fr-FR'}).text

    try:
        # Search for an answer in the page
        answer_div = utils.extract_node_from_html(
            selector=provider.result_selector,
            html=page,
            base_url=remote_host)
        return PyQuery(answer_div)\
            .add_class(HtmlClasses.RESULT)\
            .outer_html()
    except utils.NoMatchError:
        app.logger.info(
            'Provider %s was asked for "%s" but no result structure could be '
            'found in it\'s result page. Now searching for a no result '
            'structure...',
            provider_slug,
            unquote_plus(param))

    # TODO: test test the case where this fails for exemple if we have
    #   a "loading page"
    try:
        # Search for a no answer message in the page
        no_answer_div = utils.extract_content_from_html(
            provider.no_result_selector,
            provider.no_result_content,
            page)
        return PyQuery(no_answer_div)\
            .add_class(HtmlClasses.NO_RESULT)\
            .outer_html()
    except utils.NoMatchError:
        # TODO: test this behavior
        app.logger.error(
            'Provider %s was asked for "%s" but neither result structure nor '
            'a no result message could be found in it\'s result page. The '
            'remote url used was <%s>.',
            provider_slug,
            unquote_plus(param),
            full_remote_url)
        # TODO: replace this with a valide answer
        abort(BAD_REQUEST)

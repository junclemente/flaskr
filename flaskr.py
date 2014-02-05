# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2014 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort
from flask import render_template, flash
from contextlib import closing
import pdb


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
# app.config.update(dict(
#     DATABASE='flaskr.db',  # renamed from /tmp/flaskr.db
#     DEBUG=True,
#     SECRET_KEY='development key',
#     USERNAME='admin',
#     PASSWORD='default'
# ))
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    # pdb.set_trace()
    # rv = sqlite3.connect(app.config['DATABASE'])
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Creates the database tables."""
    # with app.app_context():
    #     db = get_db()
    #     with app.open_resource('schema.sql', mode='r') as f:
    #         db.cursor().executescript(f.read())
    #     db.commit()
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


# @app.teardown_appcontext
# def close_db(error):
#     """Closes the database again at the end of the request."""
#     if hasattr(g, 'sqlite_db'):
#         g.sqlite_db.close()
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.before_request
def before_request():
    g.db = connect_db()


@app.route('/')
def show_entries():
    # db = get_db()
    # pdb.set_trace()
    cur = g.db.execute('select title, text from entries order by id desc')
    # entries = cur.fetchall()
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # pdb.set_trace()
    error = None
    if request.method == 'POST':
        # if request.form['username'] != app.config['USERNAME']:
        if request.form['username'] != USERNAME:
            error = 'Invalid username'
        # elif request.form['password'] != app.config['PASSWORD']:
        elif request.form['password'] != PASSWORD:
            error = 'Invalid password'
        else:
            # pdb.set_trace()
            session['logged_in'] = True
            # flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    init_db()
    app.run()

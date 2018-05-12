import os
import sys
import sqlite3
from flask import jsonify
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)  # create the application instance :)
app.config.from_object(__name__)  # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'backend.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    print("executed schema.sql successfully.")
    with app.open_resource('schema_history.sql', mode='r') as f:
        db.cursor().executescript(f.read())

    db.commit()


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

# ROUTES
@app.route('/set_workers', methods=['POST']):
    db = get_db()
    if request.method == 'POST':
        db.execute('insert into workers (at_work, '
                   'name) values (?, ?)',
                   [request.form['at_work'],
                    request.form['name']])
        db.commit()
        flash("New entry was successfully posted")
    return 'OK'

@app.route('/worker_history', methods=['POST']):
    db = get_db()
    if request.method == 'POST':
        cursor = db.execute('select at_work from workers'
                            'where worker_id == ?',
                            [request.args.get('worker_id')])
        at_work = False
        for row in cursor.fetchall():
            at_work = bool(row)
        if at_work:
            # GET LATEST ENTRY BY HISTORY ID
            # UPDATE
            cursor = db.execute('update worker_history'
                                'set start_work = ?, '
                                'end_work = ?, '
                                'hours_worked = ? '
                                'where history_id in (select history_id from '
                                'worker_history order by id desc limit 1 where worker_id === ?)',
                                [request.form['start_work'],request.form['end_work'],
                                 request.form['hours_worked'],request.args.get('worker_id')])
        else:
            # INSERT
            cursor = db.execute('insert into worker_history (start_work, end_work, hours_worked, worker_id) '
                                'values (?, ?, ?,?)',
                                [request.form['start_work', request.form['end_work'],
                                 request.form['hours_worked'],request.args.get('worker_id')])
        db.commit()
    return 'OK'

if __name__ == '__main__':
    if sys.argv[1] == 'dbinit':
        print("init db")
        with app.app_context():
            init_db()
    elif sys.argv[1] == 'run':
        print('running app...')
        app.run()
    else:
        raise ValueError("incorrect nr of args!")

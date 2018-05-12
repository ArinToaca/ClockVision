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


@app.route('/worker', methods=['POST'])
def set_worker():
    db = get_db()
    if request.method == 'POST':
        db.execute('insert into workers (at_work, '
                   'name) values (?, ?)',
                   [0,  # initially the new worker is not at work.
                    request.form['name']])
        db.commit()
        flash("New entry was successfully posted")
        result = dict()
        cursor = db.execute('select worker_id from workers order by '
                            'worker_id desc limit 1')
        result['worker_id'] = cursor.fetchone()[0]
        return jsonify(result)
    elif request.method == 'GET':
        cursor = db.execute('select * from workers where '
                            'worker_id == ?', request.args.get('worker_id'))
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()
        result = dict(zip(columns, row))
        return jsonify(result)

    return 'OK'


@app.route('/worker_history', methods=['POST', 'GET'])
def worker_history():
    db = get_db()
    if request.method == 'POST':
        cursor = db.execute('select at_work from workers'
                            'where worker_id == ?',
                            [request.args.get('worker_id')])

        start_work, end_work = 0, 0
        at_work = not bool(cursor.fetchone()[0])
        if at_work:
            start_work = request.form['timestamp']
            # INSERT NEW HISTORY
            db.execute('insert into worker_history (start_work, '
                       'end_work, hours_worked, worker_id) '
                       'values (?, ?, ?,?)',
                       [start_work,
                        end_work,
                        0,  # field only valid at end of workday.
                        request.args.get('worker_id')])
            db.execute('update workers'
                       'set at_work = ?'
                       'where worker_id == ?',
                       [at_work,
                        request.args.get('worker_id')])
        else:
            end_work = request.form['timestamp']
            # UPDATE EXISTING HISTORY
            # get last entry history_id associated with worker_id
            cursor = db.execute('select history_id from worker_history where '
                                'worker_id == ? order by history_id '
                                'desc limit 1',
                                [request.args.get('worker_id')])
            history_id = cursor.fetchone()[0]
            # for worker_history table
            db.execute('update worker_history'
                       'set start_work = ?, '
                       'end_work = ?, '
                       'hours_worked = ? '
                       'where history_id == ?'
                       [start_work,
                        end_work,
                        (end_work - start_work),  # simple diff atm
                        history_id])
            # for workers table
            db.execute('update workers'
                       'set at_work = ?'
                       'where worker_id == ?',
                       [at_work,
                        request.args.get('worker_id')])
        db.commit()
        flash("Successfully added timestamp.")
        return 'OK'

    elif request.method == 'GET':
        # get worker_history & if worker is at work
        cursor = db.execute('select * from worker_history where '
                            'worker_id == ?', request.args.get('worker_id'))
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        cursor = db.execute('select at_work from workers where worker_id == ?',
                            request.args.get('worker_id'))
        return jsonify(results)

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

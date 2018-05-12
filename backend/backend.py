import os
import string
import random
import base64
import sys
import sqlite3
from flask import jsonify
from flask_cors import CORS, cross_origin
from flask import send_from_directory
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

design = {0: 'off', 1: 'on'}
app = Flask(__name__)  # create the application instance :)
app.config.from_object(__name__)  # load config from this file , flaskr.py
app.config['CORS_HEADERS'] = 'Content-Type'

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


@app.route('/worker', methods=['POST', 'GET'])
@cross_origin()
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
        results = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
            results[-1]['at_work'] = design[results[-1]["at_work"]]
        return jsonify(results[0])
    return 'OK'


@app.route('/worker_history', methods=['POST', 'GET'])
@cross_origin()
def get_worker_history():
    '''Fetch respective worker work history'''
    db = get_db()
    if request.method == 'POST':
        cursor = db.execute('select at_work from workers '
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
            db.execute('update workers '
                       'set at_work = ? '
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
            db.execute('update worker_history '
                       'set end_work = ?, '
                       'hours_worked = ? '
                       'where history_id == ? ',
                       [end_work,
                        (int(end_work) - start_work),  # simple diff atm
                        history_id])
            # for workers table
            db.execute('update workers '
                       'set at_work = ? '
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
            results[-1]['at_work'] = design[results[-1]["at_work"]]
        cursor = db.execute('select at_work from workers where worker_id == ?',
                            request.args.get('worker_id'))
        return jsonify(results)

    return 'OK'


@app.route('/all_workers', methods=['GET'])
@cross_origin()
def get_all_workers():
    '''Listing everything in the database'''
    db = get_db()
    cursor = db.execute('select * from workers')
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
        cursor_history = db.execute('select * from worker_history where '
                                    'worker_id == ?',
                                    [results[-1]['worker_id']])
        columns_history = [column[0] for column in cursor_history.description]
        work_history = []
        for row_history in cursor_history.fetchall():
            work_history.append(dict(zip(columns_history, row_history)))
        results[-1]["worker_history"] = work_history
        results[-1]['at_work'] = design[results[-1]["at_work"]]

    return jsonify(results)


@app.route('/raspi', methods=['POST'])
def raspi_post():
    image_data = request.form['image']
    extension = request.form['png']
    N = 10
    #  Random string generation for image files
    filename = ''.join(random.choices(
                       string.ascii_uppercase + string.digits, k=N))
    with open("./static" + str(filename) + str(extension), "wb") as fh:
        fh.write(base64.decodebytes(image_data.encode()))

    result = dict()
    result['name'] = "Test Testescu"
    result['status'] = 'entered'

    return result


@app.route('/uploads/<path:filename>')
@cross_origin()
def download_file(filename):
    '''Image fetching'''
    return send_from_directory('./static',
                               filename, as_attachment=True)


if __name__ == '__main__':
    if sys.argv[1] == 'dbinit':
        print("init db")
        with app.app_context():
            init_db()
    elif sys.argv[1] == 'run':
        print('running app...')
        app.run(host='0.0.0.0')
    else:
        raise ValueError("incorrect nr of args!")

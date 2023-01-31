from flask import render_template, jsonify, request, redirect, flash, url_for
from urllib.parse import urlparse

from pack import app
from parser.tasks import main_parse


def is_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except ValueError:
    return False


@app.route('/start_parse', methods=['POST'])
def start_parse():
    if request.method == 'POST':
        link_resume = request.form['link_resume']
        if is_url(link_resume) == False:
            flash('Ссылка некоректна!')
            return redirect('https://www.youtube.com/watch?v=GJ2RdGHizs8')
        async_result = main_parse.apply_async(args=[link_resume])
        task_id = async_result.id
        return jsonify({}), 202, {'Location': url_for('task_status',
                                                  task_id=task_id)}


@app.route('/status/<task_id>')
def task_status(task_id):
    task = main_parse.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Start find...'
        }
    elif task.state == 'TOOK_RESUME':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Start find...',
            'client_resume': task.info['client_resume']}
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            #response['result'] = task.info['result']
            vacancy = task.info['result']
            return jsonify({'result': 'Ready','htmlresponse': render_template('find.html', vacancy=vacancy)})
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')

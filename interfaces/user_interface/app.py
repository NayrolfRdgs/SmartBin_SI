from flask import Flask, jsonify, request, render_template
import uuid
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='static')

tasks = {}

try:
    from src.config import USER_INTERFACE_PORT, VALID_BINS
except Exception:
    USER_INTERFACE_PORT = 5001
    VALID_BINS = ['yellow','green','brown']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.get_json() or {}
    item_name = data.get('item_name')
    if not item_name:
        return jsonify({'success': False, 'error': 'item_name requis'}), 400
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'item_name': item_name, 'created': datetime.now().isoformat(), 'answered': False, 'bin_color': None}
    return jsonify({'success': True, 'task_id': task_id}), 202

@app.route('/api/tasks')
def list_tasks():
    pending = [{'task_id': tid, 'item_name': t['item_name'], 'created': t['created']} for tid,t in tasks.items() if not t['answered']]
    return jsonify({'success': True, 'pending': pending})

@app.route('/api/answer/<task_id>', methods=['GET','POST'])
def answer(task_id):
    t = tasks.get(task_id)
    if not t:
        return jsonify({'success': False, 'error': 'non trouvé'}), 404
    if request.method == 'GET':
        return jsonify({'success': True, 'answered': t['answered'], 'bin_color': t['bin_color']})
    data = request.get_json() or {}
    bin_color = data.get('bin_color')
    if not bin_color:
        t['answered'] = True
        t['bin_color'] = None
        return jsonify({'success': True, 'task_id': task_id, 'bin_color': None})
    if bin_color not in VALID_BINS:
        return jsonify({'success': False, 'error': 'bin invalide'}), 400
    t['answered'] = True
    t['bin_color'] = bin_color
    return jsonify({'success': True, 'task_id': task_id, 'bin_color': bin_color})

@app.route('/api/valid_bins')
def valid_bins():
    return jsonify({'success': True, 'bins': VALID_BINS})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=USER_INTERFACE_PORT)

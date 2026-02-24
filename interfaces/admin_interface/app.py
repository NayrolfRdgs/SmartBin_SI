from flask import Flask, jsonify, request, render_template
import os
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='static')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/config/read')
def read_config():
    try:
        from pathlib import Path
        repo_root = Path(__file__).resolve().parents[2]
        cfg_path = repo_root / 'src' / 'config.py'
        with open(cfg_path, 'r', encoding='utf-8') as f:
            return jsonify({'success': True, 'content': f.read(), 'path': str(cfg_path)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/config/save', methods=['POST'])
def save_config():
    try:
        data = request.get_json() or {}
        content = data.get('content', '')
        from pathlib import Path
        repo_root = Path(__file__).resolve().parents[2]
        cfg_path = repo_root / 'src' / 'config.py'
        with open(cfg_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'success': True, 'path': str(cfg_path)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/bins/status')
def bins_status():
    try:
        import sys
        from pathlib import Path
        src_dir = Path(__file__).resolve().parent.parent / 'src'
        sys.path.insert(0, str(src_dir))
        import waste_classifier
        waste_classifier.init_database()
        bins = waste_classifier.get_bin_status()
        waste_classifier.cleanup()
        return jsonify({'success': True, 'bins': bins})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/bins/history')
def bins_history():
    try:
        import sys
        from pathlib import Path
        src_dir = Path(__file__).resolve().parent.parent / 'src'
        sys.path.insert(0, str(src_dir))
        import waste_classifier
        waste_classifier.init_database()
        history = waste_classifier.get_detection_history(50)
        waste_classifier.cleanup()
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/waste/classify', methods=['POST'])
def waste_classify():
    try:
        data = request.get_json() or {}
        item_name = data.get('item_name')
        if not item_name:
            return jsonify({'success': False, 'error': 'item_name requis'})
        import sys
        from pathlib import Path
        src_dir = Path(__file__).resolve().parent.parent / 'src'
        sys.path.insert(0, str(src_dir))
        import waste_classifier
        waste_classifier.init_database()
        bin_color = waste_classifier.classify_and_sort(item_name, ask_if_unknown=True, auto_mode=False)
        waste_classifier.cleanup()
        if bin_color:
            return jsonify({'success': True, 'bin_color': bin_color})
        return jsonify({'success': False, 'error': 'Non trié'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

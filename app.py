from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from ingest import QuestionAnswer
from threading import Thread
from websocket import start_websocket
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat.js')
def chat():
    return render_template('chat.js')


@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']
    print(request)
    # 当前文件所在路径
    base_path = os.path.dirname(__file__)
    upload_path = os.path.join(base_path, 'docs', secure_filename(f.filename))
    f.save(upload_path)
    qa = QuestionAnswer(name="test")

    _, extension = os.path.splitext(upload_path)
    qa.add_file(upload_path, extension.lstrip('.'))
    return jsonify({"code": 200, "msg": "上传成功"})


@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    print(data)
    qa = QuestionAnswer(name="test")
    msg = qa.query(data['query'])
    return jsonify({"code": 200, "msg": msg})


def start_flask():
    app.run(host='0.0.0.0', port=5002, use_reloader=False)


if __name__ == '__main__':
    # 这里同时启动两个线程，一个是websocket服务，一个是flask服务
    ws_server = Thread(target=start_flask)
    ws_server.start()
    start_websocket()

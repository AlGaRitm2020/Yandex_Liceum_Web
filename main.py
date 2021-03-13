from flask import Flask, render_template, request
import os

UPLOAD_FOLDER = 'static/img'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# main
file_path = 'static/img/robot.png'
@app.route('/',  methods=['POST', 'GET'])
# @app.route('/results/<nickname>/<int:level>/<float:rating>')
def form():
    global file_path
    # import index from html
    if request.method == 'GET':

        return render_template('index.html', src=file_path)

    elif request.method == "POST":

        f = request.files['file']
        print(f.filename)
        file_path = f'{UPLOAD_FOLDER}/{f.filename}'
        f.save(file_path)

        return render_template('index.html', src=file_path)




if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')

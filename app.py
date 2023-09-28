from flask import Flask, render_template, request, redirect
from flask_cors import CORS


app = Flask(__name__)

@app.route('/upload', methods=['POST', 'GET'])
def detect():
    if (request.method == 'POST'):
        req = request.form
        print(req)
        title = req['title']
        print(title)

    return render_template('upload.html')

@app.route('/feed', methods=['POST', 'GET'])
def feed():
    return render_template('feed.html')

@app.route('/about', methods=['POST', 'GET'])
def about():
    return render_template('about.html', param = "HEllo")


if __name__ == '__main__':
    app.run(port = '5000', debug=True)
    
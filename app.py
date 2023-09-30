from flask import Flask, render_template, request, redirect
from flask_cors import CORS
import base64
import uuid

from db_access import *

app = Flask(__name__)

def generate_unique_filename():
    # Generate a UUID and convert it to a string
    unique_id = str(uuid.uuid4())
    # Remove hyphens and return the unique filename
    return unique_id.replace('-', '')

@app.route('/upload', methods=['POST', 'GET'])
def detect():
    if (request.method == 'POST'):
        req = request.form
        print(request.files)
        imagesData = req['blob'].split(' ')
        imagesData.pop()
        imageName = []

        for imageData in imagesData:
            data = base64.b64decode(imageData)
            uniqueName = generate_unique_filename()
            imageName.append(uniqueName)
            with open("static/post_images/" + uniqueName + ".jpg", 'wb') as f:
              f.write(data)
        
        dict = {
            'description': req['desc'],
            'coordinates': req['coordinates'],
            'waste_type': req['waste-category'],
            'image': imageName
        }
        print(dict)
        storePost(dict)
        return redirect('/upload')

    return render_template('upload.html')

@app.route('/feed', methods=['POST', 'GET'])
def feed():
    return render_template('feed.html')

@app.route('/post', methods=['POST', 'GET'])
def post():
    return render_template('post.html')

@app.route('/about', methods=['POST', 'GET'])
def about():
    return render_template('about.html', param = "HEllo")

@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if (request.method == 'POST'):
        req = request.form
        print(req)
        return redirect('/register')
    return render_template('register.html')

@app.route('/resetpassword', methods=['POST', 'GET'])
def resetpassword():
    return render_template('reset.html')

@app.route('/forgotpassword', methods=['POST', 'GET'])
def forgotpassword():
    return render_template('forgot.html')

if __name__ == '__main__':
    app.run(port = '5000', debug=True)
    

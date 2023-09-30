from flask import Flask, render_template, request, redirect, jsonify, make_response
from flask_cors import CORS
import base64
import uuid
import bcrypt

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
    if (request.method == 'POST'):
        req = request.form
        print(req)

        user_collection = fetchUserByEmail(req['email'])

        if user_collection is not None:
            print(user_collection)
            entered_password = req['password'].encode('utf-8')

            if bcrypt.checkpw(entered_password,  user_collection['password']):
                print("Password is correct!")
                response = make_response("Login Successful")
                response.set_cookie('user_id', str(user_collection['_id']))
                return response
            
            else:
                print("Password is incorrect.")
        else:
            print("No user with such email")
        
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if (request.method == 'POST'):
        req = request.get_json()
        print(req)
        #put in db_access#
        if(req['email'] == 'anindyakbiswas5@gmail.com'):
            #already exists
            print("Already exists")
            return "true"
        else:
            #make a db entry
            print("New email address")
            
            password = req['password'].encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password, salt)

            dict = {
                'name': req['name'],
                'coordinates': req['coordinates'],
                'email': req['email'],
                'password': hashed_password
            }
            print(dict)
            # if registerDb(dict) is not None:
            #     return redirect('/login')
            # else:
            #     print("Email exists")
            
            return "false"

        
    return render_template('register.html')

@app.route('/resetpassword', methods=['POST', 'GET'])
def resetpassword():
    return render_template('reset.html')

@app.route('/forgotpassword', methods=['POST', 'GET'])
def forgotpassword():
    return render_template('forgot.html')

if __name__ == '__main__':
    app.run(port = '5000', debug=True)
    

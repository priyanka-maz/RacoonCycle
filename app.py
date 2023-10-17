from flask import Flask, render_template, request, redirect, jsonify, make_response
from flask_cors import CORS
import base64
import uuid
import bcrypt
import os
import json
import time

from db_access import *

app = Flask(__name__)

def generate_unique_filename():
    # Generate a UUID and convert it to a string
    unique_id = str(uuid.uuid4())
    # Remove hyphens and return the unique filename
    return unique_id.replace('-', '')

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if (request.method == 'POST'):
        req = request.form
        if(req['user_id'] != ''):
            imagesData = req['blob'].split(' ')
            imagesData.pop()
            imageName = []

            for imageData in imagesData:
                data = base64.b64decode(imageData)
                uniqueName = generate_unique_filename()
                imageName.append(uniqueName)

                script_path = os.path.abspath(__file__)

                app_directory = os.path.dirname(script_path)

                static_directory = os.path.join(app_directory, "static/post_images/" + uniqueName + ".jpg")

                with open(static_directory, 'wb') as f:
                    f.write(data)
            
            lat = float(req['coordinates'].split(' ')[0])
            lon = float(req['coordinates'].split(' ')[1])
            dict = {
                'description': req['desc'],
                'waste_type': req['waste-category'] if req.get('waste-category') is not None else '',
                'image': imageName,
                'user_id': req['user_id'],
                'location' :  {"type": "Point", "coordinates": [lat, lon]}
            }
            print(dict)
            storePost(dict)
            return redirect('/feed')

    return render_template('upload.html')

@app.route('/feed_old', methods=['POST', 'GET'])
def feed():
    posts = getPost()
    return render_template('feed_old.html', posts = posts)

@app.route('/feed', methods=['POST', 'GET'])
def feed2():
    return render_template('feed.html')

@app.route('/load_feed', methods=['POST', 'GET'])
def load_feed():
    time.sleep(0.2)
    page = request.args.get('page')
    order = request.args.get('order')
    sort = request.args.get('sort')
    print("Sort value = ", sort)
    if(order == 'latest'):
        print('\n\nLATEST\n\n')
        posts = getPostsForFeed(page_no=page, sort=sort)
        return json.dumps(posts, default=str)
    elif(order == 'home'):
        print('\n\nCLOSE to HOME\n\n')
        uid = request.args.get('uid')
        posts = getPostsForFeed(page_no=page, uid=uid, sort=sort)
        return json.dumps(posts, default=str)
    elif(order == 'location'):
        print('\n\nCLOSE to CURRENT LOCATION\n\n')
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        posts = getPostsForFeed(page_no=page, location = [float(lat), float(lon)], sort=sort)
        print("Location Posts - > ",posts)
        return json.dumps(posts, default=str)

@app.route('/load_profile', methods=['POST', 'GET'])
def load_profile():
    time.sleep(0.5)
    page = request.args.get('page')
    profile_id = request.args.get('profile_id')
    posts = getPostsForProfile(page_no=page, profile_id = profile_id)
    print(posts)
    return json.dumps(posts, default=str)

@app.route('/post', methods=['POST', 'GET'])
def post():
    if(request.method == 'GET'):
        post_id = request.args.get('id')
        post = getPost(post_id)
        
        return render_template('post.html', post=post)
    
    elif(request.method == 'POST'):
        req = request.form
        print(req)
        if(req['user_id'] != ''):
            imagesData = req['blob'].split(' ')
            imagesData.pop()
            imageName = []
            for imageData in imagesData:
                data = base64.b64decode(imageData)
                uniqueName = generate_unique_filename()
                imageName.append(uniqueName)

                script_path = os.path.abspath(__file__)

                app_directory = os.path.dirname(script_path)

                static_directory = os.path.join(app_directory, "static/post_images/" + uniqueName + ".jpg")

                with open(static_directory, 'wb') as f:
                    f.write(data)
            
            dict = {
                'description': req['desc'],
                'image': imageName,
                'user_id': req['user_id']
            }
            postResolved(req['post_id'], dict)
        return redirect('/post?id='+str(req.get('post_id')))

@app.route('/userhome', methods=['POST', 'GET'])
def userhome():
    uid = request.args.get('uid')
    lat, lon = getUserHome(uid)
    location = [lat, lon]
    return location

@app.route('/about', methods=['POST', 'GET'])
def about():
    
    return render_template('about.html', param = "HEllo")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if (request.method == 'POST'):
        req = request.get_json()
        print(req)

        user_collection = fetchUserByEmail(req['email'])

        if user_collection is not None:
            print(user_collection)
            entered_password = req['password'].encode('utf-8')

            if bcrypt.checkpw(entered_password,  user_collection['password']):
                print("Password is correct!")
                uid = str(user_collection['_id'])
                return uid
                # profile redirect
            
            else:
                print("Password is incorrect.")
                return "wrong_password"
        else:
            print("No user with such email")
            return "wrong_email"
        
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if (request.method == 'POST'):
        req = request.get_json()
        print(req)
        
        # if cookie then profile
        password = req['password'].encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt)

        dict = {
            'name': req['name'],
            'coordinates': req['coordinates'],
            'email': req['email'],
            'password': hashed_password
        }
        if registerDb(dict) is not None:
            print("Email doesnt exist")
            return "false"
        else: #None
            print("Email exists")
            return "true"

        
    return render_template('register.html')


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    uid = request.args.get('id')
    user_info = fetchUserByUID(uid)
    return render_template('profile.html', user_info = user_info)

if __name__ == '__main__':
    app.run(port = '5000', debug=True)
    

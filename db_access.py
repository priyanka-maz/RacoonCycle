from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

client = MongoClient('localhost', 27017)

def storePost(dict):
    
    racoon_db = client.racoon_db
    user_collection = racoon_db.user
    post_collection = racoon_db.post
    #id of user
    id = ObjectId(dict['user_id'])
    
    
    #insert post info into post_collection
    post = post_collection.insert_one(dict)
    
    #update user_collection with the new post
    user_collection.update_one({'_id': id}, {'$push':{'posts': post.inserted_id}})


## For feed page
def getPostsForFeed(page_no=1, limit = 2, uid = None, location = None):
    racoon_db = client.racoon_db
    post_collection = racoon_db.post
    posts = []
    skip = (int(page_no)-1)*limit
    #Latest post 
    if(uid is None and location is None):
        for i in post_collection.find().sort("_id", -1).skip(skip).limit(limit):
            i['user_name'] = fetchUserByUID(i['user_id'])['name']
            i['timestamp'] = i['_id'].generation_time
            posts.append(i)
        return posts
    #Closest to Home
    elif(uid is not None):
        #get home coordinates from uid
        user_lat, user_lon = getUserHome(uid)
        pipeline = [{
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [user_lat, user_lon]
                    },
                    "distanceField": "distance",
                    "spherical": True,
                    "key": "location"  # Use the "location" field for geospatial indexing
                }
            }, { "$skip":skip }, { "$limit":limit }]
        posts = list(post_collection.aggregate(pipeline))
        for i in posts:
            i['timestamp'] = i['_id'].generation_time
            i['user_name'] = fetchUserByUID(i['user_id'])['name']
            print(i['distance'])
        return posts
    
    #Closest to Current Location
    elif(location is not None):
        print("FROM DB_ACCESS : ", location)
        pipeline = [{
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": location
                    },
                    "distanceField": "distance",
                    "spherical": True,
                    "key": "location"  # Use the "location" field for geospatial indexing
                }
            }, { "$skip":skip }, { "$limit":limit }]
        posts = list(post_collection.aggregate(pipeline))
        for i in posts:
            i['timestamp'] = i['_id'].generation_time
            i['user_name'] = fetchUserByUID(i['user_id'])['name']
            print(i['distance'])
        return posts

def getPostsForProfile(profile_id, page_no=1, limit = 2):
    racoon_db = client.racoon_db
    post_collection = racoon_db.post
    posts = []
    skip = (int(page_no)-1)*limit
    #Latest post 
    for i in post_collection.find({"user_id":profile_id}).sort("_id", -1).skip(skip).limit(limit):
        i['timestamp'] = i['_id'].generation_time
        i['user_name'] = fetchUserByUID(i['user_id'])['name']
        posts.append(i)
    return posts  
    
#For post page    
def getPost(post_id):
    racoon_db = client.racoon_db
    post_collection = racoon_db.post
    post = None
    if ObjectId.is_valid(post_id):
        objInstance = ObjectId(post_id)
        post = post_collection.find_one({"_id": objInstance})
        if post is not None:
            post['timestamp'] = post['_id'].generation_time
            post['user_name'] = fetchUserByUID(post['user_id'])['name']
            if post.get('resolved') is not None:
                post['resolved']['name'] =  fetchUserByUID(post['resolved']['user_id'])['name']
    return post

def postResolved(post_id, dict):
    racoon_db = client.racoon_db
    post_collection = racoon_db.post
    user_collection = racoon_db.user
    user_id = ObjectId(dict['user_id'])
    user_collection.update_one({"_id": user_id}, {'$push': {'resolved': post_id}})
    if ObjectId.is_valid(post_id):
        post_id = ObjectId(post_id)
        dict['timestamp'] = datetime.now()
        print(post_id)
        print(dict)
        post_collection.update_one({'_id': post_id}, {'$set':{'resolved': dict}})
            

def registerDb(dict):
    racoon_db = client.racoon_db
    user_collection = racoon_db.user

    query = {"email": dict['email']}
    user_document = user_collection.find_one(query)
    print("Doc: ", user_document)
    if user_document:
        #email already exists
        return None
    else:
        user_collection.insert_one(dict)
        for i in user_collection.find():
            print(i)
        return "yes new user"

def fetchUserByEmail(email):
    racoon_db = client.racoon_db
    user_collection = racoon_db.user

    query = {"email": email}

    # Use find_one to retrieve the first document that matches the filter
    user_document = user_collection.find_one(query)

    # Check if a user with the given email was found
    if user_document:
        return user_document
    else:
        return None

def fetchUserByUID(uid):
    racoon_db = client.racoon_db
    user_collection = racoon_db.user
    user_info = None
    if ObjectId.is_valid(uid):
        id = ObjectId(uid)
        user_info = user_collection.find_one({"_id": id},{"_id":1, "name":1, "email":1, "posts":1})
        if user_info is not None:
            user_info['join_time'] = user_info['_id'].generation_time
            user_info['post_count'] = len(user_info['posts'])
            print("length -> ", len(user_info['posts']))
            del user_info['posts']

    return user_info
    
def getUserHome(uid):
    racoon_db = client.racoon_db
    user_collection = racoon_db.user
    objInstance = ObjectId(uid)
    user = user_collection.find_one({"_id": objInstance})
    print(user['coordinates'])
    lat = float(user['coordinates'].split(' ')[0])
    lon = float(user['coordinates'].split(' ')[1])
    
    return lat, lon


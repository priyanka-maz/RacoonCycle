from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('localhost', 27017)

def storePost(dict):
    
    racoon_db = client.racoon_db
    user_collection = racoon_db.user
    post_collection = racoon_db.post
    #id of user
    id = ObjectId(dict['user_id'])
    
    #add username of the poster for easier username access
    dict['user_name'] =  user_collection.find_one({'_id': id})['name']
    
    #insert post info into post_collection
    post = post_collection.insert_one(dict)
    
    #update user_collection with the new post
    user_collection.update_one({'_id': id}, {'$push':{'posts': post.inserted_id}})


def getPost(id=None):
    racoon_db = client.racoon_db
    post_collection = racoon_db.post
    ## For feed page
    if(id is None):
        posts = []
        for i in post_collection.find().sort("_id", -1).limit(10):
            i['timestamp'] = i['_id'].generation_time
            posts.append(i)
        return posts
    ## For post page
    else:
        print(id)
        objInstance = ObjectId(id)
        post = post_collection.find_one({"_id": objInstance})
        post['timestamp'] = post['_id'].generation_time
        return post

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

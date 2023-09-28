from pymongo import MongoClient

client = MongoClient('localhost', 27017)

exam_db = client.test_db2

student_collection = exam_db.scholars

badges = ['ceo', 'student', 'supplier']

dict = {
    "name" : "Cohn Jena 2",
    "roll" : "963",
    "badges" : badges
}

student_collection.insert_one(dict)

for i in student_collection.find({},{'_id':0}):
    print(i)


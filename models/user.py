import json
from bson.objectid import ObjectId
from connectMongo import connect_mongodb

db = connect_mongodb()
users_collection = db["myuser"]

class User:
    def __init__(self, id = None):
        if id != None:
            user = list(users_collection.find({"_id" : ObjectId(id)}))
            for u in user:
                u["_id"] = str(u["_id"])
            self.user = user[0]
        else:
            self.user = {}
    
    def add_user(self):
        response = users_collection.insert_one(self.user)
        u = User(response.inserted_id)
        return u

    def update_user(self):
        response = users_collection.update_one(
            {"_id" : ObjectId(self.user["_id"])},
            {"$set" :{"email":self.user["email"], "firstname":self.user["firstname"], "lastname":self.user["lastname"], "admin":self.user["admin"]}}
        )
        if response.matched_count  == 1:
            print("update worked")
        else:
            print("coudnt update")
    
    def add_secret(self, secret):
        response = users_collection.update_one(
            {"_id" : ObjectId(self.user["_id"])},
            {'$push': {'secrets': secret}}
        )
        if response.matched_count  == 1:
            return True
        else:
            return False

    def remove_secret(self, secret):
        response = users_collection.update_one(
            {"_id" : ObjectId(self.user["_id"])},
            {'$pull': {'secrets': secret}}
        )
        if response.matched_count  == 1:
            return True
        else:
            return False

    @staticmethod
    def delete_user(id):
        response = users_collection.delete_one({"_id" : ObjectId(id)})
        if response.deleted_count == 1:
            print("delete worked")
            print(response)
            return 1
        else:
            print("couldnt delete")
            return 0
    
    @staticmethod
    def login(email, password):
        user = list(users_collection.find({"email" : email, "password" : password}))
        if(len(user) > 0):
            u = User(user[0]["_id"])
            return u
        return -1

    @staticmethod
    def get_users():
        users = list(users_collection.find({}))
        for u in users:
            u["_id"] = str(u["_id"])
        return users

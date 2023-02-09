#!/usr/local/environments/flask/lib/python3.6
import os
import pymongo
from bson import ObjectId

DATABASE = "waitercaller"


class DBHelper:

    def __init__(self):
        client = pymongo.MongoClient()
        self.db = client[DATABASE]

    def get_user(self, email):
        return self.db.users.find_one({"email": email})

    def add_user(self, place, email, salt, hashed):
        self.db.users.insert_one({"place": place,  "email": email, 
                                "salt": salt, "hashed": hashed})

    def add_table(self, number, owner):
        new_id = self.db.tables.insert_one({"number": number, "owner": owner})
        return new_id.insertedId.toString()

    def update_table(self, _id, url, qrc):
        self.db.tables.update_one({"_id": ObjectId(_id)}, {"$set": {"url": url, "qrc": qrc}})

    def get_tables(self, owner_id):
        return list(self.db.tables.find({"owner": owner_id}))

    def get_table(self, table_id):
        return self.db.tables.find_one({"_id": ObjectId(table_id)})

    def delete_table(self, table_id):
        self.db.tables.delete_one({"_id": ObjectId(table_id)})

    def add_request(self, table_id, time):
        table = self.get_table(table_id)
        try:
            self.db.requests.insert_one({"owner": table['owner'], "table_number": table[
                                    'number'], "table_id": table_id, "time": time})
            return True
        except pymongo.errors.DuplicateKeyError:
            return False

    def get_requests(self, owner_id):
        return list(self.db.requests.find({"owner": owner_id}))

    def delete_request(self, request_id):
        self.db.requests.delete_one({"_id": ObjectId(request_id)})

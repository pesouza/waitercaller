import os
import pymongo
from bson import ObjectId
from os.path import join, dirname, realpath
from time import time

DATABASE = "waitercaller"
IMAGES_PATH = join(dirname(realpath(__file__)), 'static')
expire_time = 60

class DBHelper:

    def __init__(self):
        client = pymongo.MongoClient()
        self.db = client[DATABASE]

    def get_user(self, email):
        return self.db.users.find_one({"email": email})

    def add_user(self, place, email, salt, hashed, token):
        self.db.users.insert_one({"place": place,  "email": email, 
                                "salt": salt, "hashed": hashed, 
                                "confirmed": False, "token": token})

    def confirm_email(self, token):
        user = self.db.users.find_one({"token": token})
        if user['_id']:
            self.db.users.update_one({"_id": user['_id']}, {"$set": {"token": None, "confirmed": True}})
            return True
        return False


    def add_table(self, number, owner):
        new_id = self.db.tables.insert_one({"number": number, "owner": owner}).inserted_id
        return new_id

    def update_table(self, _id, url, qrc):
        self.db.tables.update_one({"_id": _id}, {"$set": {"url": url, "qrc": qrc}})
        if owner_id == self.get_user('mail@exemplo.com.br'):
            self.db.tables.update_one({"_id": _id}, {"$set": {"expire_time": time() + expire_time}})
        

    def get_tables(self, owner_id):
        return list(self.db.tables.find({"owner": owner_id}))

    def get_table(self, table_id):
        return self.db.tables.find_one({"_id": ObjectId(table_id)})

    def delete_table(self, table_id):
        table = self.get_table(table_id)
        if os.path.exists(f'{IMAGES_PATH}/{table["qrc"]}'):
            os.remove(f'{IMAGES_PATH}/{table["qrc"]}')
        self.db.tables.delete_one({"_id": ObjectId(table_id)})

    def add_request(self, table_id, time):
        table = self.get_table(table_id)
        res = self.db.requests.count_documents({"table_id": table_id})
        if res > 0:
            return False
        else:
            self.db.requests.insert_one({"owner": table['owner'], "table_number": table[
                                    'number'], "table_id": table_id, "time": time})
            return True

    def get_requests(self, owner_id):
        if owner_id == self.get_user('mail@exemplo.com.br'):
            self.remove_expired_records()
        return list(self.db.requests.find({"owner": owner_id}))

    def delete_request(self, request_id):
        self.db.requests.delete_one({"_id": ObjectId(request_id)})

    def remove_expired_records(self):
        current_time = time.time()
        self.db.requests.delete_many({'time': {'$lt': current_time-expire_time}})
        self.db.tables.delete_many({'expire_time': {'$lt': current_time}})

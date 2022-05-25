import csv
import os

import pymongo

# myclient = pymongo.MongoClient("mongodb://colin:colin_pass@localhost:27017/")
myclient = pymongo.MongoClient(
    host=os.getenv("_MONGO_INITDB_HOST"),
    port=os.getenv("_MONGO_INITDB_PORT"),
    username=os.getenv("_MONGO_INITDB_ROOT_USERNAME"),
    password=os.getenv("_MONGO_INITDB_ROOT_PASSWORD"),
)
mydb = myclient[os.getenv("_MONGO_INITDB_DATABASE")]
mycol = mydb[os.getenv("_MONGO_INITDB_COLLECTION")]

data = []

# open CSV file
with open("credentials.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    next(csv_reader)  # skip the first row (headers)
    for row in csv_reader:
        new_row = {
            "patient_id": row[0],
            "dreem_email": row[1],
            "dreem_password": row[2],
            "wildkeys_email": row[3],
            "wildkeys_password": row[4],
            "tfa_email": row[5],
            "tfa_password": row[6],
        }
        data.append(new_row)

# insert the data
mycol.insert_many(data)

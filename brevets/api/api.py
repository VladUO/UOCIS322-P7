# Streaming Service

import os
from os import O_RDONLY
from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api
import json
import pandas as pd

from itsdangerous import (TimedJSONWebSignatureSerializer \
                                  as Serializer, BadSignature, \
                                  SignatureExpired)

from passlib.apps import custom_app_context as pwd_context

from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

# importing our database 
client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.database
user = client.users

SECRET_KEY = 'SuperSecretSquirrel'


class register(Resource): #has to be a POST
    def post(self):
        # hash the password, insert usename and hashed pword into the database
        app.logger.debug("XXXX ENTERED USER REGISTRATION XXXX")

        username = request.args.get('username', default = "None", type=str)
        password = pwd_context.encrypt(request.args.get('password', default = "None", type=str))
        app.logger.debug("USERNAME IN API", username)
        app.logger.debug("PASSWORD IN API", (request.args.get('password', default = "None", type=str)))
        
        findUser = user.users.find_one({"Username": username})
        if (findUser):
            return {"message": "A user with that name already exists, please pick another user name."}, 400
        else:
            user.users.insert({"Username": username, "Password": password})
            return {"message": "Registration success!"}, 201
        

class token(Resource):
    def get(self):
        # hash the password, compare to database, seturn error if not in there, token otherwise
        app.logger.debug("XXXX ENTERED USER LOGIN XXXX")
        username = request.form.get('username', default = "None", type=str)
        app.logger.debug("USERNAME IN API", username)
        app.logger.debug("PASSWORD IN API", request.form.get('password', default = "None", type=str))

        password = pwd_context.encrypt(request.form.get('password', default = "None", type=str))
        findUser = user.users.find_one({"Username": username})
        if (not findUser):
            return {"message": "No user matching that user name found!"}, 401
        else:
            if (verify_password(password, findUser["Password"])):
                token = generate_auth_token(username)
                return {"message": "success", "token":str(token), "valid":600, "id": str(findUser["_id"])}, 200  
            else:
                return {"message": "Password does not match the one on record!"}, 401

def hash_password(password):
    return pwd_context.encrypt(password)


def verify_password(password, hashVal):
    return pwd_context.verify(password, hashVal)

def generate_auth_token(username, expiration=600):
    s = Serializer(SECRET_KEY, expires_in=expiration)
    return s.dumps({"username": username})


def verify_auth_token(token):
    s = Serializer(SECRET_KEY)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return "Expired token!"    # valid token, but expired
    except BadSignature:
        return "Invalid token!"    # invalid token
    return True

# class for listing all times
class listAll(Resource):
    def get(self, format="json"):
        app.logger.debug("ENTERED listAll in API")
        app.logger.debug(format)  # checking format

        if format == None:
            format = "json"

        # pulling out the k value and checking it
        k = request.args.get('top', default = 0, type=int)
        token = request.args.get('token')
        if verify_auth_token(token):
            app.logger.debug(k)

            # pulling out unnecessary items from the list and cleaning the list    
            data = list(db.database.find({}, {'_id': 0, 'BrevetDistance':0, 'StartTime':0, 'Location': 0, 'Km':0, 'Miles':0}))
            data.remove({})
            # app.logger.debug("DATA FROM MONGODB", data)
            
            # depending on the selected output format, sending the resulting list to the appropriate support function
            if format == "json":
                return toJson(k, data)
            elif format == "csv":    
                return toCSV(k, data)
            else:
                return "ERROR"
        else:
            return {"Message": "Invalid token"}, 401             

# class for listing open times only
class listOpenOnly(Resource):
    def get(self, format="json"):
        app.logger.debug("ENTERED listOpenOnly in API")  
        app.logger.debug(format) # checking format 
        
        # pulling out the k value and checking it
        k = request.args.get('top', default = 0, type=int)
        app.logger.debug(k)

        token = request.args.get('token')
        if verify_auth_token(token):
            # pulling out unnecessary items from the list and cleaning the list  
            data = list(db.database.find({}, {'_id': 0, 'BrevetDistance':0, 'StartTime':0, 'Location': 0, 'Km':0, 'Miles':0, 'Close':0}))
            data.remove({})
            # app.logger.debug("DATA FROM MONGODB", data)

            # depending on the selected output format, sending the resulting list to the appropriate support function
            if format == "json":
                return toJson(k, data)
            elif format == "csv":    
                return toCSV(k, data)
            else:
                return "ERROR" 
        else:
            return {"Message": "Invalid token"}, 401     


# class for listing close times only
class listCloseOnly(Resource):
    def get(self, format="json"):
        app.logger.debug("ENTERED listCloseOnly in API") 
        app.logger.debug(format) # checking format    

        # pulling out the k value and checking it
        k = request.args.get('top', default = 0, type=int)
        app.logger.debug(k)

        token = request.args.get('token')
        if verify_auth_token(token):
            # pulling out unnecessary items from the list and clearning the list  
            data = list(db.database.find({}, {'_id': 0, 'BrevetDistance':0, 'StartTime':0, 'Location': 0, 'Km':0, 'Miles':0, 'Open':0}))
            data.remove({})
            # app.logger.debug("DATA FROM MONGODB", data)

            # depending on the selected output format, sending the resulting list to the appropriate support function
            if format == "json":
                return toJson(k, data)
            elif format == "csv":    
                return toCSV(k, data)
            else:
                return "ERROR" 
        else:
            return {"Message": "Invalid token"}, 401        

# support function for converting to JSON format
def toJson(k, data):
    # create a new list
    newlist = []
    # if we have a k value and its less than the total number of rows
    # loop through data and append each row from data to the list
    # then jsonify the list and return it
    if k > 0 and k <= len(data):
        for i in range(0, k):
            newlist.append(dict(data[i]))
            app.logger.debug("LIST", newlist)
        return jsonify(newlist)
    
    # otherwise just jsonify the original list and return that
    else:
        return jsonify(data)

# support function for converting to CSV format
def toCSV(k, data):
    # create a new list
    newlist = [] 
    # if we have a k value and its less than the total number of rows
    # loop through data and append each row from data to the list
    # then turn that list into a dataframe, convert to CSV using to_csv and return
    if k > 0 and k <= len(data):
        for i in range(0, k):
            newlist.append(dict(data[i]))
            app.logger.debug("LIST", newlist)
        df = pd.DataFrame(newlist)
               
        return df.to_csv(index=False)

    # otherwise just convert the original list to dataframe, then to CSV and return
    else:
        df = pd.DataFrame(data)
        
        return df.to_csv(index=False)


# # Create routes
# # Another way, without decorators
api.add_resource(register, '/register', '/register/<string:format>')
api.add_resource(token, '/token', '/token/<string:format>', )
api.add_resource(listAll, '/listAll', '/listAll/<string:format>')
api.add_resource(listOpenOnly, '/listOpenOnly', '/listOpenOnly/<string:format>')
api.add_resource(listCloseOnly, '/listCloseOnly', '/listCloseOnly/<string:format>')

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

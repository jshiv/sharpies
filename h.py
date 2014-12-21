#!env/bin/python
# import os
# from flask import *

# app = Flask(__name__)

# @app.route('/')
# def h():
#     return 'Hey you guys!'
#     #return render_template('hello.html')

# if __name__ == "__main__":
#     app.run()


"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""

from flask import Flask, jsonify, abort, request, make_response, url_for
from flask.views import MethodView
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth
from werkzeug.contrib.fixers import ProxyFix

import pymongo
from bson.objectid import ObjectId

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
# from app import app


 
app = Flask(__name__, static_url_path = "")
api = Api(app)
auth = HTTPBasicAuth()



class mongoConn:

    def __init__(self, db = None, collection = None, url = None, **kwargs):

        self.initParam(kwargs)

        self.url = url
        if self.url is None:
            self.url = 'mongodb://localhost:27017/'
        self.db = db
        self.collection = collection
        self.mongoConn()

    def initParam(self, kwargs):
        '''initalize the given argument structure as properties of the class
        to be used by name in specific query execution'''
        self.argList = []
        for key, value in kwargs.items():
            self.argList.append(key)
            setattr(self,key,value)
    
    def mongoConn(self):
        '''mongoConn generates the set of properties required for connecting to a mongo database:
        client
        db
        collection 
        run a query like this: [x for x in self.collection.find()]'''
        self.client = pymongo.MongoClient(self.url)
        self.db = self.client[self.db]
        try:#look for the collection in the dictionary
            self.collection = self.db[self.collection]
            #print 'made mongo connection with dict specified collection name'
        except:
            pass
        if 'gridfs' in locals():
            self.fs = gridfs.GridFS(self.db)

            
db = mongoConn(db = 'heroku_app32685412', collection = 'places', url = 'mongodb://heroku_app32685412:m1rjg1bpghmlgl0gu1dqvpka4v@ds027761.mongolab.com:27761/heroku_app32685412')
# db = mongoConn(db = 'backend', collection = 'places')


 
@auth.get_password
def get_password(username):
    if username == 'duchess':
        return 'password'
    return None
 
@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'message': 'Unauthorized access' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog
    


places = [
    {
        'id': 1,
        'title': u'Your House',
        'description': u'Where we go to play!'
    },
    {
        'id': 2,
        'title': u'My House',
        'description': u'Where we go to stay!'
    }
]

#db.collection.insert(places)#seed database
 
place_fields = {
    'title': fields.String,
    'description': fields.String,
    'uri': fields.Url('place'),
    '_id':fields.String
}

class PlaceListAPI(Resource):
    # decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = str, required = True, help = 'No place title provided', location = 'json')
        self.reqparse.add_argument('description', type = str, default = "", location = 'json')
        super(PlaceListAPI, self).__init__()
        
    def get(self):
        places = [doc for doc in db.collection.find()]
        return { 'places': map(lambda t: marshal(t, place_fields), places) }

    def post(self):
        args = self.reqparse.parse_args()
        place = {
            'id': places[-1]['id'] + 1,
            'title': args['title'],
            'description': args['description'],
        }
        db.collection.insert(place)#insert the new place
        _id = str([doc['_id'] for doc in db.collection.find({'id': place['id']})][0])#collect mongos generated object id
        place.update({'_id':_id})#update the dict with mongos object id
        places.append(place)
        return { 'place': marshal(place, place_fields) }, 201

class PlaceAPI(Resource):
    # decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = str, location = 'json')
        self.reqparse.add_argument('description', type = str, location = 'json')
        self.reqparse.add_argument('done', type = bool, location = 'json')
        super(PlaceAPI, self).__init__()

    def get(self, _id):
        # place = filter(lambda t: t['_id'] == _id, places)
        place = [doc for doc in db.collection.find({u'_id': ObjectId(str(_id))})]
        if len(place) == 0:
            abort(404)
        return { 'place': marshal(place[0], place_fields) }
        
    def put(self, _id):
        #place = filter(lambda t: t['id'] == id, places)
        place = [doc for doc in db.collection.find({u'_id': ObjectId(str(_id))})]
        if len(place) == 0:
            abort(404)
        place = place[0]
        args = self.reqparse.parse_args()
        for k, v in args.iteritems():
            if v != None:
                place[k] = v
                db.collection.update({u'_id': ObjectId(str(_id))}, {"$set": {k:v} } ,upsert = True)
        return { 'place': marshal(place, place_fields) }

    def delete(self, _id):
        # place = filter(lambda t: t['id'] == id, places)
        place = [doc for doc in db.collection.find({u'_id': ObjectId(str(_id))})]
        if len(place) == 0:
            abort(404)
        #places.remove(place[0])
        db.collection.remove({u'_id': ObjectId(str(_id))})
        return { 'result': True }

api.add_resource(PlaceListAPI, '/things/api/v1.0/places', endpoint = 'places')
api.add_resource(PlaceAPI, '/things/api/v1.0/places/<_id>', endpoint = 'place')

app.wsgi_app = ProxyFix(app.wsgi_app)
    
if __name__ == '__main__':
    app.run(debug = True)
    # http_server = HTTPServer(WSGIContainer(app))
    # http_server.listen(5000)
    # IOLoop.instance().start()

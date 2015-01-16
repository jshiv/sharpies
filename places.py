#!env/bin/python

"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension.

Curl Commands:
curl -u duchess:password -i -H "Content-Type: application/json" -X POST -d '{"name":"My Butt","information":"its all sticky..."}' https://recipe-schematics.herokuapp.com/api/v1.0/places

httpie commands:
GET:
    http -a duchess:password https://sharpies.herokuapp.com/api/v1.0/places
    or
    curl -u duchess:password -i -H "Content-Type: application/json" -X GET https://sharpies.herokuapp.com/api/v1.0/places

GET NEAR mongo query only:
lng = -122.413294
lat = 37.786121
max_dist_meters = 100
placesNear = [doc for doc in db.collection.find({"loc" : {"$near": { "$geometry" : {"type":"Point","coordinates":[lng, lat]},"$maxDistance":max_dist_meters}}})]

POST:
    curl -u duchess:password -i -H "Content-Type: application/json" -X POST -d '{"name":"Mississippi","information":"can you spell that with out using an i"}' https://sharpies.herokuapp.com/api/v1.0/places

PUT:
    curl -u duchess:password -i -H "Content-Type: application/json" -X PUT -d '{"name":"BUTT BUTT","information":"  CHICKEN BUTT   "}' https://sharpies.herokuapp.com/api/v1.0/places/54962928c177ac0007eaeac8

DELETE:
    curl -u duchess:password -i -H "Content-Type: application/json" -X DELETE https://sharpies.herokuapp.com/api/v1.0/places/54962928c177ac0007eaeac8

aws ssh template:
ssh -i root/notes/.keys/see_spark_run.pem ubuntu@ec2-54-148-91-215.us-west-2.compute.amazonaws.com


                         _
_._ _..._ .-',     _.._(`))
'-. `     '  /-._.-'    ',/
   )         \            '.
  / _    _    |             \
|  a    a    /              |
\   .-.                     ;  
  '-('' ).-'       ,'       ;
     '-;           |      .'
        \           \    /
        | 7  .__  _.-\   \
        | |  |  ``/  /`  /
       /,_|  |   /,_/   /
          /,_/      '`-'
          
"""

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

            
# db = mongoConn(db = 'heroku_app32685412', collection = 'places', url = 'mongodb://heroku_app32685412:m1rjg1bpghmlgl0gu1dqvpka4v@ds027761.mongolab.com:27761/heroku_app32685412')
db = mongoConn(db = 'backend', collection = 'places')


 
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
        'name': u'Your House',
        'information': u'Where we go to play!'
    },
    {
        'id': 2,
        'name': u'My House',
        'information': u'Where we go to stay!'
    }
]

#db.collection.insert(places)#seed database
 
place_fields = {
    'name': fields.String,
    'information': fields.String,
    'type':fields.String,
    'address':fields.String,
    'phone':fields.String,
    'long':fields.String,
    'lat':fields.String,
    'cover':fields.Integer,
    'line':fields.String,
    'pop':fields.Integer,
    'image':fields.String,


    'uri': fields.Url('place'),
    '_id':fields.String
}

class PlaceListAPI(Resource):
    # decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type = str, required = True, help = 'No place name provided', location = 'json')
        self.reqparse.add_argument('information', type = str, default = "", location = 'json')
        self.reqparse.add_argument('type', type = str, default = "", location = 'json')
        self.reqparse.add_argument('address', type = str, default = "", location = 'json')
        self.reqparse.add_argument('phone', type = str, default = "", location = 'json')
        self.reqparse.add_argument('long', type = str, default = "", location = 'json')
        self.reqparse.add_argument('lat', type = str, default = "", location = 'json')
        self.reqparse.add_argument('cover', type = int, default = 0, location = 'json')
        self.reqparse.add_argument('line', type = str, default = "", location = 'json')
        self.reqparse.add_argument('pop', type = int, default = 0, location = 'json')
        self.reqparse.add_argument('image', type = str, default = "", location = 'json')
        super(PlaceListAPI, self).__init__()
        
    def get(self):
        places = [doc for doc in db.collection.find()]
        return { 'places': map(lambda t: marshal(t, place_fields), places) }

    def post(self):
        args = self.reqparse.parse_args()
        place = args
        # construct the location parameter for geoJson mongodb stuff
        try:
            if (place['long'] != '') and (place['lat'] != ''):
                place.update({'loc': { "type": "Point", "coordinates": [ float(place['long']), float(place['lat']) ] }})
        except:
            pass
        # place = {
        #     'id': places[-1]['id'] + 1,
        #     'name': args['name'],
        #     'information': args['information'],
        #     'type': args['type'],
        #     'address': args['address']
        # }

        _id = db.collection.insert(place)#insert the new place
        locDict = place.pop('loc',None)#remove the loc parameter from the json document but keep it in mongo
        # _id = str([doc['_id'] for doc in db.collection.find({'id': place['id']})][0])#collect mongos generated object id
        place.update({'_id':str(_id)})#update the dict with mongos object id
        #places.append(place)
        return { 'place': marshal(place, place_fields) }, 201



class PlacesNearAPI(Resource):
    # decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type = str, location = 'json')
        self.reqparse.add_argument('information', type = str, default = "", location = 'json')
        self.reqparse.add_argument('type', type = str, default = "", location = 'json')
        self.reqparse.add_argument('address', type = str, default = "", location = 'json')
        self.reqparse.add_argument('phone', type = str, default = "", location = 'json')
        self.reqparse.add_argument('long', type = str, default = "", location = 'json')
        self.reqparse.add_argument('lat', type = str, default = "", location = 'json')
        self.reqparse.add_argument('cover', type = int, default = 0, location = 'json')
        self.reqparse.add_argument('line', type = str, default = "", location = 'json')
        self.reqparse.add_argument('pop', type = int, default = 0, location = 'json')
        self.reqparse.add_argument('image', type = str, default = "", location = 'json')
        super(PlacesNearAPI, self).__init__()

    def get(self,lng,lat,radius):
        # place = filter(lambda t: t['_id'] == _id, places)
        #lng = -122.413294
        #lat = 37.786121
        # max_dist_meters = 100
        nearest_places = [doc for doc in db.collection.find({"loc" : {"$near": { "$geometry" : {"type":"Point","coordinates":[float(lng), float(lat)]},"$maxDistance":float(radius)}}})]

        # places_near = [{"cover": 20,
        # "name": "Bartinis",
        # "address": "43 Central Ave",
        # "phone": "978-319-1460",
        # "pop": 5,
        # "line": "5-10",
        # "type": "Dive/Sports Bar",
        # "image": "BartinisBarImage",
        # "information": "$1 Jello Shots all night!!!",
        # "long" : "-122.424324", 
        # "lat":"37.788359" 
        #  }]
        #place = [doc for doc in db.collection.find({u'_id': ObjectId(str(_id))})]
        if len(nearest_places) == 0:
            abort(404)
        return { 'nearest_places': map(lambda t: marshal(t, place_fields), nearest_places) }

class PlaceAPI(Resource):
    # decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type = str, location = 'json')
        self.reqparse.add_argument('information', type = str, location = 'json')
        self.reqparse.add_argument('type', type = str, default = "", location = 'json')
        self.reqparse.add_argument('address', type = str, default = "", location = 'json')
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

api.add_resource(PlaceListAPI, '/api/v1.0/places', endpoint = 'places')
api.add_resource(PlaceAPI, '/api/v1.0/places/<_id>', endpoint = 'place')
api.add_resource(PlacesNearAPI, '/api/v1.0/nearest_places/<lng>,<lat>,<radius>', endpoint = 'nearest_places')

app.wsgi_app = ProxyFix(app.wsgi_app)
    
if __name__ == '__main__':
    #app.run(debug = True)
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(8080)
    IOLoop.instance().start()

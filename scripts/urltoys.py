import urllib2
import json

local = True

def make_url(url_ext = 'places'):
    if local:
        host = 'http://localhost:8080/'
    else:
        host = 'https://sharpies.herokuapp.com/'

    return host + 'api/v1.0/' + url_ext


def put_dict(url, payload):
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url, data=json.dumps(payload))
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: 'PUT'
    url = opener.open(request)

def delete(url):
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url)
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: 'DELETE'
    url = opener.open(request)

    
def post_dict(url, payload):
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps(payload))
    
def get_dict(url):
    response = urllib2.urlopen(url)
    return json.load(response) 


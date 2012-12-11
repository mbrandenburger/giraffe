__author__ = 'marcus'

import json
import logging
import threading
from functools import wraps
from flask import Flask, Response, request
from giraffe.common.config import Config

logger = logging.getLogger("service.collector")
config = Config("giraffe.cfg")
app = Flask(__name__)

class Rest_API(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        app.run(config.get("flask", "host"), config.getint("flask", "port"))
#        app.run(host='134.169.176.116', port=1337)

    def stop(self):
        self._Thread__stop()

# (Marcus) TODO:

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == config.get("flask", "user") and password == config.get("flask", "pass")

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def show_welcome():
    return json.dumps({ 'Message' : 'Welcome to Giraffe REST API' })

@app.route('/hosts/')
@requires_auth
def show_all_hosts():
    return json.dumps({ 'Message' : 'Liste aller hosts' })

@app.route('/hosts/<host_id>/')
@requires_auth
def show_host(host_id):
    return json.dumps({ 'User' : host_id })

@app.route('/hosts/<host_id>/meters/<meter_id>/start_time/<start_time>')
@requires_auth
def show_host_meter(host_id, meter_id=None, start_time=None):
    message = {}
    message['host']       = host_id
    message['meter']      = meter_id
    message['start_time'] = start_time

    return json.dumps(message)

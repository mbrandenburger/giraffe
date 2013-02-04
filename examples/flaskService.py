import logging

__author__ = 'marcus'

from flask import Flask
import flask

_logger = logging.getLogger("service.flask")

app = Flask(__name__)

if __name__ == '__main__':
    app.run()


@app.route("/")
def hello():

#    rq = flask.request
#    print rq.headers['X-Auth-Token']

    return "Hello World!"

@app.route("/hello")
def mofo():

#    rq = flask.request
#    print rq.headers['X-Auth-Token']

    return "Hello MOFOs!"

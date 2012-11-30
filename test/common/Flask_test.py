__author__ = 'marcus'

from flask import Flask
app = Flask(__name__)

@app.route('/hosts/')
def show_all_hosts():
    return 'Liste aller hosts'

@app.route('/hosts/<host_id>/')
def show_host(host_id):
    # show the user profile for that user


    return 'User %s' % host_id

@app.route('/hosts/<host_id>/meters/<meter_id>/start_time/<start_time>')
def show_host(host_id, meter_id, start_time):
    # show the user profile for that user
    return 'host: %s, meters: %s, starttime: %s' % (host_id, meter_id, start_time)

if __name__ == '__main__':
    app.run()

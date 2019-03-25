"""ECAAF endpoint simulator"""
from flask import flash, Flask, jsonify, abort, request, redirect, make_response, url_for, render_template
from flask.ext.httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename

import os
import uuid
import time
import sys


__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"

app = Flask(__name__, static_url_path = "")
auth = HTTPBasicAuth()
sim_port = 0
sim_asn = 0


@auth.get_password
def get_password(username):
    if username == 'admin':
        return 'admin'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/api/testsim/v1/testconfig', methods = ['POST'])
@auth.login_required
def ecaaf_test_config(target_pool, target_project):
    return jsonify({"return code": "sucess"}})


if __name__ == '__main__':
    app.secret_key='ecaafsim'
    total = len(sys.argv)
    if total == 3:
	sim_name=sys.argv[1]
        sim_port=int(sys.argv[2])
    if total == 3:
	print "STARTING SIMULTOR-->"+sim_name
        app.run(host='localhost',port=sim_port,debug = True)
    else:
        print "Too few arguments to start the simulator"

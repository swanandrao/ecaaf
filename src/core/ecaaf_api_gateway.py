from flask import flash, Flask, jsonify, abort, request, redirect, make_response, url_for, render_template
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os
import uuid
import zipfile
import shutil

from dmisc import ecaaf_auth, ecaaf_config, ecaaf_db, ecaaf_logger, ecaaf_utils
from dmisc import ecaaf_context_dispatch

__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"

app = Flask(__name__, static_url_path = "", template_folder='../bui')
auth = HTTPBasicAuth()
logger = ecaaf_logger.get_logger('ecaaf_api_gateway')

__events = [
    {
        'event_id': str(uuid.uuid4()),
        'event_name': 'DUMMY',
        'event_domain': 'DUMMY',
        'event_platform': 'DUMMY',
        'event_action':'DUMMY',
        'event_source' : 'DUMMY'
    },
]

@auth.get_password
def get_password(username):
    return ecaaf_auth.get_password()

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'status': 'Unauthorized access' } ), 403)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'status': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'status': 'Not found' } ), 404)

@app.errorhandler(409)
def not_found(error):
    return make_response(jsonify( { 'status': 'already present' } ), 409)

@app.route('/ecaaf/api/v1.0/funclettree', methods = ['GET'])
@auth.login_required
def get_funclet_tree():
    return jsonify(ecaaf_utils.get_funclet_tree())

@app.route('/', methods = ['GET'])
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/uploadfile', methods = ['POST'])
def uploadfile():
    _user=request.form['username']
    _password=request.form['pass']
    logger.info('User %s logged in'%_user)
    if _user != ecaaf_auth.get_username() or _password != ecaaf_auth.get_password():
        return render_template('userautherror.html')
    else:
        return render_template('fileupload.html')

@app.route('/uploaddone', methods=['POST'])
def upload_file_done():
    return render_template('fileupload.html')

@app.route('/uploads', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logger.error('File not found in request..')
        return render_template('fileuploaderror.html')
    file = request.files['file']
    if file.filename == '':
        return render_template('fileuploaderror.html')
    elif file and ecaaf_utils.allowed_file(file.filename):
        filename = secure_filename(file.filename)
        bindreq=ecaaf_utils.create_bind_req(request.form)
        bindreq['fname']=filename
        file.save(os.path.join(ecaaf_utils.get_upload_path(bindreq, True, \
            False), filename))
        logger.info('File %s has been uploaded'%filename)
        logger.info("Dispatching bindreq: %s"%str(bindreq))
        ecaaf_context_dispatch.dispatch_bind_req(bindreq)
        return render_template('fileuploaddone.html')
    return render_template('fileuploaderror.html')

@app.route('/ecaaf/api/v1.0/deploy-app', methods=['POST'])
def deploy_app():
    file = None
    bindreq={}
    resp={}
    analyze = False
    try:
        if 'file' in request.files:
            file = request.files['file']
        if file and file.filename != '' and ecaaf_utils.allowed_file(file.filename):
            filename = secure_filename(file.filename)
        appname=request.form['aname']
        fpath=ecaaf_config.get_app_path()+'/'+appname
        ret=ecaaf_utils.deploy_app(file, os.path.join(fpath,filename))
        if ret==True:
            return jsonify({'status': 'deploy-app suceeded'})
        else:
            return jsonify({'status': 'deploy-app failed'})
    except:
        logger.error("Deploy app for app: %s failed"%bindreq['aname'],exc_info=True)
        return jsonify({'status': 'deploy-app failed'})

@app.route('/ecaaf/api/v1.0/action-event', methods=['POST'])
def action_event():
    file = None
    bindreq={}
    try:
        if 'file' in request.files:
            file = request.files['file']
        if file and file.filename != '' and ecaaf_utils.allowed_file(file.filename):
            filename = secure_filename(file.filename)
        #if ecaaf_db.kvdb_get(request.form['ename']):
        #    abort(409)
        ecaaf_db.kvdb_set(request.form['ename'], "")
        bindreq=ecaaf_utils.create_bind_req(request.form)
        bindreq['type']=request.form['type']
        if file:
            bindreq['fname']=filename
            fpath=os.path.join(ecaaf_utils.get_upload_path(bindreq,\
                False, False),filename)
        else:
            fpath=ecaaf_utils.get_upload_path(bindreq,False,False)
        if os.path.exists(fpath):
            abort(409)
        if file:
            file.save(os.path.join(ecaaf_utils.get_upload_path(bindreq,True,\
                False), filename))
            logger.info('File %s has been uploaded'%filename)
        else:
            fpath=ecaaf_utils.get_upload_path(bindreq,True,False)
        logger.info("Dispatching bindreq for event: %s"%bindreq['ename'])
        ecaaf_context_dispatch.dispatch_bind_req(bindreq)
        return jsonify({'status': 'action-event bind deployment suceeded'})
    except:
        return jsonify({'status': 'action-event bind deployment failed'})

@app.route('/ecaaf/api/v1.0/create-action', methods=['POST'])
def create_action():
    bindreq={}
    if 'file' not in request.files:
        logger.error('File not found in request..')
        abort(400)
    file = request.files['file']
    logger.info("Swanand:File %s"%file)
    if file.filename == '':
        abort(400)
    elif file and ecaaf_utils.allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            bindreq=ecaaf_utils.create_bind_req(request.form)
            bindreq['type']=request.form['type']
            bindreq['fname']=filename
            fpath=ecaaf_utils.get_action_path(bindreq)
            logger.info("swanand fpath %s" %fpath)
            if os.path.exists(fpath):
                abort(409)
            os.makedirs(fpath)
            zpath=os.path.join(fpath,filename)
            file.save(zpath)
            z = zipfile.ZipFile(zpath)
            z.extractall(fpath)
            os.remove(zpath)
        except:
            if os.path.exists(fpath):
                shutil.rmtree(fpath)
            logger.error("Creation of action %s failed" % bindreq['action'],exc_info=True)
            return jsonify({'status':'create-action failed'})
    return jsonify( { 'status': 'event-bind deployment suceeded' } )

@app.route('/ecaaf/api/v1.0/funclet-event', methods=['POST'])
def funclet_event():
    file = None
    bindreq={}
    if 'file' not in request.files:
        logger.error('File not found in request..')
        abort(400)
    file = request.files['file']
    if file and file.filename != '' and ecaaf_utils.allowed_file(file.filename):
        filename = secure_filename(file.filename)
    if ecaaf_db.kvdb_get(request.form['ename']):
        abort(409)
    ecaaf_db.kvdb_set(request.form['ename'], "")
    bindreq=ecaaf_utils.create_bind_req(request.form)
    bindreq['type']=request.form['type']
    if file:
        bindreq['fname']=filename
        fpath=os.path.join(ecaaf_utils.get_upload_path(bindreq,\
            False, False),filename)
    else:
        fpath=ecaaf_utils.get_upload_path(bindreq,False,False)
    if os.path.exists(fpath):
        abort(409)
    if file:
        file.save(os.path.join(ecaaf_utils.get_upload_path(bindreq,True,\
            False), filename))
        logger.info('File %s has been uploaded'%filename)
    else:
        fpath=ecaaf_utils.get_upload_path(bindreq,True,False)
    logger.info("Dispatching bindreq for event: %s"%bindreq['ename'])
    ecaaf_context_dispatch.dispatch_bind_req(bindreq)
    return jsonify({ 'status': 'event-bind deployment suceeded' })

@app.route('/ecaaf/api/v1.0/ephemeron', methods=['POST'])
def bind_event():
    file = None
    bindreq={}
    if 'file' in request.files:
        file = request.files['file']
    if file and file.filename != '' and ecaaf_utils.allowed_file(file.filename):
        filename = secure_filename(file.filename)

        if ecaaf_db.kvdb_get(request.form['ename']):
            abort(409)
        ecaaf_db.kvdb_set(request.form['ename'], "")
        bindreq=ecaaf_utils.create_bind_req(request.form)
        bindreq['type']=request.form['type']
    if file:
        bindreq['fname']=filename
        fpath=os.path.join(ecaaf_utils.get_upload_path(bindreq,\
            False, False),filename)
    else:
        fpath=ecaaf_utils.get_upload_path(bindreq,False,False)
    if os.path.exists(fpath):
        abort(409)
    if file:
        file.save(os.path.join(ecaaf_utils.get_upload_path(bindreq,True,\
            False), filename))
        logger.info('File %s has been uploaded'%filename)
    else:
        fpath=ecaaf_utils.get_upload_path(bindreq,True,False)
    logger.info("Dispatching bindreq for event: %s"%bindreq['ename'])
    ecaaf_context_dispatch.dispatch_bind_req(bindreq)
    return jsonify( { 'status': 'event-bind deployment suceeded' } )

@app.route('/ecaaf/api/v1.0/events', methods = ['GET'])
@auth.login_required
def get_events():
    return jsonify( { 'events': map(make_public_event, events) } )

@app.route('/ecaaf/api/v1.0/events/<event_id>', methods = ['GET'])
@auth.login_required
def get_event(event_id):
    event = ecaaf_db.kvdb_get(event_id)
    if not event:
        abort(404)
    return jsonify( { 'event': json.dumps(event)} )

@app.route('/ecaaf/api/v1.0/events', methods = ['POST'])
@auth.login_required
def create_event():
    if not request.json or not 'event_name' in request.json:
        abort(400)
    event = {
        'event_id': str(uuid.uuid4()),
        'type': 'event',
        'event_name': str(request.json['event_name'])
    }
    try:
        event['params']=request.json['params']
    except:
        logger.error("Could not find params in event map..",exc_info=True)
    logger.info("Dispatching event: %s"%event['event_id'])
    #elastic store the event - state created.
    ecaaf_context_dispatch.dispatch_event_req(event)
    return jsonify({'event_id':event['event_id']}), 201

@app.route('/ecaaf/api/v1.0/events/<event_id>', methods = ['DELETE'])
@auth.login_required
def delete_event(event_id):
    if not ecaaf_db.kvdb_get(event_id):
        abort(404)
    ecaaf_db.kvdb_delete(event_id)
    return jsonify( { 'result': True } )

if __name__ == '__main__':
    h,p,s=ecaaf_config.get_api_gateway_config()
    app.secret_key=s
    app.run(host=h,port=p,debug = True)

"""Important utility functions used by the core services"""

import docker
import ConfigParser
import fileinput
import json
import os
import shutil
import zipfile
import time

import ecaaf_db
import ecaaf_container
import ecaaf_logger
import ecaaf_config

__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"

__allowed_extensions=ecaaf_config.get_upload_extensions()
__install_dir=ecaaf_config.get_path_config('install_dir')
__event_upload_folder=ecaaf_config.get_path_config('event_upload_folder')
__boilerplate_path=__install_dir+ecaaf_config.get_path_config('boilerplate_path')
__domain_folder=__install_dir+ecaaf_config.get_path_config('domain_folder')
__image_config_file=ecaaf_config.get_path_config('image_config_file')
__action_config=ecaaf_config.get_path_config('action_config')
__host_vol_dir=ecaaf_config.get_path_config('host_vol_dir')
__bindkeys=['ename','porg','pdomain','platform','action','action_version',\
            'runtime','runtime_version',\
            'target_url','target_port','target_api_version',\
            'target_username','target_password']
__composekeys=['appname','event_source','functionlist' ]
__logger = ecaaf_logger.get_logger('ecaaf_utils')

#convert the config file to a dictionary
class ConfigLoads(ConfigParser.ConfigParser):
    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d

def load_config(fname):
    try:
        f = ConfigLoads()
        f.read(fname)
        ret = f.as_dict()
    except:
        __logger.error("Could not load config...")
    return ret

#perform inplace search and replace
def snr(filename, sstr, rstr):
    file = fileinput.input(filename, inplace=1)
    for line in file:
        line = line.replace(sstr, rstr)
        #This print is required DONOT remove!
        print line,
    file.close()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in __allowed_extensions

def recurse_map(map,list,index):
    if index==len(list):
        return {}
    if list[index] not in map:
        map[list[index]]={}
    map[list[index]]=recurse_map(map[list[index]],list,index+1)
    return map

def prune_funclet_tree(map, __pruned_map, reclist, level, max_depth):
    if level == max_depth:
        return recurse_map(__pruned_map,reclist,0)
    if not map:
        return {}
    for k in map:
        reclist.append(k)
        prune_funclet_tree(map[k],__pruned_map, reclist, level+1,max_depth)
        reclist.remove(k)
    return __pruned_map

def get_funclet_tree():
    dir = {}
    __pruned_map={}
    rootdir=__domain_folder
    rootdir = rootdir.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys(files)
        parent = reduce(dict.get, folders[:-1], dir)
        parent[folders[-1]] = subdir
    #prune out all routes that do not comply to
    #domain/platform/action funclet/runtime/runtime-version
    dir=prune_funclet_tree(dir,__pruned_map,[],0,8)
    return dir

def get_upload_path(bindreq, create, includezip):
    try:
        po=bindreq['porg']
        pd=bindreq['pdomain']
        pl=bindreq['platform']
        ac=bindreq['action']
        av=bindreq['action_version']
        ru=bindreq['runtime']
        rv=bindreq['runtime_version']
        en=bindreq['ename']
        path = __event_upload_folder+'/'+en+'.'+po+'.'+pd+'.'+pl+'.'+ac+'.'\
            +av+'.'+ru+'.'+rv+'/'
        if includezip == True:
            path+='/'
            path+=bindreq["fname"].rsplit('.',1)[0]
        if create == True:
            os.makedirs(path)
    except:
        __logger.error('Failed to create directories in upload path %s'%path)
    return path

def get_action_path(bindreq,create=False):
    path=''
    try:
        po=bindreq['porg']
        pd=bindreq['pdomain']
        pl=bindreq['platform']
        ac=bindreq['action']
        av=bindreq['action_version']
        ru=bindreq['runtime']
        rv=bindreq['runtime_version']
        path = __domain_folder+'/'+po+'/'+pd+'/'+pl+'/'+ac+'/'+av+'/'+ru+'/'+rv
        if create == True:
            os.makedirs(path)
    except:
        __logger.error("Could not construct path to action %s"%ac)
    return path

def get_image_tag(bindreq):
    tag=''
    try:
        po=bindreq['porg']
        pd=bindreq['pdomain']
        pl=bindreq['platform']
        ac=bindreq['action']
        av=bindreq['action_version']
        ru=bindreq['runtime']
        en=bindreq['ename']
        tag = po+'/'+pd+'/'+pl+'/'+ac+'/'+av+'/'+ru+'/'+en

    except:
        __logger.error("Could not create image tag {0} for bindreq {1}"\
        .format(tag, bindreq['id']), exc_info=True)
    return tag

def copy_files(src, dest, excludelist=''):
    src_files = os.listdir(src)
    if not src_files:
        return False
    for file_name in src_files:
        try:
            if file_name not in excludelist:
                full_file_name = os.path.join(src, file_name)
                if (os.path.isfile(full_file_name)):
                    shutil.copy(full_file_name, dest)
        except:
            __logger.error("Could not copy files from {0} to {1}".format(src,dest))
            return False

def create_bind_req(form):
        bindreq={}

        __logger.info("Received form for %s"% form['ename'])
        for k in __bindkeys:
            if k in form:
                bindreq[k] = form[k]
            else:
                __logger.info("bind key %s not found in form..."%k)
        bindreq['id']=bindreq['porg']+'/'+bindreq['pdomain']+'/'+bindreq['platform']+'/'+\
                    bindreq['action']+'/'+bindreq['action_version']+'/'+\
                    bindreq['runtime']+'/'+bindreq['runtime_version']
        return bindreq

def create_compose_req(form):
        bindreq={}
        funclist=[]
        __logger.info("Received form for %s"% form['appname'])
        for k in __composekeys:
            if k in form:
                if k =='functionlist':
                    temp=json.loads(form[k])
                    for func in temp:
                        funclist.append(create_bind_req(func))
                    bindreq[k]=funclist
                else:
                    bindreq[k] = form[k]
        return bindreq

def disable_components(tdir,pre,action,post,generic):
    if pre:
        snr(tdir+'/master.py','import ecaaf_action_pre',\
            '#import ecaaf_action_pre')
        snr(tdir+'/master.py','ecaaf_action_pre','#ecaaf_action_pre')
        __logger.info("pre-action funclet not defined...")
    if action:
        snr(tdir+'/master.py','import ecaaf_action_handler',\
            '#import ecaaf_action_handler')
        snr(tdir+'/master.py','ecaaf_action_handler','#ecaaf_action_handler')
        __logger.info("action funclet not defined...")
    if post:
        snr(tdir+'/master.py','import ecaaf_action_post',\
            '#import ecaaf_action_post')
        snr(tdir+'/master.py','ecaaf_action_post','#ecaaf_action_post')
        __logger.info("post-action funclet not defined...")
    if generic:
        snr(tdir+'/master.py','import ecaaf_generic_handler','#import \
        ecaaf_generic_handler')
        snr(tdir+'/master.py','ecaaf_generic_handler','#ecaaf_generic_handler')
        __logger.info("generic funclet not defined...")

def prep_py_master(tdir, config, action):
    ret=True
    #pre,post, action or generic handlers are optional
    #if none of the four are present then it is just a marker
    #lambda function.
    try:
        if config:
            if 'ecaaf' in config:
                if 'ecaaf_action_pre' in config['ecaaf']:
                    prefile=config['ecaaf']['ecaaf_action_pre']
                    snr(tdir+'/master.py', 'ecaaf_action_pre', prefile)
                else:
                    disable_components(tdir,True,False,False,False)
            if 'ecaaf' in config:
                if 'ecaaf_action_post' in config['ecaaf']:
                    postfile=config['ecaaf']['ecaaf_action_post']
                    snr(tdir+'/master.py', 'ecaaf_action_post', postfile)
                else:
                    disable_components(tdir,False,False,True,False)
            if 'ecaaf' in config:
                if 'ecaaf_generic_handler' in config['ecaaf'] and \
                    ('ecaaf' not in action or \
                    'ecaaf_action_pre' not in config['ecaaf'] or \
                    'ecaaf_action_post' not in config['ecaaf']):
                    generichandler=config['ecaaf']['ecaaf_generic_handler']
                    snr(tdir+'/master.py', 'ecaaf_generic_handler', generichandler)
                else:
                    disable_components(tdir,False,False,False,True)
        else:
            disable_components(tdir,True,False,True,True)
        if 'ecaaf' in action:
            if 'ecaaf_action_handler' in action['ecaaf']:
                actionhandler=action['ecaaf']['ecaaf_action_handler']
                snr(tdir+'/master.py', 'ecaaf_action_handler', actionhandler)
            else:
                disable_components(tdir,False,True,False,False)
    except:
        __logger.error("Could not prep master file....", exc_info=True)
        ret =False
    return ret

#add the prep master function for different runtimes to this dict
__prep_master={
        'python':prep_py_master
}

def get_boilerplate_action(tdir,actionpath='',runtime='', runtime_version=''):
    copy_files(__boilerplate_path, tdir)
    copy_files(__boilerplate_path+'/runtime/'+runtime, tdir)
    copy_files(__boilerplate_path+'/runtime/'+runtime+'/'+\
        runtime_version, tdir)
    if actionpath != '':
        copy_files(actionpath, tdir)
        
def build_image(bindreq,deltag=True):
    tag=''
    d=None
    a=None
    tdir=''
    #need to add validation like image created etc.
    try:
        if 'fname' in bindreq:
            zfile=get_upload_path(bindreq,False,False)+'/'+bindreq['fname']
            z = zipfile.ZipFile(str(zfile))
            z.extractall(str(get_upload_path(bindreq,False,False)))
        tdir = get_upload_path(bindreq,False,False)
        actionpath=get_action_path(bindreq)
        get_boilerplate_action(tdir, actionpath, bindreq['runtime'], \
            bindreq['runtime_version'])
        if 'fname' in bindreq:
            d=load_config(tdir+'/'+__image_config_file)
        a=load_config(tdir+'/'+__action_config)
        __prep_master[bindreq['runtime']](tdir, d, a)
        tag=get_image_tag(bindreq)
        img = ecaaf_container.dbuild(tdir,tag)
        if img:
            bindreq["itag"]=tag
            ecaaf_db.kvdb_set(bindreq["ename"], bindreq)
            __logger.info("Image with id %s created..." % str(img.id))
        else:
            __logger.error("Image with tag %s failed creation..." % str(tag))
        __logger.info('removing the scratch directory %s' % tdir)
        #if(deltag):
            #shutil.rmtree(tdir)
    except:
        if os.path.exists(tdir):
            shutil.rmtree(tdir)
        __logger.error('Could not build image for bindreq: %s'%bindreq['id'],\
        exc_info=True)
    return tag

def build_image_optimized(bindreq):
    tag=''
    d=None
    a=None
    modules=[]
    mstr=''
    tdir=__event_upload_folder+'/'+bindreq['otag']
    #need to add validation like image created etc.
    try:
        if os.path.exists(tdir):
            shutil.rmtree(tdir)
        os.makedirs(tdir)
        for f in bindreq['functionlist']:
            copy_files(f['fpath'], tdir,[''])
            actionpath=get_action_path(f)
            a=load_config(f['fpath']+'/'+__action_config)
            if 'ecaaf' in a:
                if 'ecaaf_action_handler' in a['ecaaf']:
                    modules.append(a['ecaaf']['ecaaf_action_handler'])

        #TODO:For now supporting python 2.7 but need to change it to be more
        #generic.
        get_boilerplate_action(tdir, '', 'python','2.7')
        os.rename(tdir+'/masteragg.py',tdir+'/master.py')
        for m in modules:
            if mstr == '':
                mstr=mstr+m
            else:
                mstr=mstr+','+m
        snr(tdir+'/master.py', 'ecaaf_modules', mstr)
        tag=bindreq['appname']+'/'+bindreq['otag']
        img = ecaaf_container.dbuild(tdir,tag)
        img=tag
        if img:
            bindreq["itag"]=tag
            ecaaf_db.kvdb_set(tag, bindreq)
            #__logger.info("Image with id %s created..." % str(img.id))
            __logger.info("Image with id %s created..." %tag)
        else:
            __logger.error("Image with tag %s failed creation..." % str(tag))
        __logger.info('removing the scratch directory %s' % tdir)
        #shutil.rmtree(tdir)
    except:
        if os.path.exists(tdir):
            shutil.rmtree(tdir)
        __logger.error('Could not build image for bindreq: %s'%bindreq['id'],\
        exc_info=True)
    return tag

def run_image(cargs):
    tag=''
    #Need to add validation like image exist etc..
    try:
        __logger.info(cargs)
        v={__host_vol_dir:{'bind':'/host','mode':'rw'}}
        cargs=json.loads(cargs)
        bindargs=ecaaf_db.kvdb_get(cargs['event_name'])
        if 'itag' in bindargs:
            tag=bindargs["itag"]
            cargs["binding"]=bindargs
            enc=json.dumps(cargs)
            denc=json.dumps(enc)
            e = "event="+denc
            c = ecaaf_container.drun(tag,e,v)
            if c:
                __logger.info('Event:%s executed in container %s...' % (str(tag),str(c.id)))
                __logger.info('Event string %s...' %e)
            else:
                __logger.error('Event:%s failed to execute...' % str(tag), exc_info=True)
        else:
            __logger.error("Could not find itag for event %"%cargs['event_name'])
    except:
        __logger.error("Could not execute event {0} failed to launch \
        the image{1}".format(cargs['event_name'],tag), exc_info=True)
    return tag

#TODO:Fill in the app deployment and composition logic here
#the yaml file is stored under ecaaf/ecaaf.catalog/<app-name>
def deploy_app(file,filepath):
    ret=True
    try:
        file.save(filepath)
        __logger.info('File %s has been uploaded'%filepath)
    except:
        ret=False
        __logger.error('File %s has been uploaded'%filepath, exc_info=True)
    return ret

#TODO:Fill in the app execution logic here
def exec_app(payload):
    __logger.info('App %s executed'%payload['app_name'])
    return

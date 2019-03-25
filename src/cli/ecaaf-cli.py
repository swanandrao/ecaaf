""" The command line interpreter for deploying events and creating new action
funclets for ecaaf"""

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import style_from_dict
from pygments.token import Token
import json

import click
import os
import traceback
import sys
import requests
from requests.auth import HTTPBasicAuth
from werkzeug.utils import secure_filename

__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"

##TODO:Change this to something meaningful when using outside of test or demo.
#__ecaaf_api_gateway="http://localhost:5000/"
__ecaaf_api_gateway="http://100.104.6.11:5000/"
__f={}
__eventbindkeys={'name':'ename',
    'source asn':'asn',
    'organization':'porg',
    'domain':'pdomain',
    'platform':'platform',
    'action funclet':'action',
    'action funclet version':'action_version',
    'runtime':'runtime',
    'runtime version':'runtime_version',
    'upload file path':'fpath',
    'upload file name':'fname',
    'target url':'target_url',
    'target port':'target_port',
    'target api version':'target_api_version',
    'target username':'target_username',
    'target password':'target_password'
}
__eventbindkeyslist=['name','source asn','organization','domain','platform','action funclet','action funclet version','runtime','runtime version',\
                'upload file path','upload file name','target url','target port',\
                'target api version','target username','target password']
__funceventbindkeys={'name':'eename',
    'runtime':'runtime',
    'runtime version':'runtime_version',
    'upload file path':'fpath',
    'upload file name':'fname',
}
__funceventbindkeyslist=['name','runtime','runtime version','upload file path',\
    'upload file name']
__actionbindkeys={'organization':'porg',
    'domain':'pdomain',
    'platform':'platform',
    'action name':'ename',
    'action version':'action_version',
    'runtime':'runtime',
    'runtime version':'runtime_version',
    'upload file path':'fpath',
    'upload file name':'fname'
}
__actionbindkeyslist=['action name','action version','organization','domain','platform','runtime',\
                'runtime version','upload file path','upload file name']
__ephemeronbindkeys={
    'ephemeron name':'ename',
    'runtime':'runtime',
    'runtime version':'runtime_version',
    'upload file path':'fpath',
    'upload file name':'fname'
}
__ephemeronbindkeyslist=['ephemeron name','runtime','runtime version',\
    'upload file path','upload file name']
__deployapptbindkeys={
    'app name':'aname',
    'upload file path':'fpath',
    'upload file name':'fname'
}
__deployappbindkeyslist=['app name','upload file path','upload file name']
__composekeys={'app-name':'appname',
    'add-function':'functionlist'
}
__composekeyslist=['app-name','add-function']
__loopcommands=['clear', 'list', 'help', 'show']
__listcommands=['organization','domain', 'platform', 'action funclet', 'action funclet version','runtime', 'runtime version']
__searchkeys=['organization','domain', 'platform', 'action funclet','action funclet version','runtime', 'runtime version']

__man_action_event='''create an event and bind it to an action funclet from the
action registry, an action-event may have a user provided pre and/or post
processing funclets.'''
__man_funclet_event='''create an event and bind it to a funclet provided by the
user, the funclet is not persisted in the registry.'''
__man_ephemeron='''execute an ephimeral funclet that is not bound to any
event and is executed as soon as deployed'''
__man_action='''an action funclet is a funclet that resides in the action
registry, this can then be later bound to events deployed using the
action-event context'''
__help={'list':'list the available choices for this context',
        'clear':'clears the screen',
        'quit':'exit the command line interface',
        'create-action':__man_action,
        'action-event':__man_action_event,
        'funclet-event':__man_funclet_event,
        'create-ephemeron':__man_ephemeron,
        'action-event-help':{
            'name':'\033[1mname of the event, * indicates mandatory field',
            'source asn':'\033[1mappliance serial number of the event source',
            'organization':'\033[1mname of the organization, * indicates mandatory field',
            'domain':'\033[1muse list command to view the available domains, * indicates mandatory field',
            'action funclet':'\033[1muse list command to view the available funclets, * indicates mandatory field',
            'action funclet version':'\033[1muse list command to view the available versions for the selected action, * indicates mandatory field',
            'platform':'\033[1muse list command to view the available platforms, * indicates mandatory field',
            'runtime':'\033[1muse list command to view the available runtimes, * indicates mandatory field',
            'runtime version':'\033[1muse list command to view available runtime versions, * indicates mandatory field',
            'upload file folder':'\033[1mfolder or directory containing the zip file containing pre/post functions, config and requirements files',
            'upload file name':'\033[1mzip file containing pre/post functions, config file etc.',
            'target url':'\033[1murl of the target ReST endpoint',
            'target port':'\033[1mport of the target ReST endpoint',
            'target api version':'\033[1mapi version of the ReST service',
            'target username':'\033[1musername for the target',
            'target password':'\033[1mpassword for the target'
        },
        'create-action-help':{
            'action name':'\033[1mname of the action funclet, * indicates mandatory field',
            'action version':'\033[1mversion of the action funclet, * indicates mandatory field',
            'organization':'\033[1morganization of the action, * indicates mandatory field',
            'domain':'\033[1mdomain of the action, * indicates mandatory field',
            'platform':'\033[1mplatform of the action, * indicates mandatory field',
            'runtime':'\033[1mruntime to execute the action, * indicates mandatory field',
            'runtime version':'\033[1mversion of the runtime to execute the action, * indicates mandatory field',
            'upload file folder':'\033[1mfolder or directory containing the zip file, * indicates a mandatory field',
            'upload file name':'\033[1mzip file containing action funclet and action.ecaaf files, * indicates a mandatory field'
        },
        'funclet-event-help':{
            'name':'\033[1mname of the funclet',
            'source asn':'\033[1mappliance serial number of the event source',
            'generic funclet':'\033[1muse list command to view the available funclets',
            'runtime':'\033[1muse list command to view the available runtimes',
            'runtime version':'\033[1muse list command to view available runtime versions',
            'upload file folder':'\033[1mfolder or directory containing the zip file containing pre/post funclets',
            'upload file name':'\033[1mzip file containing pre/post funclets etc.'
        },
        'create-ephemeron-help':{
            'name':'\033[1mname of the event',
            'generic funclet':'\033[1muse list command to view the available funclets',
            'runtime':'\033[1muse list command to view the available runtimes',
            'runtime version':'\033[1muse list command to view available runtime versions',
            'upload file folder':'\033[1mfolder or directory containing the zip file containing pre/post funclets, config and requirements files',
            'upload file name':'\033[1mzip file containing pre/post funclets etc.'
        }
}
SQLCompleter = WordCompleter(['event','name', 'organization','domain',\
                                'platform','runtime',\
                                'action','target-url'\
                                'help','quit','clear'],
                             ignore_case=True)
history = InMemoryHistory()

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

def get_funclet_tree(type):
    r=None
    funclet_tree={}
    data={}
    username=''
    password=''
    params={}
    url = __ecaaf_api_gateway+'ecaaf/api/v1.0/funclettree'
    headers = {'Content-type':'application/json', 'Accept':'application/json'}
    auth=HTTPBasicAuth('admin', 'admin')
    try:
        if (type=='get'):
            r = requests.get(url, auth=auth,params=params,data=data, headers=headers)
        if r:
            if r.status_code == requests.codes.ok:
                return json.loads(json.dumps(r.json()))
    except:
        return None

def ecaaf_api_gateway_upload_file(data, type):
    url=''
    if type == 'action-event':
        url = __ecaaf_api_gateway+'ecaaf/api/v1.0/action-event'
    if type == 'funclet-event':
        url = __ecaaf_api_gateway+'ecaaf/api/v1.0/funclet-event'
    if type == 'create-action':
        data['action']=data['ename']
        url = __ecaaf_api_gateway+'ecaaf/api/v1.0/create-action'
    if type == 'create-ephemeron':
        url = __ecaaf_api_gateway+'ecaaf/api/v1.0/ephemeron'
    if type == 'deploy-app':
        url = __ecaaf_api_gateway+'ecaaf/api/v1.0/deploy-app'
    headers = {'Content-type': 'multipart/form-data'}
    data['type']=type
    fileobj=None
    if data['fpath'] != '' and data['fname'] != '':
        fileobj = open(data['fpath']+'/'+data['fname'], 'rb')
    r=None
    try:
        if fileobj:
            r = requests.post(url, data = data, files={"file": (data['fname'],\
                fileobj)})
        else:
            r = requests.post(url, data = data)
        if r.status_code == requests.codes.ok:
            print('%s request sucessfully sent to ecaaf api gateway...'%type)
        if r.status_code == requests.codes.conflict:
            print('Event already present...')
        return True
    except:
        print('Error could not process request...')
    return False

def ecaaf_api_get_event_binding(ename):
    return

def ecaaf_api_get_event_binding_all():
    return

def ecaaf_cli_usage():
    usage_str='''\033[1m
create-action\t\t- create an action funclet
action-event\t\t- deploy an action funclet and event binding
funclet-event\t\t- deploy a user funclet and event binding
deploy-app\t\t- deploy z-application
create-ephemeron\t- execute ephemeral funclet
list\t\t\t- list available options for the current context
help\t\t\t- get help for the current context
show\t\t\t- show the bind or action context build so far
quit\t\t\t- exit the current context, final context will exit the cli
'''
    print usage_str

def ecaaf_action_event_loop_commands(user_input,avl_vals,curr,btype, brq, bindkeys, bindkeyslist):
    help=__help['action-event-help']
    prmpt_str=u'ecaaf/'+btype+'/'
    prmpt=''
    try:
        user_input.strip()
        while True:
            if curr in __searchkeys or curr == 'name':
                prmpt=prmpt_str+curr+'*]:'
            else:
                prmpt=prmpt_str+curr+']:'
            if (curr in __searchkeys or curr == 'name') and user_input == '':
                if curr!='name':
                    print '%s is required field, use the list command to see the available options'%curr
                else:
                    print '%s is required field'%curr
            elif user_input == 'quit':
                return 'quit'
            elif user_input == 'list':
                if curr in __searchkeys:
                    for val in avl_vals:
                            print val
            elif user_input == 'show':
                for k in bindkeyslist:
                    if bindkeys[k] in brq:
                        print("%s: %s" % (k,brq[bindkeys[k]]))
            elif user_input == 'help':
                if curr in help:
                    print "\n\033[1m"+curr+" : "+help[curr]+"\n"
            elif user_input == 'clear':
                os.system('clear')
            elif curr in __searchkeys and user_input not in avl_vals:
                print 'Please select from one of the following options:'
                for val in avl_vals:
                    print val
            else:
                return user_input.strip()
            user_input = prompt(prmpt,
                        completer=SQLCompleter,
                        history=history,
                        auto_suggest=AutoSuggestFromHistory()
                        )
    except:
        print("Goodbye...")
    return user_input.strip()

def ecaaf_create_action_event(btype='action-event'):
    brq={}
    btype='action-event'
    src_tree={}
    prmpt_str=''
    prmpt_str=u'ecaaf/'+btype+'/'
    try:
        ft=get_funclet_tree('get')
        if not ft:
            print ('could not retrieve registry from api gateway, check if the api gateway is donw...')
            return
        src_tree['domain']=ft['ecaaf.catalog']
        lvl_data=src_tree['domain']
        __bindkeyslist = __eventbindkeyslist
        __bindkeys = __eventbindkeys
        print "\n\033[1mLet's define an action event and bind it to an action funclet!\033[0m\n"
        for k in __bindkeyslist:
            if k in __searchkeys or k == 'name':
                prmpt=prmpt_str+k+'*]:'
            else:
                prmpt=prmpt_str+k+']:'
            user_input = prompt(prmpt,
                                completer=SQLCompleter,
                                history=history,
                                auto_suggest=AutoSuggestFromHistory()
                                )
            if user_input in __loopcommands or k in __searchkeys or \
            user_input=='':
                if k in __searchkeys:
                    user_input=ecaaf_action_event_loop_commands(user_input,\
                    lvl_data, k, btype,brq, __bindkeys, __bindkeyslist)
                else:
                    user_input=ecaaf_action_event_loop_commands(user_input,{}, \
                    k, btype, brq,__bindkeys,__bindkeyslist)
                #quitting the inner context
                if user_input=='quit':
                    return
            #quitting the outer context
            if user_input=='quit':
                return
            key2=__bindkeys[k]
            brq[key2]=user_input
            if user_input in lvl_data and k in __searchkeys:
                lvl_data=lvl_data[user_input]
        print "\n\033[1mReview event:\033[0m"
        for k in __bindkeyslist:
            print("{0}: {1}".format(k,brq[__bindkeys[k]]))
        print ""
        user_input = prompt(u'Deploy %s? (y/n)>'%btype,
                            completer=SQLCompleter,history=history,
                            auto_suggest=AutoSuggestFromHistory()
                            )
        user_input.strip()
        if user_input=='quit':
            return
        if user_input == 'y' or user_input == 'Y':
            if 'asn' in brq:
                #Change this assignment later to make treat asn at server
                #for now concat asn to event_name
                #Target Simulator should encode asn with event name in the curl
                #request.
                temp=brq['ename']+'.'+brq['asn']
                brq['ename']=temp
            print str(brq)
            ecaaf_api_gateway_upload_file(brq,'action-event')
        else:
            print('Binding ignored...')
        if user_input == 'clear':
            os.system('clear')
    except:
        print("Oops something went wrong....")
        traceback.print_exc(file=sys.stdout)
    return

def ecaaf_action_loop_commands(user_input,avl_vals,curr,btype, brq, bindkeyslist,\
    bindkeys):
    if btype=='create-action':
        help=__help['create-action-help']
    if btype=='funclet-event':
        help=__help['funclet-event-help']
    if btype=='create-ephemeron':
        help=__help['create-ephemeron-help']
    prmpt_str=u'ecaaf/'+btype+'/'
    prmpt=''
    try:
        user_input.strip()
        while True:
            prmpt=prmpt_str+curr+'*]:'
            if user_input == '':
                print '%s is required field'%curr
            elif user_input == 'quit':
                return 'quit'
            elif user_input == 'list':
                print ''
            elif user_input == 'show':
                for k in bindkeyslist:
                    if bindkeys[k] in brq:
                        print("{0}: {1}".format(k,brq[bindkeys[k]]))
            elif user_input == 'help':
                if curr in help:
                    print "\n\033[1m"+curr+" : "+help[curr]+"\n"
            elif user_input == 'clear':
                os.system('clear')
            else:
                return user_input.strip()
            user_input = prompt(prmpt,
                        completer=SQLCompleter,
                        history=history,
                        auto_suggest=AutoSuggestFromHistory()
                        )
    except:
        print("Goodbye...")
    return user_input.strip()

def ecaaf_create_action(btype='create-action'):
    brq={}
    src_tree={}
    prmpt_str=''
    prmpt_str=u'ecaaf/'+btype+'/'
    try:
        if btype == 'create-action':
            __bindkeyslist = __actionbindkeyslist
            __bindkeys = __actionbindkeys
            print "\n\033[1mLet's deploy an action funclet!\033[0m\n"
        if btype == 'funclet-event':
            __bindkeyslist = __funceventbindkeyslist
            __bindkeys = __funceventbindkeys
            print "\n\033[1mLet's create a funclet-event binding!\033[0m\n"
        if btype == 'create-ephemeron':
            __bindkeyslist = __funceventbindkeyslist
            __bindkeys = __funceventbindkeys
            print "\n\033[1mLet's create an ephemeron!\033[0m\n"
        if btype == 'deploy-app':
            __bindkeyslist = __deployappbindkeyslist
            __bindkeys = __deployapptbindkeys
            print "\n\033[1mLet's create an ephemeron!\033[0m\n"
        for k in __bindkeyslist:
            prmpt=prmpt_str+k+'*]:'
            user_input = prompt(prmpt,
                                completer=SQLCompleter,
                                history=history,
                                auto_suggest=AutoSuggestFromHistory()
                                )
            if user_input in __loopcommands or k in __bindkeyslist or \
            user_input=='':
                user_input=ecaaf_action_loop_commands(user_input,{}, k, btype, \
                brq, __bindkeyslist,__bindkeys)
                #quitting the inner context
                if user_input=='quit':
                    return
            #quitting the outer context
            if user_input=='quit':
                return
            key2=__bindkeys[k]
            brq[key2]=user_input
        print "\n\033[1mReview action:\033[0m"
        for k in __bindkeyslist:
            print("%s: %s" % (k,brq[__bindkeys[k]]))
        print ""
        user_input = prompt(u'Commit %s? (y/n)>'%btype,
                            completer=SQLCompleter,history=history,
                            auto_suggest=AutoSuggestFromHistory()
                            )
        user_input.strip()
        if user_input=='quit':
            return
        if user_input == 'y' or user_input == 'Y':
            ecaaf_api_gateway_upload_file(brq, btype)
        else:
            print('%s context ignored...' % btype)
        if user_input == 'clear':
            os.system('clear')
    except:
        print("Oops something went wrong....")
        traceback.print_exc(file=sys.stdout)
    return

def ecaaf_add_task(btype='add-task'):
    brq={}
    btype='add-task'
    src_tree={}
    prmpt_str=''
    prmpt_str=u'ecaaf/'+btype+'/'
    try:
        ft=get_funclet_tree('get')
        if not ft:
            print ('could not retrieve registry from api gateway, check if the api gateway is donw...')
            return
        src_tree['domain']=ft['ecaaf.catalog']
        lvl_data=src_tree['domain']
        __bindkeyslist = __eventbindkeyslist
        __bindkeys = __eventbindkeys
        print "\n\033[1mLet's define an action event and bind it to an action funclet!\033[0m\n"
        for k in __bindkeyslist:
            if k in __searchkeys or k == 'name':
                prmpt=prmpt_str+k+'*]:'
            else:
                prmpt=prmpt_str+k+']:'
            user_input = prompt(prmpt,
                                completer=SQLCompleter,
                                history=history,
                                auto_suggest=AutoSuggestFromHistory()
                                )
            if user_input in __loopcommands or k in __searchkeys or \
            user_input=='':
                if k in __searchkeys:
                    user_input=ecaaf_action_event_loop_commands(user_input,\
                    lvl_data, k, btype,brq, __bindkeys, __bindkeyslist)
                else:
                    user_input=ecaaf_action_event_loop_commands(user_input,{}, \
                    k, btype, brq,__bindkeys,__bindkeyslist)
                #quitting the inner context
                if user_input=='quit':
                    return
            #quitting the outer context
            if user_input=='quit':
                return
            key2=__bindkeys[k]
            brq[key2]=user_input
            if user_input in lvl_data and k in __searchkeys:
                lvl_data=lvl_data[user_input]
        print "\n\033[1mReview event:\033[0m"
        for k in __bindkeyslist:
            print("{0}: {1}".format(k,brq[__bindkeys[k]]))
        print ""
        user_input = prompt(u'Add task %s? (y/n)>'%btype,
                            completer=SQLCompleter,history=history,
                            auto_suggest=AutoSuggestFromHistory()
                            )
        user_input.strip()
        if user_input=='quit':
            return
        if user_input == 'y' or user_input == 'Y':
            return brq
        else:
            print('Binding ignored...')
        if user_input == 'clear':
            os.system('clear')
    except:
        print("Oops something went wrong....")
        traceback.print_exc(file=sys.stdout)
    return

def ecaaf_compose_app(btype='deploy-app'):
    brq={}
    src_tree={}
    functionlist=[]
    eventsource={}
    can_optimize=False
    prmpt_str=''
    prmpt_str=u'ecaaf-cli/'+btype+'/'
    try:
        __bindkeyslist = __composekeyslist
        __bindkeys = __composekeys
        for k in __bindkeyslist:
            if k == 'app-name':
                prmpt=prmpt_str+k+'*]:'
                user_input = prompt(prmpt,
                                    completer=SQLCompleter,
                                    history=history,
                                    auto_suggest=AutoSuggestFromHistory()
                                    )
            if k == 'add-function':
                prmpt=prmpt_str+k+']:'
                user_input='y'
            if k == 'add-function' and (user_input == 'y' or user_input == 'Y'):
                while (user_input == 'y' or user_input == 'Y'):
                    ae=ecaaf_add_task('add-task')
                    if ae=='quit':
                        return
                    functionlist.append(ae)
                    if ae['event_source'] not in eventsource:
                        eventsource[ae['event_source']]=[ae['ename']]
                    else:
                        eventsource[ae['event_source']].append(ae['ename'])
                    user_input = prompt(prmpt+' add more(y/n)?',
                                        completer=SQLCompleter,
                                        history=history,
                                        auto_suggest=AutoSuggestFromHistory()
                                        )
                key2=__bindkeys[k]
                brq[key2]=json.dumps(functionlist)
                brq['event_source']=eventsource
            elif k == 'app-name':
                key2=__bindkeys[k]
                brq[key2]=user_input
            #quitting the outer context
            if user_input=='quit':
                return
        print "\n\033[1mReview app:\033[0m"
        print("{0}: {1}".format('app-name',brq['appname']))
        for itm in json.loads(brq['functionlist']):
            print("{0}: {1}".format('function-name',itm['ename']))
        print ""
        for k in brq['event_source'].keys():
            if len(brq['event_source'][k]) > 1:
                    can_optimize=True
        if can_optimize:
            user_input = prompt(u'Run N-Dimesional Analyzer? (y/n)>',
                                completer=SQLCompleter,history=history,
                                auto_suggest=AutoSuggestFromHistory()
                                )
            if user_input == 'y' or user_input == 'Y':
                brq['optimize']='y'
                brq['analyze']='y'
                print "\n\033[1mGenerating analysis for application %s...\033[0m"%brq['appname'],
                #TODO:Uncomment it later...
                #status,ret=ecaaf_api_gateway_upload_file(brq,'deploy-app')

                spinner = spinning_cursor()
                while ret['status']!='analysis-completed':
                    sys.stdout.write(next(spinner))
                    sys.stdout.flush()
                    time.sleep(0.5)
                    status,ret=ecaaf_api_gateway_upload_file(brq,'deploy-app')
                    sys.stdout.write('\b')
                print "\n"
                if status==True:
                    print '\n\033[1m-------------------------------------------------------------------------\033[0m'
                    print '\n\033[1mNormal AWS Execution\033[0m'
                    print '\n\033[1m-------------------------------------------------------------------------\033[0m'
                    print "\n\033[1mCost of each function:\033[0m"
                    funcs=ret['regular_run']
                    for func in funcs:
                        print func+'\t\t:\t'+str(math.ceil(float(funcs[func])*1000)/1000)+' GB-seconds'
                    print "\n\033[1mApp cost\t\t:\t%s GB-seconds\033[0m"\
                    %str(math.ceil(float(ret['regular_run_tot'])*1000)/1000)
                    print '\n\033[1m-------------------------------------------------------------------------\033[0m'
                    print '\n\033[1mN-Dimensional Analyzed AWS Execution\033[0m'
                    print '\n\033[1m-------------------------------------------------------------------------\033[0m'
                    print "\n\033[1mCost of each function:\033[0m"
                    funcs=ret['regular_run']
                    for func in funcs:
                        print func+'\t\t:\t'+str(math.ceil(float(funcs[func])*1000)/1000)+' GB-seconds'
                    print "\n\033[1mApp cost\t\t:\t%s GB-seconds\033[0m"\
                    %str(math.ceil(float(ret['optimized_run'])*1000)/1000)
                    print '\n\033[1m-------------------------------------------------------------------------\033[0m'
                    print "\n\033[1mResult: N-Dimensional analyzed version is %s percent cheaper\033[0m"\
                    %str(math.ceil(float(ret['percentage_gain'])))
                    print '\n\033[1m-------------------------------------------------------------------------\033[0m'
        user_input = prompt(u'Deploy %s? (y/n)>'%btype,
                            completer=SQLCompleter,history=history,
                            auto_suggest=AutoSuggestFromHistory()
                            )
        user_input.strip()
        if user_input=='quit':
            return
        if user_input == 'y' or user_input == 'Y':
            print 'App %s sucessfully deployed...'%brq['appname']
            #TODO:Add final deploy code...
            #ecaaf_api_gateway_upload_file(brq,'deploy-app')
        else:
            print('Binding ignored...')
        if user_input == 'clear':
            os.system('clear')
    except:
        print("Oops something went wrong....")
        traceback.print_exc(file=sys.stdout)
    return

def ecaaf_cli_start():
    __f['action-event']=ecaaf_create_action_event
    __f['funclet-event']=ecaaf_create_action
    __f['create-action']=ecaaf_create_action
    __f['create-ephemeron']=ecaaf_create_action
    __f['deploy-app']=ecaaf_compose_app
    __f['help']=ecaaf_cli_usage
    os.system('clear')
    print("\n\033[1mWelcome to ecaaf command line interface!!\n\033[0m")
    ecaaf_cli_usage()
    while 1:
        user_input = prompt(u'ecaaf>',
                            completer=SQLCompleter, history=history,
                            auto_suggest=AutoSuggestFromHistory()
                            )
        user_input.strip()
        if user_input == 'quit':
            break
        elif user_input=='clear':
            os.system('clear')
        elif 'help' in user_input:
            opts=user_input.split(' ')
            if len(opts) > 2:
                print ('%s not recognized' % user_input)
            elif len(opts) == 2 and opts[1] in __help:
                    print "\033[1m"+opts[1]+"\033[0m: "+__help[opts[1]]
            else:
                print "\033[1m help [context]\033[0m, example help ephemeron"
        elif user_input == 'list':
            ecaaf_cli_usage()
        elif user_input=='show':
            print ''
        else :
            if(user_input in __f):
                __f[user_input](user_input)
            else:
                print('%s not recognized'%user_input)

if __name__=='__main__':
    ecaaf_cli_start()

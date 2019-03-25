"""Wrapper for container runtime used by the core services"""

import docker

__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"

__client=docker.from_env()
#container helper functions
def dclient():
    return __client

def dbuild(tdir,tag):
    img=__client.images.build(path=tdir,tag=tag, network_mode="host")
    return img

#def drun(tag,e,v):
#    container=__client.containers.run(tag,environment=[e],\
#        detach=False,volumes=v,remove=True, network_mode="bridge")
#    return container

##Need to run in host network mode to get pass proxies
def drun(tag,e,v):
    container=__client.containers.run(tag,environment=[e],\
        detach=False,volumes=v,remove=True, network_mode="host")
    return container
#TODO:save a docker image to a tar ball
def dsave():
    return

#TODO:load a docker image from tar ball
def dload():
    return

#TODO:delete a docker image
def delete():
    return

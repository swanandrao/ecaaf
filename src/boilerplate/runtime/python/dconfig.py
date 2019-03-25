"""Configuraton file for the container env only the api gateway settings need
to be changed during production deployment """

__author__      = "Swanand Rao"
__copyright__   = ""
__credits__     = ["Swanand Rao"]
__license__     = ""
__version__     = "0.1"
__maintainer__  = "Swanand Rao"
__email__       = "swanand.rao@gmail.com"
__status__      = "pre-alpha"

__config={
    'scratchdir':'/host/scratch',
    'logdir':'/host/logs',
    'api_gateway_url':'http://docker.for.mac.host.internal',
    'api_gateway_port':'5000'
}

def scratchdir():
    return __config['scratchdir']

def logdir():
    return __config['logdir']

def apigateway():
    return __config['api_gateway_url']+'/'+__config['api_gateway_port']

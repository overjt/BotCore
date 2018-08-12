from gpapi.googleplay import GooglePlayAPI
from utils import evalRegex
from settings import CREDENTIALS
from os.path import expanduser
import os
import pickle

HOMEDIR = expanduser("~/.botcoregplay/")
DEVICECODE = "bacon"
CACHEDIR = HOMEDIR+'cache/';
CACHEFILE = CACHEDIR + DEVICECODE + '.txt'
CONFIGDIR = HOMEDIR+'config/';
CONFIGFILE = CONFIGDIR + 'config.txt'
STORAGEPATH = os.path.join(os.getcwd(), "media", "files", "temp")

def write_cache(gsfId, token):
    if not os.path.exists(CACHEDIR):
        os.makedirs(os.path.dirname(CACHEDIR))
    info = {'gsfId': gsfId, 'token': token}
    pickle.dump(info, open(CACHEFILE, "wb"))

def read_cache():
    try:
        with open(CACHEFILE, "rb") as f:
            info = pickle.load(f)
    except:
        info = None
    return info

def refresh_cache(server, email, password):
    server.login(email, password, None, None)
    write_cache(server.gsfId, server.authSubToken)

def do_login(server, email, password):
    cacheinfo = read_cache()
    if cacheinfo:
        # Sign in using cached info
        try:
            server.login(None, None, cacheinfo['gsfId'], cacheinfo['token'])
        except:
            refresh_cache(server, email, password)
    else:
        # Re-authenticate using email and pass and save info to cache
        refresh_cache(server, email, password)
    return server
try:
    if os.path.exists(CONFIGFILE):
        with open(CONFIGFILE, "rb") as f:
            config = pickle.load(f)
            email = config['email']
            password = config['password']
    else:
        raise
except:
    email = None
    password = None

if email is None and password is None:
    if not os.path.exists(CONFIGDIR):
        os.makedirs(os.path.dirname(CONFIGDIR))
        config = {'email': CREDENTIALS.get("playstoreEmail"), 'password': CREDENTIALS.get("playstorePassword")}
        pickle.dump(config, open(CONFIGFILE, "wb"))

def getApk(packageId):
    server = GooglePlayAPI('en_US', 'America/New York', DEVICECODE)
    try:
        server = do_login(server, email, password)
    except:
        return {
            "type": "text",
            "message": "Error al ingresar al PlayStore"
        }
    try:
        paths = []
        download = server.download(packageId, expansion_files=True)
        apkpath = os.path.join(STORAGEPATH, download['docId'] + '.apk')
        if not os.path.isdir(STORAGEPATH):
            os.makedirs(STORAGEPATH)
        with open(apkpath, 'wb') as first:
            for chunk in download.get('file').get('data'):
                first.write(chunk)
        paths.append(apkpath)

        for obb in download['additionalData']:
            name = obb['type'] + '.' + str(obb['versionCode']) + '.' + download['docId'] + '.obb'
            obbpath = os.path.join(STORAGEPATH, download['docId'], name)
            if not os.path.isdir(os.path.join(STORAGEPATH, download['docId'])):
                os.makedirs(os.path.join(STORAGEPATH, download['docId']))
            with open(obbpath, 'wb') as second:
                for chunk in obb.get('file').get('data'):
                    second.write(chunk)
            paths.append(obbpath)
        return {
            "type": "files",
            "paths": paths
        }
    except Exception as err:
        print("[APKDOWNLOADER]", err)
        return {
            "type": "text",
            "message": "Error al descargar la aplicación, asegurese que no sea de pago o incompatible"
        }

def process_message(message, msg_sender, msg_to, msg_type, connector, bot):
    regex = "(?:^{bot_name} |^\.)apk (.*)$".format(bot_name=bot.name.lower())
    found = evalRegex(regex, message)
    if found:
        response = getApk(found)
        if response:
            if response["type"] == "files":
                for apkFile in response.get("paths", []):
                    connector.send_file(
                        msg_to, apkFile, is_reply=True)
            else:
                connector.send_message(
                    msg_to, response["message"], is_reply=True)
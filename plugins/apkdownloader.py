from gpapi.googleplay import GooglePlayAPI
from utils import downloadImage, evalRegex, bytes2Human
from settings import CREDENTIALS
from os.path import expanduser
import os
import pickle
from io import open as iopen

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

def getApk(packageId, connector, msg_to):
    server = GooglePlayAPI('es_CO', 'America/Bogota', DEVICECODE)
    try:
        server = do_login(server, email, password)
    except:
        return {
            "type": "text",
            "message": "Error al ingresar al PlayStore"
        }
    try:
        paths = []
        packageInfo = server.details(packageId)
        msg = """Descargando la siguiente aplicación:
Nombre: {title}
Versión: {version}
Fecha de actualización: {upload_date}
Peso: {installationSize}""".format(
            title = packageInfo["title"],
            version = packageInfo["versionCode"],
            upload_date = packageInfo["uploadDate"],
            installationSize = bytes2Human(packageInfo["installationSize"])
        )
        try:
            img_path = downloadImage(packageInfo["images"][0]["url"])
        except:
            img_path = None

        if img_path:        
            connector.send_image(msg_to, img_path, is_reply=True, caption=msg)
        else:
            connector.send_message(msg_to, msg, is_reply=True)
        download = server.download(packageId, expansion_files=True)
        apkStoragePath = os.path.join(STORAGEPATH,str(packageInfo['docId']),str(packageInfo["versionCode"]))
        apkpath = os.path.join(apkStoragePath, download['docId'] + '.apk')
        if not os.path.isdir(apkStoragePath):
            os.makedirs(apkStoragePath)
        
        if not os.path.isfile(apkpath):
            apkpathTemp = apkpath + ".temp"
            if os.path.isfile(apkpathTemp):
                return connector.send_message(msg_to, "Se está descargando, por favor intente mas tarde...", is_reply=True)
            with iopen(apkpathTemp, 'wb') as first:
                for chunk in download.get('file').get('data'):
                    first.write(chunk)
            os.rename(apkpathTemp, apkpath)
        paths.append(apkpath)

        for obb in download['additionalData']:
            name = obb['type'] + '.' + str(obb['versionCode']) + '.' + download['docId'] + '.obb'
            obbpath = os.path.join(STORAGEPATH, download['docId'], name)
            if not os.path.isdir(os.path.join(STORAGEPATH, download['docId'])):
                os.makedirs(os.path.join(STORAGEPATH, download['docId']))

            if not os.path.isfile(obbpath):
                obbpathTemp = obbpath + ".temp"
                if os.path.isfile(obbpathTemp):
                    return connector.send_message(msg_to, "Se está descargando, por favor intente mas tarde...", is_reply=True)
                with iopen(obbpathTemp, 'wb') as second:
                    for chunk in obb.get('file').get('data'):
                        second.write(chunk)
                os.rename(obbpathTemp, obbpath)
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
        response = getApk(found, connector, msg_to)
        if response:
            if response["type"] == "files":
                for apkFile in response.get("paths", []):
                    connector.send_file(
                        msg_to, apkFile, is_reply=True)
            else:
                connector.send_message(
                    msg_to, response["message"], is_reply=True)
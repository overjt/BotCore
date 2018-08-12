import re
import requests
from io import open as iopen
import hashlib
import os


def downloadImage(url):
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        file_name = hashlib.md5(url.encode('utf-8')).hexdigest() + "." + r.headers['Content-Type'].split('/')[1]
        file_path = os.path.join(os.getcwd(), "media",
                                 "images", "temp")
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        
        file_path = os.path.join(file_path, file_name)
        if not os.path.isfile(file_path):
            file_path_temp = file_path + ".temp"
            if os.path.isfile(file_path_temp):
                os.remove(file_path_temp)

            with iopen(file_path_temp, 'wb') as file:
                file.write(r.content)
            os.rename(file_path_temp, file_path)
        return file_path
    return None


def evalRegex(regex, text):
    try:
        found = re.search(regex, text, re.IGNORECASE).group(1)
    except AttributeError:
        found = None
    return found

import requests

def openURL(URL, params):
    r = requests.get(URL + "?", params=params)
    #print(r.text)
    return r.text

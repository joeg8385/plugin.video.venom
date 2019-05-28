# -*- coding: utf-8 -*-

'''
    Venom Add-on
'''
import json

from resources.lib.modules import client
from resources.lib.modules import control


user = control.setting('fanart.tv.user')
if user == '' or user == None:
    user = 'cf0ebcc2f7b824bd04cf3a318f15c17d'

headers = {'api-key': '9f846e7ec1ea94fad5d8a431d1d26b43'}
if not user == '':
    headers.update({'client-key': user})

base_url = "http://webservice.fanart.tv/v3/%s/%s"
lang = control.apiLanguage()['trakt']


def get_tvshow_art(tvdb):
    url = base_url % ('tv', '%s')
    try:
        art = client.request(url % tvdb, headers=headers, timeout='30', error=True)
        art = json.loads(art)
    except: return None

    try:
        poster2 = art['tvposter']
        poster2 = [(x['url'], x['likes']) for x in poster2 if x.get('lang') == lang] + [(x['url'], x['likes']) for x in poster2 if x.get('lang') == '']
        poster2 = [(x[0], x[1]) for x in poster2]
        poster2 = sorted(poster2, key=lambda x: int(x[1]), reverse=True)
        poster2 = [x[0] for x in poster2][0]
        poster2 = poster2.encode('utf-8')
    except:
        poster2 = '0'

    try:
        fanart2 = art['showbackground']
        fanart2 = [(x['url'], x['likes']) for x in fanart2 if x.get('lang') == lang] + [(x['url'], x['likes']) for x in fanart2 if x.get('lang') == '']
        fanart2 = [(x[0], x[1]) for x in fanart2]
        fanart2 = sorted(fanart2, key=lambda x: int(x[1]), reverse=True)
        fanart2 = [x[0] for x in fanart2][0]
        fanart2 = fanart2.encode('utf-8')
    except:
        fanart2= '0'

    try:
        banner2 = art['tvbanner']
        banner2 = [(x['url'], x['likes']) for x in banner2 if x.get('lang') == lang] + [(x['url'], x['likes']) for x in banner2 if x.get('lang') == '']
        banner2 = [(x[0], x[1]) for x in banner2]
        banner2 = sorted(banner2, key=lambda x: int(x[1]), reverse=True)
        banner2 = [x[0] for x in banner2][0]
        banner2 = banner2.encode('utf-8')
    except:
        banner2 = '0'

    try:
        if 'hdtvlogo' in art: clearlogo = art['hdtvlogo']
        else: clearlogo = art['clearlogo']
        clearlogo = [(x['url'], x['likes']) for x in clearlogo if x.get('lang') == lang] + [(x['url'], x['likes']) for x in clearlogo if x.get('lang') == '']
        clearlogo = [(x[0], x[1]) for x in clearlogo]
        clearlogo = sorted(clearlogo, key=lambda x: int(x[1]), reverse=True)
        clearlogo = [x[0] for x in clearlogo][0]
        clearlogo = clearlogo.encode('utf-8')
    except:
        clearlogo = '0'

    try:
        if 'hdclearart' in art: clearart = art['hdclearart']
        else: clearart = art['clearart']
        clearart = [(x['url'], x['likes']) for x in clearart if x.get('lang') == lang] + [(x['url'], x['likes']) for x in clearart if x.get('lang') == '']
        clearart = [(x[0], x[1]) for x in clearart]
        clearart = sorted(clearart, key=lambda x: int(x[1]), reverse=True)
        clearart = [x[0] for x in clearart][0]
        clearart = clearart.encode('utf-8')
    except:
        clearart = '0'

    try:
        if 'tvthumb' in art: landscape = art['tvthumb']
        else: landscape = art['showbackground']
        landscape = [(x['url'], x['likes']) for x in landscape if x.get('lang') == lang] + [(x['url'], x['likes']) for x in landscape if x.get('lang') == '']
        landscape = [(x[0], x[1]) for x in landscape]
        landscape = sorted(landscape, key=lambda x: int(x[1]), reverse=True)
        landscape = [x[0] for x in landscape][0]
        landscape = landscape.encode('utf-8')
    except:
        landscape = '0'

    extended_art = {'extended': True, 'poster2': poster2, 'banner2': banner2, 'fanart2': fanart2, 'clearlogo': clearlogo, 'clearart': clearart, 'landscape': landscape}
    return extended_art


def get_movie_art(imdb):
    url = base_url % ('movies', '%s')
    try:
        artmeta = True
        art = client.request(url % imdb, headers=headers, timeout='30', error=True)
        try: art = json.loads(art)
        except: artmeta = False
        if artmeta == False: return None
    except:
            pass

    try:
        poster2 = art['movieposter']
        poster2 = [(x['url'], x['likes']) for x in poster2 if x.get('lang') == lang] + [(x['url'], x['likes']) for x in poster2 if x.get('lang') == '']
        poster2 = [(x[0], x[1]) for x in poster2]
        poster2 = sorted(poster2, key=lambda x: int(x[1]), reverse=True)
        poster2 = [x[0] for x in poster2][0]
        poster2 = poster2.encode('utf-8')
    except:
        poster2 = '0'

    try:
        if 'moviebackground' in art: fanart2 = art['moviebackground']
        else: fanart2 = art['moviethumb']
        fanart2 = [(x['url'], x['likes']) for x in fanart2 if x.get('lang') == lang] + [(x['url'], x['likes']) for x in fanart2 if x.get('lang') == '']
        fanart2 = [(x[0], x[1]) for x in fanart2]
        fanart2 = sorted(fanart2, key=lambda x: int(x[1]), reverse=True)
        fanart2 = [x[0] for x in fanart2][0]
        fanart2 = fanart2.encode('utf-8')
    except:
        fanart2 = '0'

    try:
        banner2 = art['moviebanner']
        banner2 = [(x['url'], x['likes']) for x in banner2 if x.get('lang') == lang] + [(x['url'], x['likes']) for x in banner2 if x.get('lang') == '']
        banner2 = [(x[0], x[1]) for x in banner2]
        banner2 = sorted(banner2, key=lambda x: int(x[1]), reverse=True)
        banner2 = [x[0] for x in banner2][0]
        banner2 = banner2.encode('utf-8')
    except:
        banner2 = '0'

    try:
        if 'hdmovielogo' in art: clearlogo = art['hdmovielogo']
        else: clearlogo = art['movielogo']
        clearlogo = [(x['url'], x['likes']) for x in clearlogo if x.get('lang') == lang] + [(x['url'], x['likes']) for x in clearlogo if x.get('lang') == '']
        clearlogo = [(x[0], x[1]) for x in clearlogo]
        clearlogo = sorted(clearlogo, key=lambda x: int(x[1]), reverse=True)
        clearlogo = [x[0] for x in clearlogo][0]
        clearlogo = clearlogo.encode('utf-8')
    except:
        clearlogo = '0'

    try:
        if 'hdmovieclearart' in art: clearart = art['hdmovieclearart']
        else: clearart = art['movieart']
        clearart = [(x['url'], x['likes']) for x in clearart if x.get('lang') == lang] + [(x['url'], x['likes']) for x in clearart if x.get('lang') == '']
        clearart = [(x[0], x[1]) for x in clearart]
        clearart = sorted(clearart, key=lambda x: int(x[1]), reverse=True)
        clearart = [x[0] for x in clearart][0]
        clearart = clearart.encode('utf-8')
    except:
        clearart = '0'

    try:
        discart = art['moviedisc']
        discart = [(x['url'], x['likes']) for x in discart if x.get('lang') == lang] + [(x['url'], x['likes']) for x in discart if x.get('lang') == '']
        discart = [(x[0], x[1]) for x in discart]
        discart = sorted(discart, key=lambda x: int(x[1]), reverse=True)
        discart = [x[0] for x in discart][0]
        discart = discart.encode('utf-8')
    except:
        discart = '0'

    try:
        if 'moviethumb' in art: landscape = art['moviethumb']
        else: landscape = art['moviebackground']
        landscape = [(x['url'], x['likes']) for x in landscape if x.get('lang') == lang] + [(x['url'], x['likes']) for x in landscape if x.get('lang') == '']
        landscape = [(x[0], x[1]) for x in landscape]
        landscape = sorted(landscape, key=lambda x: int(x[1]), reverse=True)
        landscape = [x[0] for x in landscape][0]
        landscape = landscape.encode('utf-8')
    except:
        landscape = '0'

    extended_art = {'extended': True, 'poster2': poster2, 'fanart2': fanart2, 'banner2': banner2, 'clearlogo': clearlogo, 'clearart': clearart, 'discart': discart, 'landscape': landscape}
    return extended_art
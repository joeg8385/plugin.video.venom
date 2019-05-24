# -*- coding: utf-8 -*-

'''
Venom
'''

import os,sys,re,datetime,xbmc
import json,urlparse,requests

from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import metacache
from resources.lib.modules import workers
from resources.lib.modules import log_utils

# from resources.lib.modules import trakt


class movies:
    def __init__(self):
        # self.list = [{'content': 'movie'}]
        self.list = []
        self.meta = []

        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))

        self.lang = control.apiLanguage()['trakt']

        self.imdbinfo = 'https://www.omdbapi.com/?i=%s&plot=short&r=json'

        self.tmdb_key = control.setting('tm.user')
        if self.tmdb_key == '' or self.tmdb_key == None:
            self.tmdb_key = '3320855e65a9758297fec4f7c9717698'

        self.tmdb_lang = 'en'
        self.tmdb_link = 'http://api.themoviedb.org'
        self.tmdb_image = 'http://image.tmdb.org/t/p/original'
        self.tmdb_poster = 'http://image.tmdb.org/t/p/w500'
        # self.tmdb_api_link = 'http://api.themoviedb.org/3/list/%s?api_key=%s' % ('%s', '%s')
        self.tmdb_info_link = 'http://api.themoviedb.org/3/movie/%s?api_key=%s&language=%s&append_to_response=credits,releases,external_ids' % ('%s', self.tmdb_key, self.tmdb_lang)

        self.tmdb_art_link = 'http://api.themoviedb.org/3/movie/%s/images?api_key=' + self.tmdb_key
        self.tmdb_img_link = 'http://image.tmdb.org/t/p/w%s%s'

        self.fanart_tv_user = control.setting('fanart.tv.user')
        if self.fanart_tv_user == '' or self.fanart_tv_user == None:
            self.fanart_tv_user = 'cf0ebcc2f7b824bd04cf3a318f15c17d'
        self.user = str(self.fanart_tv_user) + str(self.tmdb_key)
        self.fanart_tv_art_link = 'http://webservice.fanart.tv/v3/movies/%s'


    def get_request(self, url):
        try:
            try:
                response = requests.get(url)
            except requests.exceptions.SSLError:
                response = requests.get(url, verify=False)
        except requests.exceptions.ConnectionError:
            control.notification(title='default', message=32028, icon='INFO')
            return

        if '200' in str(response):
            return json.loads(response.text)
        elif 'Retry-After' in response.headers:
            # API REQUESTS ARE BEING THROTTLED, INTRODUCE WAIT TIME
            throttleTime = response.headers['Retry-After']
            log_utils.log2('TMDB Throttling Applied, Sleeping for %s seconds' % throttleTime, '')
            sleep(int(throttleTime) + 1)
            return self.get_request(url)
        else:
            log_utils.log2('Get request failed to TMDB URL: %s' % url, 'error')
            log_utils.log2('TMDB Response: %s' % response.text, 'error')
            return None


    def tmdb_list(self, url):
        next = url
        # for i in re.findall('date\[(\d+)\]', url):
            # url = url.replace('date[%s]' % i, (self.datetime - datetime.timedelta(days = int(i))).strftime('%Y-%m-%d'))

        try:
            result = self.get_request(url % self.tmdb_key)
            # result = client.request(url % self.tmdb_key)
            # result = json.loads(result)
            items = result['results']

        except:
            return

        # try:
            # page = int(result['page'])
            # total = int(result['total_pages'])
            # if page >= total: raise Exception()
            # url2 = '%s&page=%s' % (url.split('&page=', 1)[0], str(page+1))
            # result = client.request(url2 % self.tmdb_key)
            # result = json.loads(result)
            # items += result['results']
        # except: pass
        try:
            page = int(result['page'])
            total = int(result['total_pages'])
            if page >= total: raise Exception()
            if not 'page=' in url: raise Exception()
            next = '%s&page=%s' % (next.split('&page=', 1)[0], str(page+1))
            next = next.encode('utf-8')
        except: next = ''

        for item in items:
            try:
                title = item['title']
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = item['release_date']
                year = re.compile('(\d{4})').findall(year)[-1]
                year = year.encode('utf-8')

                tmdb = item['id']
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

                poster = item['poster_path']
                if poster == '' or poster == None: poster = '0'
                if not poster == '0': poster = '%s%s' % (self.tmdb_poster, poster)
                poster = poster.encode('utf-8')

                fanart = item['backdrop_path']
                if fanart == '' or fanart == None: fanart = '0'
                if not fanart == '0': fanart = '%s%s' % (self.tmdb_image, fanart)
                fanart = fanart.encode('utf-8')

                premiered = item['release_date']
                try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')

                rating = str(item['vote_average'])
                if rating == '' or rating == None: rating = '0'
                rating = rating.encode('utf-8')

                votes = str(item['vote_count'])
                try: votes = str(format(int(votes),',d'))
                except: votes = '0'
                if votes == '' or votes == None: votes = '0'
                votes = votes.encode('utf-8')

                plot = item['overview']
                if plot == '' or plot == None: plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                try: tagline = item['tagline']
                except: tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                try: tagline = tagline.encode('utf-8')
                except: tagline = '0'

##--TMDb additional info
                url = self.tmdb_info_link % tmdb
                item = client.request(url, timeout='30')
                item = json.loads(item)

                tmdb = item['id']
                if tmdb == '' or tmdb == None: tmdb = '0'
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

                imdb = item['external_ids']['imdb_id']
                if imdb == '' or imdb == None: imdb = '0'
                imdb = imdb.encode('utf-8')

                # studio = item['production_companies']
                # try: studio = [x['name'] for x in studio][0]
                # except: studio = '0'
                # if studio == '' or studio == None: studio = '0'
                # studio = studio.encode('utf-8')

                genre = item['genres']
                try: genre = [x['name'] for x in genre]
                except: genre = '0'
                genre = ' / '.join(genre)
                genre = genre.encode('utf-8')
                if not genre: genre = 'NA'

                try: duration = str(item['runtime'])
                except: duration = '0'
                if duration == '' or duration == None or duration == 'N/A': duration = '0'
                duration = duration.encode('utf-8')

                mpaa = item['releases']['countries']
                try: mpaa = [x for x in mpaa if not x['certification'] == '']
                except: mpaa = '0'
                try: mpaa = ([x for x in mpaa if x['iso_3166_1'].encode('utf-8') == 'US'] + [x for x in mpaa if not x['iso_3166_1'].encode('utf-8') == 'US'])[0]['certification']
                except: mpaa = '0'
                mpaa = mpaa.encode('utf-8')

                director = item['credits']['crew']
                try: director = [x['name'] for x in director if x['job'].encode('utf-8') == 'Director']
                except: director = '0'
                if director == '' or director == None or director == []: director = '0'
                director = ' / '.join(director)
                director = director.encode('utf-8')

                writer = item['credits']['crew']
                try: writer = [x['name'] for x in writer if x['job'].encode('utf-8') in ['Writer', 'Screenplay']]
                except: writer = '0'
                try: writer = [x for n,x in enumerate(writer) if x not in writer[:n]]
                except: writer = '0'
                if writer == '' or writer == None or writer == []: writer = '0'
                writer = ' / '.join(writer)
                writer = writer.encode('utf-8')

                cast = item['credits']['cast']
                try: cast = [(x['name'].encode('utf-8'), x['character'].encode('utf-8')) for x in cast]
                except: cast = []

                # try:
                    # if not imdb == None or imdb == '0':
                        # # link returns "no API key provided"-need to investigate link used
                        # url = self.imdbinfo % imdb
                        # item = client.request(url, timeout='30')
                        # item = json.loads(item)

                        # plot2 = item['Plot']
                        # plot2 = client.replaceHTMLCodes(plot2)
                        # plot2 = plot.encode('utf-8')
                        # if plot == '' or plot == None: plot = plot2

                        # rating2 = str(item['imdbRating'])
                        # rating2 = rating2.encode('utf-8')
                        # if rating == '' or rating == None: rating = rating2

                        # votes2 = str(item['imdbVotes'])
                        # votes2 = str(format(int(votes2),',d'))
                        # votes2 = votes2.encode('utf-8')
                        # if votes == '' or votes == None: votes = votes2
                # except:
                    # pass

                item = {}
                item = {'content': 'movie', 'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': '0', 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline,
                        'code': tmdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'poster': poster, 'poster2': '0', 'poster3': '0', 'banner': '0', 'fanart': fanart, 'fanart2': '0', 'fanart3': '0', 'clearlogo': '0', 'clearart': '0', 'landscape': '0', 'next': next}
                meta = {}
                meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.lang, 'user': self.user, 'item': item}

                extended_art = self.extended_art(imdb)
                if not extended_art == None:
                    item.update(extended_art)
                    meta.update(item)

                self.list.append(item)
                self.meta.append(meta)
                metacache.insert(self.meta)

            except:
                pass
        return self.list


    def tmdb_collections_list(self, url):
        try:
            result = client.request(url)
            result = json.loads(result)
            items = result['items']
        except:
            return
        next = ''
        for item in items:
            try:
                media_type = item['media_type']
                title = item['title']
                if not media_type == 'movie': title = item['name']
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = item['release_date']
                try: year = re.compile('(\d{4})').findall(year)[0]
                except: year = '0'
                if year == '' or year == None: year = '0'
                year = year.encode('utf-8')

                tmdb = item['id']
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

                poster = item['poster_path']
                if poster == '' or poster == None: raise Exception()
                else: poster = '%s%s' % (self.tmdb_poster, poster)
                poster = poster.encode('utf-8')

                fanart = item['backdrop_path']
                if fanart == '' or fanart == None: fanart = '0'
                if not fanart == '0': fanart = '%s%s' % (self.tmdb_image, fanart)
                fanart = fanart.encode('utf-8')

                premiered = item['release_date']
                try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')

                rating = str(item['vote_average'])
                if rating == '' or rating == None: rating = '0'
                rating = rating.encode('utf-8')

                votes = str(item['vote_count'])
                try: votes = str(format(int(votes),',d'))
                except: pass
                if votes == '' or votes == None: votes = '0'
                votes = votes.encode('utf-8')

                plot = item['overview']
                if plot == '' or plot == None: plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                try: tagline = tagline.encode('utf-8')
                except: pass

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': '0', 'genre': '0', 'duration': '0', 'rating': rating, 'votes': votes, 'mpaa': '0', 'director': '0', 'writer': '0', 'cast': '0', 'plot': plot, 'tagline': tagline, 'code': '0', 'imdb': '0', 'tmdb': tmdb, 'tvdb': '0', 'poster': poster, 'banner': '0', 'fanart': fanart, 'next': next})
            except:
                pass
        return self.list


    def extended_art(self, imdb):
        self.fanart_tv_headers = {'api-key': '9f846e7ec1ea94fad5d8a431d1d26b43'}
        if not self.fanart_tv_user == '': self.fanart_tv_headers.update({'client-key': self.fanart_tv_user})

        try:
            artmeta = True
            art = client.request(self.fanart_tv_art_link % imdb, headers=self.fanart_tv_headers, timeout='30', error=True)
            try: art = json.loads(art)
            except: artmeta = False
            if artmeta == False: return None
        except:
            pass

        try:
            poster2 = art['movieposter']
            poster2 = [x for x in poster2 if x.get('lang') == self.lang][::-1] + [x for x in poster2 if x.get('lang') == 'en'][::-1] + [x for x in poster2 if x.get('lang') in ['00', '']][::-1]
            poster2 = poster2[0]['url'].encode('utf-8')
        except:
            poster2 = '0'

        try:
            if 'moviebackground' in art: fanart2 = art['moviebackground']
            else: fanart2 = art['moviethumb']
            fanart2 = [x for x in fanart if x.get('lang') == self.lang][::-1] + [x for x in fanart2 if x.get('lang') == 'en'][::-1] + [x for x in fanart2 if x.get('lang') in ['00', '']][::-1]
            fanart2 = fanart2[0]['url'].encode('utf-8')
        except:
            fanart2 = '0'

        try:
            banner = art['moviebanner']
            banner = [x for x in banner if x.get('lang') == self.lang][::-1] + [x for x in banner if x.get('lang') == 'en'][::-1] + [x for x in banner if x.get('lang') in ['00', '']][::-1]
            banner = banner[0]['url'].encode('utf-8')
        except:
            banner = '0'

        try:
            if 'hdmovielogo' in art: clearlogo = art['hdmovielogo']
            else: clearlogo = art['clearlogo']
            clearlogo = [x for x in clearlogo if x.get('lang') == self.lang][::-1] + [x for x in clearlogo if x.get('lang') == 'en'][::-1] + [x for x in clearlogo if x.get('lang') in ['00', '']][::-1]
            clearlogo = clearlogo[0]['url'].encode('utf-8')
        except:
            clearlogo = '0'

        try:
            if 'hdmovieclearart' in art: clearart = art['hdmovieclearart']
            else: clearart = art['clearart']
            clearart = [x for x in clearart if x.get('lang') == self.lang][::-1] + [x for x in clearart if x.get('lang') == 'en'][::-1] + [x for x in clearart if x.get('lang') in ['00', '']][::-1]
            clearart = clearart[0]['url'].encode('utf-8')
        except:
            clearart = '0'

        try:
            if 'moviethumb' in art: landscape = art['moviethumb']
            else: landscape = art['moviebackground']
            landscape = [x for x in landscape if x.get('lang') == 'en'][::-1] + [x for x in landscape if x.get('lang') == '00'][::-1]
            landscape = landscape[0]['url'].encode('utf-8')
        except:
            landscape = '0'

        extended_art = {'extended': True, 'banner': banner, 'poster2': poster2, 'poster3': '0', 'fanart2': fanart2, 'fanart3': '0', 'clearlogo': clearlogo, 'clearart': clearart, 'landscape': landscape}
        try:
            if self.tmdb_key == '': raise Exception()
            art2 = client.request(self.tmdb_art_link % imdb, timeout='30', error=True)
            art2 = json.loads(art2)
        except: return extended_art

        try:
            poster3 = '0'
            poster3 = art2['posters']
            poster3 = [x for x in poster3 if x.get('iso_639_1') == 'en'] + [x for x in poster3 if not x.get('iso_639_1') == 'en']
            poster3 = [(x['width'], x['file_path']) for x in poster3]
            poster3 = [(x[0], x[1]) if x[0] < 300 else ('300', x[1]) for x in poster3]
            poster3 = self.tmdb_img_link % poster3[0]
            poster3 = poster3.encode('utf-8')
        except: return extended_art

        extended_art = {'extended': True, 'banner': banner, 'poster2': poster2, 'poster3': poster3, 'fanart2': fanart2, 'fanart3': '0', 'clearlogo': clearlogo, 'clearart': clearart, 'landscape': landscape}
        try:
            fanart3 = '0'
            fanart3 = art2['backdrops']
            fanart3 = [x for x in fanart3 if x.get('iso_639_1') == 'en'] + [x for x in fanart3 if not x.get('iso_639_1') == 'en']
            fanart3 = [x for x in fanart3 if x.get('width') == 1920] + [x for x in fanart3 if x.get('width') < 1920] + [x for x in fanart3 if x.get('width') <= 3840]
            fanart3 = [(x['width'], x['file_path']) for x in fanart3]
            fanart3 = [(x[0], x[1]) if x[0] < 1280 else ('1280', x[1]) for x in fanart3]
            fanart3 = self.tmdb_img_link % fanart3[0]
            fanart3 = fanart3.encode('utf-8')
        except: return extended_art

        extended_art = {'extended': True, 'banner': banner, 'poster2': poster2, 'poster3': poster3, 'fanart2': fanart2, 'fanart3': fanart3, 'clearlogo': clearlogo, 'clearart': clearart, 'landscape': landscape}

        return extended_art


class tvshows:
    def __init__(self):
        self.list = []

        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))

        self.lang = control.apiLanguage()['tvdb']

        self.tmdb_lang = 'en'
        self.tmdb_key = control.setting('tm.user')
        if self.tmdb_key == '' or self.tmdb_key == None:
            self.tmdb_key = '3320855e65a9758297fec4f7c9717698'
        self.tmdb_poster = 'http://image.tmdb.org/t/p/w500'
        self.tmdb_image = 'http://image.tmdb.org/t/p/original'
        self.tmdb_info_link = 'http://api.themoviedb.org/3/tv/%s?api_key=%s&language=%s&append_to_response=credits,releases,external_ids' % ('%s', self.tmdb_key, self.tmdb_lang)

        self.fanart_tv_user = control.setting('fanart.tv.user')
        if self.fanart_tv_user == '' or self.fanart_tv_user == None:
            self.fanart_tv_user = 'cf0ebcc2f7b824bd04cf3a318f15c17d'
        self.user = self.fanart_tv_user + str('')
        self.fanart_tv_art_link = 'http://webservice.fanart.tv/v3/tv/%s'

        # self.tvdb_key = control.setting('tvdb.user')
        # if self.tvdb_key == '' or self.tvdb_key == None:
            # self.tvdb_key = '1D62F2F90030C444'
        # self.tvdb_key = 'MUQ2MkYyRjkwMDMwQzQ0NA=='
        # self.tvdb_image = 'http://thetvdb.com/banners/'

        self.omdb_key = control.setting('omdb.key')
        if self.omdb_key == '' or self.omdb_key == None:
            self.omdb_key = 'd4daa2b'
        self.imdb_by_query = 'http://www.omdbapi.com/?i=%s&apikey=%s' % ("%s", self.omdb_key)


    def get_request(self, url):
        try:
            try:
                response = requests.get(url)
            except requests.exceptions.SSLError:
                response = requests.get(url, verify=False)
        except requests.exceptions.ConnectionError:
            control.notification(title='default', message=32028, icon='INFO')
            return

        if '200' in str(response):
            return json.loads(response.text)
        elif 'Retry-After' in response.headers:
            # API REQUESTS ARE BEING THROTTLED, INTRODUCE WAIT TIME
            throttleTime = response.headers['Retry-After']
            log_utils.log2('TMDB Throttling Applied, Sleeping for %s seconds' % throttleTime, '')
            sleep(int(throttleTime) + 1)
            return self.get_request(url)
        else:
            log_utils.log2('Get request failed to TMDB URL: %s' % url, 'error')
            log_utils.log2('TMDB Response: %s' % response.text, 'error')
            return None


    def tmdb_list(self, url):
        next = url
        try:
            result = self.get_request(url % self.tmdb_key)
            # result = client.request(url % self.tmdb_key)
            # result = json.loads(result)
            items = result['results']
        except:
            return

        # try:
            # page = int(result['page'])
            # total = int(result['total_pages'])
            # if page >= total: raise Exception()
            # url2 = '%s&page=%s' % (url.split('&page=', 1)[0], str(page+1))
            # result = client.request(url2 % self.tmdb_key)
            # result = json.loads(result)
            # items += result['results']
        # except: pass
        try:
            page = int(result['page'])
            total = int(result['total_pages'])
            if page >= total: raise Exception()
            if not 'page=' in url: raise Exception()
            next = '%s&page=%s' % (next.split('&page=', 1)[0], str(page+1))
            next = next.encode('utf-8')
        except: next = ''

        for item in items:
            try:
                title = item['name']
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = item['first_air_date']
                year = re.compile('(\d{4})').findall(year)[-1]
                year = year.encode('utf-8')

                tmdb = item['id']
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

                poster = item['poster_path']
                if poster == '' or poster == None: poster = '0'
                if not poster == '0': poster = '%s%s' % (self.tmdb_poster, poster)
                poster = poster.encode('utf-8')

                fanart = item['backdrop_path']
                if fanart == '' or fanart == None: fanart = '0'
                if not fanart == '0': fanart = '%s%s' % (self.tmdb_image, fanart)
                fanart = fanart.encode('utf-8')

                # bannner = item['banner_path']
                # if banner == '' or banner == None: banner = '0'
                # if not banner == '0': banner = self.tmdb_image + banner
                # banner = banner.encode('utf-8')

                premiered = item['first_air_date']
                try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')

                rating = str(item['vote_average'])
                if rating == '' or rating == None: rating = '0'
                rating = rating.encode('utf-8')

                votes = str(item['vote_count'])
                try: votes = str(format(int(votes),',d'))
                except: pass
                if votes == '' or votes == None: votes = '0'
                votes = votes.encode('utf-8')

                plot = item['overview']
                if plot == '' or plot == None: plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                try: tagline = tagline.encode('utf-8')
                except: tagline = 'NA'


##--TMDb additional info
                url = self.tmdb_info_link % tmdb
                item = client.request(url, timeout='30')
                item = json.loads(item)

                tvdb = item['external_ids']['tvdb_id']
                if tvdb == '' or tvdb == None: tvdb = '0'
                tvdb = re.sub('[^0-9]', '', str(tvdb))
                tvdb = tvdb.encode('utf-8')

                imdb = item['external_ids']['imdb_id']
                if imdb == '' or imdb == None: imdb = '0'
                imdb = imdb.encode('utf-8')
                if not imdb == '0': url = self.imdb_by_query % imdb

                genre = item['genres']
                try: genre = [x['name'] for x in genre]
                except: genre = '0'
                genre = ' / '.join(genre)
                genre = genre.encode('utf-8')
                if not genre: genre = 'NA'

                studio = item['networks']
                try: studio = [x['name'] for x in studio][0]
                except: studio = '0'
                if studio == '' or studio == None: studio = '0'
                studio = studio.encode('utf-8')

                cast = item['credits']['cast']
                try: cast = [(x['name'].encode('utf-8'), x['character'].encode('utf-8')) for x in cast]
                except: cast = []

                duration = str(item['episode_run_time'][0])
                try: duration = duration.strip("[]")
                except: duration = '0'
                duration = duration.encode('utf-8')

                director = item['credits']['crew']
                try: director = [x['name'] for x in director if x['job'].encode('utf-8') == 'Director']
                except: director = '0'
                if director == '' or director == None or director == []: director = '0'
                director = ' / '.join(director)
                director = director.encode('utf-8')

##--IMDb additional info
                url = self.imdb_by_query % imdb

                item2 = client.request(url, timeout='30')
                item2 = json.loads(item2)

                mpaa = item2['Rated']
                if mpaa == None or mpaa == '' or mpaa == 'N/A' or mpaa == 'NA': mpaa = '0'
                mpaa = mpaa.encode('utf-8')

                writer = item2['Writer']
                if writer == None or writer == '' or writer == 'N/A' or writer == 'NA': writer = '0'
                writer = writer.replace(', ', ' / ')
                writer = re.sub(r'\(.*?\)', '', writer)
                writer = ' '.join(writer.split())
                writer = writer.encode('utf-8')

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline, 'code': imdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'poster': poster, 'banner': '0', 'fanart': fanart, 'next': next})

                meta = {'tmdb': tmdb, 'imdb': imdb, 'tvdb': tvdb, 'lang': self.lang, 'user': self.user, 'item': self.list}
                self.meta.append(meta)
                # metacache.insert(self.meta)
            except:
                pass
        return self.list


    def worker(self, list):
        self.list = list
        try:
            if self.list == None or self.list == []: return
            self.meta = []
            total = len(self.list)
            maximum = total + 10

            self.fanart_tv_headers = {'api-key': '9f846e7ec1ea94fad5d8a431d1d26b43'}
            if not self.fanart_tv_user == '': self.fanart_tv_headers.update({'client-key': self.fanart_tv_user})

            for i in range(0, total): self.list[i].update({'metacache': False})
            self.list = metacache.fetch(self.list, self.lang, self.user)

            imdb = []
            threads = []

            # for i in range(total):
                # threads = [x for x in threads if x.is_alive()]
                # while len(threads) >= maximum:
                    # control.sleep(0.5)
                    # threads = [x for x in threads if x.is_alive()]
                # if not self.list[i]['imdb'] in imdb: # Otherwise data is retrieved multiple times if different episodes of the same show are in the list.
                    # imdb.append(self.list[i]['imdb'])
                    # thread = workers.Thread(self.super_info, i)
                    # thread.start()
                    # threads.append(thread)
            # [x.join() for x in threads]

            for r in range(0, total, 100):
                threads = []
                for i in range(r, r+100):
                    if i <= total: threads.append(workers.Thread(self.super_info, i))
                [i.start() for i in threads]
                [i.join() for i in threads]

            if self.meta: metacache.insert(self.meta)

            self.list = [i for i in self.list]
            # self.list = [i for i in self.list if not i['tvdb'] == '0']
            if self.fanart_tv_user == '':
                for i in self.list: i.update({'clearlogo': '0', 'clearart': '0'})
        except:
            tools.Logger.error()
        # return self.list

    def super_info(self, i):
        try:
            title = self.list[i]['title']

            tvdb = self.list[i]['tvdb']
            try:
                artmeta = True
                art = client.request(self.fanart_tv_art_link % tvdb, headers=self.fanart_tv_headers, timeout='30', error=True)

                try: art = json.loads(art)
                except: artmeta = False
            except:
                pass

            try:
                poster2 = art['tvposter']
                poster2 = [x for x in poster2 if x.get('lang') == 'en'][::-1] + [x for x in poster2 if x.get('lang') == '00'][::-1]
                poster2 = poster2[0]['url'].encode('utf-8')
            except:
                poster2 = '0'

            try:
                fanart2 = art['showbackground']
                fanart2 = [x for x in fanart2 if x.get('lang') == 'en'][::-1] + [x for x in fanart2 if x.get('lang') == '00'][::-1]
                fanart2 = fanart2[0]['url'].encode('utf-8')
            except:
                fanart2 = '0'

            try:
                banner2 = art['tvbanner']
                banner2 = [x for x in banner2 if x.get('lang') == 'en'][::-1] + [x for x in banner2 if x.get('lang') == '00'][::-1]
                banner2 = banner2[0]['url'].encode('utf-8')
            except:
                banner2 = '0'

            try:
                if 'hdtvlogo' in art: clearlogo = art['hdtvlogo']
                else: clearlogo = art['clearlogo']
                clearlogo = [x for x in clearlogo if x.get('lang') == 'en'][::-1] + [x for x in clearlogo if x.get('lang') == '00'][::-1]
                clearlogo = clearlogo[0]['url'].encode('utf-8')
            except:
                clearlogo = '0'

            try:
                if 'hdclearart' in art: clearart = art['hdclearart']
                else: clearart = art['clearart']
                clearart = [x for x in clearart if x.get('lang') == 'en'][::-1] + [x for x in clearart if x.get('lang') == '00'][::-1]
                clearart = clearart[0]['url'].encode('utf-8')
            except:
                clearart = '0'

            try:
                if 'tvthumb' in art: landscape = art['tvthumb']
                else: landscape = art['showbackground']
                landscape = [x for x in landscape if x.get('lang') == 'en'][::-1] + [x for x in landscape if x.get('lang') == '00'][::-1]
                landscape = landscape[0]['url'].encode('utf-8')
            except:
                landscape = '0'

            item = {'extended': True, 'title': title, 'poster2': poster2, 'banner': '0', 'banner2': banner2, 'fanart2': fanart2, 'clearlogo': clearlogo, 'clearart': clearart, 'landscape': landscape}
            item = dict((k,v) for k, v in item.iteritems() if not v == '0')
            self.list[i].update(item)

            if artmeta == False: raise Exception()

            meta = {'item': item}
            self.meta.append(meta)
        except:
            pass

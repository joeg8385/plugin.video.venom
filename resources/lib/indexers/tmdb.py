# -*- coding: utf-8 -*-

'''
Venom
'''

import os,sys,re,datetime
import json,urlparse,requests,xbmc

from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import metacache
from resources.lib.modules import workers
from resources.lib.modules import log_utils

# from resources.lib.modules import trakt


class movies:
    def __init__(self):
        self.list = []
        self.meta = []

        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))

        self.lang = control.apiLanguage()['trakt']

        self.tmdb_key = control.setting('tm.user')
        if self.tmdb_key == '' or self.tmdb_key == None:
            self.tmdb_key = '3320855e65a9758297fec4f7c9717698'

        self.tmdb_lang = 'en'
        self.tmdb_link = 'http://api.themoviedb.org'
        self.tmdb_image = 'http://image.tmdb.org/t/p/original'
        self.tmdb_poster = 'http://image.tmdb.org/t/p/w500'
        # self.tmdb_api_link = 'http://api.themoviedb.org/3/list/%s?api_key=%s' % ('%s', '%s')
        self.tmdb_info_link = 'http://api.themoviedb.org/3/movie/%s?api_key=%s&language=%s&append_to_response=credits,release_dates,external_ids' % ('%s', self.tmdb_key, self.tmdb_lang)
###                                                                                  other "append_to_response" options                                           alternative_titles,videos,images
        self.tmdb_art_link = 'http://api.themoviedb.org/3/movie/%s/images?api_key=' + self.tmdb_key
        # self.tmdb_img_link = 'http://image.tmdb.org/t/p/w%s%s'

        self.fanart_tv_user = control.setting('fanart.tv.user')
        if self.fanart_tv_user == '' or self.fanart_tv_user == None:
            self.fanart_tv_user = 'cf0ebcc2f7b824bd04cf3a318f15c17d'
        self.user = str(self.fanart_tv_user) + str(self.tmdb_key)
        self.fanart_tv_art_link = 'http://webservice.fanart.tv/v3/movies/%s'

        self.omdb_key = control.setting('omdb.key')
        if self.omdb_key == '' or self.omdb_key == None:
            self.omdb_key = 'd4daa2b'
        self.imdbinfo = 'http://www.omdbapi.com/?i=%s&apikey=%s&plot=short&r=json' % ('%s', self.omdb_key)


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
            items = result['results']
        except:
            return

        # try:
            # page = int(result['page'])
            # total = int(result['total_pages'])
            # if page >= total: raise Exception()
            # url2 = '%s&page=%s' % (url.split('&page=', 1)[0], str(page+1))
            # result = self.get_request(url2 % self.tmdb_key)
            # # result = client.request(url2 % self.tmdb_key)
            # # result = json.loads(result)
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

                try: 
                    originaltitle = item['original_title']
                    originaltitle = client.replaceHTMLCodes(title)
                    originaltitle = title.encode('utf-8')
                except: originaltitle = title

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
                item = self.get_request(url)

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

                mpaa = item['release_dates']['results']
                mpaa = [i for i in mpaa if i['iso_3166_1'] == 'US']
                try:
                    mpaa = mpaa[0].get('release_dates')[-1].get('certification')
                    if not mpaa:
                        mpaa = mpaa[0].get('release_dates')[0].get('certification')
                        if not mpaa:
                            mpaa = mpaa[0].get('release_dates')[1].get('certification')
                    mpaa = str(mpaa).encode('utf-8')
                except: mpaa = '0'

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

                try:
                    if not imdb == None or not imdb == '0':
                        url = self.imdbinfo % imdb
                        item = client.request(url, timeout='30')
                        item = json.loads(item)
                        plot2 = item['Plot']
                        plot2 = client.replaceHTMLCodes(plot2)
                        plot2 = plot.encode('utf-8')
                        if plot == '0' or plot == '' or plot == None: plot = plot2

                        rating2 = str(item['imdbRating'])
                        rating2 = rating2.encode('utf-8')
                        if rating == '0' or rating == '' or rating == None: rating = rating2

                        votes2 = str(item['imdbVotes'])
                        votes2 = str(format(int(votes2),',d'))
                        votes2 = votes2.encode('utf-8')
                        if votes == '0' or votes == '' or votes == None: votes = votes2
                except:
                    pass

                item = {}
                item = {'content': 'movie', 'title': title, 'originaltitle': originaltitle, 'year': year, 'premiered': premiered, 'studio': '0', 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline,
                        'code': tmdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'poster': poster, 'poster2': '0', 'poster3': '0', 'banner': '0', 'fanart': fanart, 'fanart2': '0', 'fanart3': '0', 'clearlogo': '0', 'clearart': '0', 'landscape': '0', 'metacache': False, 'next': next}
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
            result = self.get_request(url)
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
                year = re.compile('(\d{4})').findall(year)[0]
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

                try:
                    tagline = item['tagline']
                    if tagline == '' or tagline == '0' or tagline == None:
                        tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                    tagline = tagline.encode('utf-8')
                except: tagline = '0'


##--TMDb additional info
                url = self.tmdb_info_link % tmdb
                item = self.get_request(url)

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

                mpaa = item['release_dates']['results']
                mpaa = [i for i in mpaa if i['iso_3166_1'] == 'US']
                try:
                    mpaa = mpaa[0].get('release_dates')[-1].get('certification')
                    if not mpaa:
                        mpaa = mpaa[0].get('release_dates')[0].get('certification')
                        if not mpaa:
                            mpaa = mpaa[0].get('release_dates')[1].get('certification')
                    mpaa = str(mpaa).encode('utf-8')
                except: mpaa = '0'

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

                try:
                    if not imdb == None or not imdb == '0':
                        url = self.imdbinfo % imdb
                        item = client.request(url, timeout='30')
                        item = json.loads(item)
                        plot2 = item['Plot']
                        plot2 = client.replaceHTMLCodes(plot2)
                        plot2 = plot.encode('utf-8')
                        if plot == '0' or plot == '' or plot == None: plot = plot2

                        rating2 = str(item['imdbRating'])
                        rating2 = rating2.encode('utf-8')
                        if rating == '0' or rating == '' or rating == None: rating = rating2

                        votes2 = str(item['imdbVotes'])
                        votes2 = str(format(int(votes2),',d'))
                        votes2 = votes2.encode('utf-8')
                        if votes == '0' or votes == '' or votes == None: votes = votes2
                except:
                    pass

                item = {}
                item = {'content': 'movie', 'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': '0', 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline,
                        'code': tmdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'poster': poster, 'poster2': '0', 'poster3': '0', 'banner': '0', 'fanart': fanart, 'fanart2': '0', 'fanart3': '0', 'clearlogo': '0', 'clearart': '0', 'landscape': '0', 'metacache': False, 'next': next}
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


    def extended_art(self, imdb):
        self.fanart_tv_headers = {'api-key': '9f846e7ec1ea94fad5d8a431d1d26b43'}
        if not self.fanart_tv_user == '': self.fanart_tv_headers.update({'client-key': self.fanart_tv_user})
###--Fanart.tv artwork
        try:
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
                poster2 = [(x['url'], x['likes']) for x in poster2 if x.get('lang') == self.lang] + [(x['url'], x['likes']) for x in poster2 if x.get('lang') == '']
                poster2 = [(x[0], x[1]) for x in poster2]
                poster2 = sorted(poster2, key=lambda x: int(x[1]), reverse=True)
                poster2 = [x[0] for x in poster2][0]
                poster2 = poster2.encode('utf-8')
            except:
                poster2 = '0'

            try:
                if 'moviebackground' in art: fanart2 = art['moviebackground']
                else: fanart2 = art['moviethumb']
                fanart2 = [(x['url'], x['likes']) for x in fanart2 if x.get('lang') == self.lang] + [(x['url'], x['likes']) for x in fanart2 if x.get('lang') == '']
                fanart2 = [(x[0], x[1]) for x in fanart2]
                fanart2 = sorted(fanart2, key=lambda x: int(x[1]), reverse=True)
                fanart2 = [x[0] for x in fanart2][0]
                fanart2 = fanart2.encode('utf-8')
            except:
                fanart2 = '0'

            try:
                banner = art['moviebanner']
                banner = [(x['url'], x['likes']) for x in banner if x.get('lang') == self.lang] + [(x['url'], x['likes']) for x in banner if x.get('lang') == '']
                banner = [(x[0], x[1]) for x in banner]
                banner = sorted(banner, key=lambda x: int(x[1]), reverse=True)
                banner = [x[0] for x in banner][0]
                banner = banner.encode('utf-8')
            except:
                banner = '0'

            try:
                if 'hdmovielogo' in art: clearlogo = art['hdmovielogo']
                else: clearlogo = art['movielogo']
                clearlogo = [(x['url'], x['likes']) for x in clearlogo if x.get('lang') == self.lang] + [(x['url'], x['likes']) for x in clearlogo if x.get('lang') == '']
                clearlogo = [(x[0], x[1]) for x in clearlogo]
                clearlogo = sorted(clearlogo, key=lambda x: int(x[1]), reverse=True)
                clearlogo = [x[0] for x in clearlogo][0]
                clearlogo = clearlogo.encode('utf-8')
            except:
                clearlogo = '0'

            try:
                if 'hdmovieclearart' in art: clearart = art['hdmovieclearart']
                else: clearart = art['movieart']
                clearart = [(x['url'], x['likes']) for x in clearart if x.get('lang') == self.lang] + [(x['url'], x['likes']) for x in clearart if x.get('lang') == '']
                clearart = [(x[0], x[1]) for x in clearart]
                clearart = sorted(clearart, key=lambda x: int(x[1]), reverse=True)
                clearart = [x[0] for x in clearart][0]
                clearart = clearart.encode('utf-8')
            except:
                clearart = '0'

            try:
                discart = art['moviedisc']
                discart = [(x['url'], x['likes']) for x in discart if x.get('lang') == self.lang] + [(x['url'], x['likes']) for x in discart if x.get('lang') == '']
                discart = [(x[0], x[1]) for x in discart]
                discart = sorted(discart, key=lambda x: int(x[1]), reverse=True)
                discart = [x[0] for x in discart][0]
                discart = discart.encode('utf-8')
            except:
                discart = '0'

            try:
                if 'moviethumb' in art: landscape = art['moviethumb']
                else: landscape = art['moviebackground']
                landscape = [(x['url'], x['likes']) for x in landscape if x.get('lang') == self.lang] + [(x['url'], x['likes']) for x in landscape if x.get('lang') == '']
                landscape = [(x[0], x[1]) for x in landscape]
                landscape = sorted(landscape, key=lambda x: int(x[1]), reverse=True)
                landscape = [x[0] for x in landscape][0]
                landscape = landscape.encode('utf-8')
            except:
                landscape = '0'

            extended_art = {'extended': True, 'banner': banner, 'poster2': poster2, 'poster3': '0', 'fanart2': fanart2, 'fanart3': '0', 'clearlogo': clearlogo, 'clearart': clearart, 'discart': discart, 'landscape': landscape}

# ###--TMDb artwork
            # try:
                # if self.tmdb_key == '': raise Exception()
                # art2 = client.request(self.tmdb_art_link % imdb, timeout='30', error=True)
                # art2 = json.loads(art2)
            # except: return extended_art

            # try:
                # poster3 = '0'
                # poster3 = art2['posters']
                # poster3 = [x for x in poster3 if x.get('iso_639_1') == 'en'] + [x for x in poster3 if not x.get('iso_639_1') == 'en']
                # poster3 = [(x['width'], x['file_path']) for x in poster3]
                # poster3 = [(x[0], x[1]) if x[0] <= 500 else ('500', x[1]) for x in poster3]
                # poster3 = self.tmdb_img_link % poster3[0]
                # poster3 = poster3.encode('utf-8')
            # except: return extended_art

            # extended_art = {'extended': True, 'banner': banner, 'poster2': poster2, 'poster3': poster3, 'fanart2': fanart2, 'fanart3': '0', 'clearlogo': clearlogo, 'clearart': clearart, 'discart': discart, 'landscape': landscape}
            # try:
                # fanart3 = '0'
                # fanart3 = art2['backdrops']
                # fanart3 = [x for x in fanart3 if x.get('iso_639_1') == 'en'] + [x for x in fanart3 if not x.get('iso_639_1') == 'en']
                # fanart3 = [x for x in fanart3 if x.get('width') == 1920] + [x for x in fanart3 if x.get('width') < 1920] + [x for x in fanart3 if x.get('width') <= 3840]
                # fanart3 = [(x['width'], x['file_path']) for x in fanart3]
                # fanart3 = [(x[0], x[1]) if x[0] <= 1280 else ('1280', x[1]) for x in fanart3]
                # fanart3 = self.tmdb_img_link % fanart3[0]
                # fanart3 = fanart3.encode('utf-8')
            # except: return extended_art
            # extended_art = {'extended': True, 'banner': banner, 'poster2': poster2, 'poster3': poster3, 'fanart2': fanart2, 'fanart3': fanart3, 'clearlogo': clearlogo, 'clearart': clearart, 'discart': discart, 'landscape': landscape}

            return extended_art
        except:
            return None


class tvshows:
    def __init__(self):
        self.list = []
        self.meta = []

        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))

        self.lang = control.apiLanguage()['tvdb']

        self.tmdb_key = control.setting('tm.user')
        if self.tmdb_key == '' or self.tmdb_key == None:
            self.tmdb_key = '3320855e65a9758297fec4f7c9717698'

        self.tmdb_lang = 'en-US'
        self.tmdb_poster = 'http://image.tmdb.org/t/p/w500'
        self.tmdb_image = 'http://image.tmdb.org/t/p/original'
        self.tmdb_info_link = 'http://api.themoviedb.org/3/tv/%s?api_key=%s&language=%s&append_to_response=credits,content_ratings,external_ids' % ('%s', self.tmdb_key, self.tmdb_lang)
###                                                                                  other "append_to_response" options                                           alternative_titles,videos,images

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
        self.imdb_by_query = 'http://www.omdbapi.com/?i=%s&apikey=%s' % ('%s', self.omdb_key)


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
            items = result['results']
        except:
            return

        # try:
            # page = int(result['page'])
            # total = int(result['total_pages'])
            # if page >= total: raise Exception()
            # url2 = '%s&page=%s' % (url.split('&page=', 1)[0], str(page+1))
            # result = self.get_request(url2 % self.tmdb_key)
            # # result = client.request(url2 % self.tmdb_key)
            # # result = json.loads(result)
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
                item = self.get_request(url)


                tvdb = item['external_ids']['tvdb_id']
                if tvdb == '' or tvdb == None or tvdb == 'N/A' or tvdb == 'NA': tvdb = '0'
                tvdb = re.sub('[^0-9]', '', str(tvdb))
                tvdb = tvdb.encode('utf-8')

                imdb = item['external_ids']['imdb_id']
                if imdb == '' or imdb == None or imdb == 'N/A' or imdb == 'NA': imdb = '0'
                imdb = imdb.encode('utf-8')

                genre = item['genres']
                try: genre = [x['name'] for x in genre]
                except: genre = '0'
                genre = ' / '.join(genre)
                genre = genre.encode('utf-8')
                if not genre: genre = 'NA'

                duration = str(item['episode_run_time'][0])
                try: duration = duration.strip("[]")
                except: duration = '0'
                duration = duration.encode('utf-8')

                try:
                    mpaa = [i['rating'] for i in item['content_ratings']['results'] if i['iso_3166_1'] == 'US'][0]
                except: 
                    try:
                        mpaa = item['content_ratings'][0]['rating']
                    except: mpaa = 'NR'

                studio = item['networks']
                try: studio = [x['name'] for x in studio][0]
                except: studio = '0'
                if studio == '' or studio == None: studio = '0'
                studio = studio.encode('utf-8')

                director = item['credits']['crew']
                try: director = [x['name'] for x in director if x['job'].encode('utf-8') == 'Director']
                except: director = '0'
                if director == '' or director == None or director == []: director = '0'
                director = ' / '.join(director)
                director = director.encode('utf-8')

                cast = item['credits']['cast']
                try: cast = [(x['name'].encode('utf-8'), x['character'].encode('utf-8')) for x in cast]
                except: cast = []


# ##--IMDb additional info
                if not imdb == '0' or None:
                    try:
                        url = self.imdb_by_query % imdb
                        item2 = client.request(url, timeout='30')
                        item2 = json.loads(item2)
                    except: Exception()

                    try:
                        mpaa2 = item2['Rated']
                    except: mpaa2 = 'NR'
                    mpaa2 = mpaa.encode('utf-8')
                    if mpaa == '0' or mpaa == 'NR' and not mpaa2 == 'NR': mpaa = mpaa2

                    try:
                        writer = item2['Writer']
                    except: writer = 'NA'
                    writer = writer.replace(', ', ' / ')
                    writer = re.sub(r'\(.*?\)', '', writer)
                    writer = ' '.join(writer.split())
                    writer = writer.encode('utf-8')

                item = {}
                item = {'content': 'tvshow', 'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline,
                        'code': tmdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'poster': poster, 'poster2': '0', 'banner': '0', 'banner2': '0', 'fanart': fanart, 'fanart2': '0', 'clearlogo': '0', 'clearart': '0', 'landscape': '0', 'metacache': False, 'next': next}

                meta = {}
                meta = {'tmdb': tmdb, 'imdb': imdb, 'tvdb': tvdb, 'lang': self.lang, 'user': self.user, 'item': item}

                extended_art = self.extended_art(tvdb)
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
        result = self.get_request(url)
        items = result['items']
        next = ''
        for item in items:
            try:
                title = item['name']
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = item['first_air_date']
                year = re.compile('(\d{4})').findall(year)[-1]
                year = year.encode('utf-8')

                tmdb = item['id']
                if tmdb == '' or tmdb == None: tmdb = '0'
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

                imdb = '0'
                tvdb = '0'

                poster = item['poster_path']
                if poster == '' or poster == None: poster = '0'
                else: poster = self.tmdb_poster + poster
                poster = poster.encode('utf-8')

                fanart = item['backdrop_path']
                if fanart == '' or fanart == None: fanart = '0'
                if not fanart == '0': fanart = '%s%s' % (self.tmdb_image, fanart)
                fanart = fanart.encode('utf-8')

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

                try:
                    tagline = item['tagline']
                    if tagline == '' or tagline == '0' or tagline == None:
                        tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                    tagline = tagline.encode('utf-8')
                except: tagline = '0'

##--TMDb additional info
                url = self.tmdb_info_link % tmdb
                item = self.get_request(url)

                tvdb = item['external_ids']['tvdb_id']
                if tvdb == '' or tvdb == None or tvdb == 'N/A' or tvdb == 'NA': tvdb = '0'
                tvdb = re.sub('[^0-9]', '', str(tvdb))
                tvdb = tvdb.encode('utf-8')

                imdb = item['external_ids']['imdb_id']
                if imdb == '' or imdb == None or imdb == 'N/A' or imdb == 'NA': imdb = '0'
                imdb = imdb.encode('utf-8')

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

                try:
                    mpaa = [i['rating'] for i in item['content_ratings']['results'] if i['iso_3166_1'] == 'US'][0]
                except: 
                    try:
                        mpaa = item['content_ratings'][0]['rating']
                    except: mpaa = 'NR'

                # studio = item['production_companies']
                # try: studio = [x['name'] for x in studio][0]
                # except: studio = '0'
                # if studio == '' or studio == None: studio = '0'
                # studio = studio.encode('utf-8')

                studio = item['networks']
                try: studio = [x['name'] for x in studio][0]
                except: studio = '0'
                if studio == '' or studio == None: studio = '0'
                studio = studio.encode('utf-8')

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

                try:
                    if not imdb == None or imdb == '0':
                        url = self.imdbinfo % imdb
                        item = client.request(url, timeout='30')
                        item = json.loads(item)
                        plot2 = item['Plot']
                        plot2 = client.replaceHTMLCodes(plot2)
                        plot2 = plot.encode('utf-8')
                        if plot == '0' or plot == '' or plot == None: plot = plot2

                        rating2 = str(item['imdbRating'])
                        rating2 = rating2.encode('utf-8')
                        if rating == '0' or rating == '' or rating == None: rating = rating2

                        votes2 = str(item['imdbVotes'])
                        votes2 = str(format(int(votes2),',d'))
                        votes2 = votes2.encode('utf-8')
                        if votes == '0' or votes == '' or votes == None: votes = votes2
                except:
                    pass

                item = {}
                item = {'content': 'movie', 'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline,
                        'code': tmdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'poster': poster, 'poster2': '0', 'poster3': '0', 'banner': '0', 'fanart': fanart, 'fanart2': '0', 'fanart3': '0', 'clearlogo': '0', 'clearart': '0', 'landscape': '0', 'metacache': False, 'next': next}
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


    def extended_art(self, tvdb):
        self.fanart_tv_headers = {'api-key': '9f846e7ec1ea94fad5d8a431d1d26b43'}
        if not self.fanart_tv_user == '': self.fanart_tv_headers.update({'client-key': self.fanart_tv_user})

        try:
            try:
                art = client.request(self.fanart_tv_art_link % tvdb, headers=self.fanart_tv_headers, timeout='30', error=True)
                art = json.loads(art)
            except: return None

            try:
                poster2 = art['tvposter']
                poster2 = [(x['url'], x['likes']) for x in poster2 if x.get('lang') == self.lang] + [(x['url'], x['likes']) for x in poster2 if x.get('lang') == '']
                poster2 = [(x[0], x[1]) for x in poster2]
                poster2 = sorted(poster2, key=lambda x: int(x[1]), reverse=True)
                poster2 = [x[0] for x in poster2][0]
                poster2 = poster2.encode('utf-8')
            except:
                poster2 = '0'

            try:
                fanart2 = art['showbackground']
                fanart2 = [(x['url'], x['likes']) for x in fanart2 if x.get('lang') == self.lang] + [(x['url'], x['likes']) for x in fanart2 if x.get('lang') == '']
                fanart2 = [(x[0], x[1]) for x in fanart2]
                fanart2 = sorted(fanart2, key=lambda x: int(x[1]), reverse=True)
                fanart2 = [x[0] for x in fanart2][0]
                fanart2 = fanart2.encode('utf-8')
            except:
                fanart = '0'

            try:
                banner2 = art['tvbanner']
                banner2 = [(x['url'], x['likes']) for x in banner2 if x.get('lang') == self.lang] + [(x['url'], x['likes']) for x in banner2 if x.get('lang') == '']
                banner2 = [(x[0], x[1]) for x in banner2]
                banner2 = sorted(banner2, key=lambda x: int(x[1]), reverse=True)
                banner2 = [x[0] for x in banner2][0]
                banner2 = banner2.encode('utf-8')
            except:
                banner = '0'

            try:
                if 'hdtvlogo' in art: clearlogo = art['hdtvlogo']
                else: clearlogo = art['clearlogo']
                clearlogo = [(x['url'], x['likes']) for x in clearlogo if x.get('lang') == self.lang] + [(x['url'], x['likes']) for x in clearlogo if x.get('lang') == '']
                clearlogo = [(x[0], x[1]) for x in clearlogo]
                clearlogo = sorted(clearlogo, key=lambda x: int(x[1]), reverse=True)
                clearlogo = [x[0] for x in clearlogo][0]
                clearlogo = clearlogo.encode('utf-8')
            except:
                clearlogo = '0'

            try:
                if 'hdclearart' in art: clearart = art['hdclearart']
                else: clearart = art['clearart']
                clearart = [(x['url'], x['likes']) for x in clearart if x.get('lang') == self.lang] + [(x['url'], x['likes']) for x in clearart if x.get('lang') == '']
                clearart = [(x[0], x[1]) for x in clearart]
                clearart = sorted(clearart, key=lambda x: int(x[1]), reverse=True)
                clearart = [x[0] for x in clearart][0]
                clearart = clearart.encode('utf-8')
            except:
                clearart = '0'

            try:
                if 'tvthumb' in art: landscape = art['tvthumb']
                else: landscape = art['showbackground']
                landscape = [(x['url'], x['likes']) for x in landscape if x.get('lang') == self.lang] + [(x['url'], x['likes']) for x in landscape if x.get('lang') == '']
                landscape = [(x[0], x[1]) for x in landscape]
                landscape = sorted(landscape, key=lambda x: int(x[1]), reverse=True)
                landscape = [x[0] for x in landscape][0]
                landscape = landscape.encode('utf-8')
            except:
                landscape = '0'

            extended_art = {'extended': True, 'poster2': poster2, 'banner2': banner2, 'fanart2': fanart2, 'clearlogo': clearlogo, 'clearart': clearart, 'landscape': landscape}

            return extended_art
        except:
            return None

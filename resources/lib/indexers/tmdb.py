# -*- coding: utf-8 -*-

'''
Venom
'''

import re, datetime
import json, requests, xbmc

from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import metacache
from resources.lib.modules import log_utils
# from resources.lib.modules import trakt


class Movies:
    def __init__(self):
        self.list = []
        self.meta = []

        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))

        self.lang = control.apiLanguage()['trakt']

        self.tmdb_key = control.setting('tm.user')
        if self.tmdb_key == '' or self.tmdb_key is None:
            self.tmdb_key = '3320855e65a9758297fec4f7c9717698'

        self.tmdb_link = 'http://api.themoviedb.org'
        # self.tmdb_poster = 'http://image.tmdb.org/t/p/w500'
        self.tmdb_poster = 'http://image.tmdb.org/t/p/w300'
        # self.tmdb_fanart = 'http://image.tmdb.org/t/p/original'
        self.tmdb_fanart = 'http://image.tmdb.org/t/p/w1280'

        self.tmdb_info_link = 'http://api.themoviedb.org/3/movie/%s?api_key=%s&language=%s&append_to_response=credits,release_dates,external_ids' % ('%s', self.tmdb_key, self.lang)
###                                                                                  other "append_to_response" options                                           alternative_titles,videos,images
        self.tmdb_art_link = 'http://api.themoviedb.org/3/movie/%s/images?api_key=%s&include_image_language=en,%s,null' % ('%s', self.tmdb_key, self.lang)

        self.disable_fanarttv = control.setting('disable.fanarttv')


    def get_request(self, url):
        try:
            try:
                response = requests.get(url)
            except requests.exceptions.SSLError:
                response = requests.get(url, verify=False)
        except requests.exceptions.ConnectionError:
            control.notification(title='default', message=32024, icon='INFO')
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
            if not 'page=' in url:
                raise Exception()
            next = '%s&page=%s' % (next.split('&page=', 1)[0], str(page+1))
            next = next.encode('utf-8')
        except:
            next = ''

        for item in items:
            try:
                title = (item.get('title')).encode('utf-8')

                try: 
                    originaltitle = (item.get('original_title')).encode('utf-8')
                except:
                    originaltitle = title

                year = item['release_date']
                year = re.compile('(\d{4})').findall(year)[-1]
                year = year.encode('utf-8')

                tmdb = item['id']
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

                # try:
                    # meta_chk = []
                    # meta_chk.append({'tmdb': tmdb, 'imdb': '0', 'tvdb': '0'})
                    # meta_chk = metacache.fetch(meta_chk, self.lang, self.tmdb_key)
                    # log_utils.log('meta_chk = %s' % str(meta_chk), __name__, log_utils.LOGDEBUG)

                    # for i in meta_chk:
                        # if 'metacache' in i:
                            # if i['metacache'] is True:
                                # item = meta_chk
                                # log_utils.log('metacache = %s' % i['metacache'], __name__, log_utils.LOGDEBUG)
                                # raise Exception()

                poster = item.get('poster_path')
                if not poster == '' and not poster is None:
                    poster = ('%s%s' % (self.tmdb_poster, poster)).encode('utf-8')
                else:
                    poster = '0'
                # log_utils.log('poster = %s' % str(poster), __name__, log_utils.LOGDEBUG)

                fanart = item.get('backdrop_path')
                if not fanart == '' and not fanart is None:
                    fanart = ('%s%s' % (self.tmdb_fanart, fanart)).encode('utf-8')
                else:
                    fanart = '0'
                # log_utils.log('fanart = %s' % str(fanart), __name__, log_utils.LOGDEBUG)

                premiered = item['release_date']
                try:
                    premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except:
                    premiered = '0'
                premiered = premiered.encode('utf-8')

                try:
                    rating = str(item['vote_average']).encode('utf-8')
                except:
                    rating = '0'

                try:
                    votes = str(format(int(item['vote_count']),',d')).encode('utf-8')
                except:
                    votes = '0'

                plot = (item.get('overview')).encode('utf-8')

                try:
                    tagline = item['tagline']
                    tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                    tagline = tagline.encode('utf-8')
                except:
                    tagline = '0'

##--TMDb additional info
                url = self.tmdb_info_link % tmdb
                item = self.get_request(url)

                imdb = item['external_ids']['imdb_id']
                if imdb == '' or imdb is None: imdb = '0'
                imdb = imdb.encode('utf-8')

                # studio = item['production_companies']
                # try: studio = [x['name'] for x in studio][0]
                # except: studio = '0'
                # if studio == '' or studio is None: studio = '0'
                # studio = studio.encode('utf-8')

                try:
                    genre = item['genres']
                    genre = [x['name'] for x in genre]
                    genre = (' / '.join(genre)).encode('utf-8')
                except:
                    genre = 'NA'

                try:
                    duration = (str(item['runtime'])).encode('utf-8')
                except:
                    duration = '0'

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
                try:
                    director = [x['name'] for x in director if x['job'].encode('utf-8') == 'Director']
                except:
                    director = '0'
                if director == '' or director is None or director == []:
                    director = '0'
                director = (' / '.join(director)).encode('utf-8')

                writer = item['credits']['crew']
                try:
                    writer = [x['name'] for x in writer if x['job'].encode('utf-8') in ['Writer', 'Screenplay']]
                except:
                    writer = '0'
                try:
                    writer = [x for n,x in enumerate(writer) if x not in writer[:n]]
                except:
                    writer = '0'
                if writer == '' or writer is None or writer == []:
                    writer = '0'
                writer = (' / '.join(writer)).encode('utf-8')

                cast = item['credits']['cast']
                try:
                    cast = [(x['name'].encode('utf-8'), x['character'].encode('utf-8')) for x in cast]
                except:
                    cast = []

                item = {}
                item = {'content': 'movie', 'title': title, 'originaltitle': originaltitle, 'year': year, 'premiered': premiered, 'studio': '0', 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes,
                                'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline, 'code': tmdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'poster': poster,
                                'poster2': '0', 'poster3': '0', 'banner': '0', 'fanart': fanart, 'fanart2': '0', 'fanart3': '0', 'clearlogo': '0', 'clearart': '0', 'landscape': fanart, 'metacache': False, 'next': next}
                meta = {}
                meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.lang, 'user': self.tmdb_key, 'item': item}

                # fanart_thread = threading.Thread
                if not self.disable_fanarttv == 'true':
                    from resources.lib.indexers import fanarttv
                    extended_art = fanarttv.get_movie_art(imdb, tmdb)
                    if not extended_art is None:
                        item.update(extended_art)
                        meta.update(item)

                self.list.append(item)
                self.meta.append(meta)
                metacache.insert(self.meta)
                # log_utils.log('self.list = %s' % str(self.list), __name__, log_utils.LOGDEBUG)
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

                title = (item.get('title')).encode('utf-8')
                if not media_type == 'movie':
                    title = (item.get('name')).encode('utf-8')

                try: 
                    originaltitle = (item.get('original_title')).encode('utf-8')
                except:
                    originaltitle = title

                year = item['release_date']
                year = re.compile('(\d{4})').findall(year)[0]
                year = year.encode('utf-8')

                tmdb = item['id']
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

                poster = item.get('poster_path')
                if not poster == '' and not poster is None:
                    poster = ('%s%s' % (self.tmdb_poster, poster)).encode('utf-8')
                else:
                    poster = '0'

                fanart = item.get('backdrop_path')
                if not fanart == '' and not fanart is None:
                    fanart = ('%s%s' % (self.tmdb_fanart, fanart)).encode('utf-8')
                else:
                    fanart = '0'

                premiered = item['release_date']
                try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')

                try:
                    rating = str(item['vote_average']).encode('utf-8')
                except: rating = '0'

                try:
                    votes = str(format(int(item['vote_count']),',d')).encode('utf-8')
                except: votes = '0'

                plot = (item.get('overview')).encode('utf-8')

                try:
                    tagline = item['tagline']
                    if tagline == '' or tagline == '0' or tagline is None:
                        tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                    tagline = tagline.encode('utf-8')
                except: tagline = '0'


##--TMDb additional info
                url = self.tmdb_info_link % tmdb
                item = self.get_request(url)

                imdb = item['external_ids']['imdb_id']
                if imdb == '' or imdb is None: imdb = '0'
                imdb = imdb.encode('utf-8')

                # studio = item['production_companies']
                # try: studio = [x['name'] for x in studio][0]
                # except: studio = '0'
                # if studio == '' or studio is None: studio = '0'
                # studio = studio.encode('utf-8')

                genre = item['genres']
                try: genre = [x['name'] for x in genre]
                except: genre = '0'
                genre = ' / '.join(genre)
                genre = genre.encode('utf-8')
                if not genre: genre = 'NA'

                try: duration = str(item['runtime'])
                except: duration = '0'
                if duration == '' or duration is None or duration == 'N/A': duration = '0'
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
                if director == '' or director is None or director == []: director = '0'
                director = ' / '.join(director)
                director = director.encode('utf-8')

                writer = item['credits']['crew']
                try:
                    writer = [x['name'] for x in writer if x['job'].encode('utf-8') in ['Writer', 'Screenplay']]
                except:
                    writer = '0'
                try:
                    writer = [x for n,x in enumerate(writer) if x not in writer[:n]]
                except:
                    writer = '0'
                if writer == '' or writer is None or writer == []:
                    writer = '0'
                writer = ' / '.join(writer)
                writer = writer.encode('utf-8')

                cast = item['credits']['cast']
                try: cast = [(x['name'].encode('utf-8'), x['character'].encode('utf-8')) for x in cast]
                except: cast = []

                item = {}
                item = {'content': 'movie', 'title': title, 'originaltitle': originaltitle, 'year': year, 'premiered': premiered, 'studio': '0', 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes,
                                'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline, 'code': tmdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'poster': poster,
                                'poster2': '0', 'poster3': '0', 'banner': '0', 'fanart': fanart, 'fanart2': '0', 'fanart3': '0', 'clearlogo': '0', 'clearart': '0', 'landscape': '0', 'metacache': False, 'next': next}
                meta = {}
                meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.lang, 'user': self.tmdb_key, 'item': item}

                # fanart_thread = threading.Thread
                if not self.disable_fanarttv == 'true':
                    from resources.lib.indexers import fanarttv
                    extended_art = fanarttv.get_movie_art(imdb, tmdb)
                    if not extended_art is None:
                        item.update(extended_art)
                        meta.update(item)

                self.list.append(item)
                self.meta.append(meta)
                metacache.insert(self.meta)

            except:
                pass
        return self.list


    def tmdb_art(self, tmdb):
        try:
            if self.tmdb_key == '':
                raise Exception()
            art3 = self.get_request(self.tmdb_art_link % tmdb)
        except:
            import traceback
            traceback.print_exc()
            return None

        url = (self.tmdb_art_link % tmdb)

        try:
            poster3 = art3['posters']
            log_utils.log('poster3 = %s' % str(poster3), __name__, log_utils.LOGDEBUG)
            poster3 = [(x['width'], x['file_path']) for x in poster3]
            log_utils.log('poster3 = %s' % str(poster3), __name__, log_utils.LOGDEBUG)
            poster3 = [x[1] for x in poster3]
            log_utils.log('poster3 = %s' % str(poster3), __name__, log_utils.LOGDEBUG)
            poster3 = self.tmdb_poster + poster3[0]
            log_utils.log('poster3 = %s' % str(poster3), __name__, log_utils.LOGDEBUG)
        except:
            poster3 = '0'
            log_utils.log('poster3 = %s' % str(poster3), __name__, log_utils.LOGDEBUG)
        try:
            fanart3 = art3['backdrops']
            fanart3 = [(x['width'], x['file_path']) for x in fanart3]
            fanart3 = [x[1] for x in fanart3]
            fanart3 = self.tmdb_fanart + fanart3[0]
        except:
            fanart3 = '0'

        extended_art = {'extended': True, 'poster3': poster3, 'fanart3': fanart3}
        return extended_art



class TVshows:
    def __init__(self):
        self.list = []
        self.meta = []

        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))

        self.lang = control.apiLanguage()['tvdb']

        self.tmdb_key = control.setting('tm.user')
        if self.tmdb_key == '' or self.tmdb_key is None:
            self.tmdb_key = '3320855e65a9758297fec4f7c9717698'

        self.tmdb_link = 'http://api.themoviedb.org'
        # self.tmdb_poster = 'http://image.tmdb.org/t/p/w500'
        self.tmdb_poster = 'http://image.tmdb.org/t/p/w300'
        # self.tmdb_fanart = 'http://image.tmdb.org/t/p/original'
        self.tmdb_fanart = 'http://image.tmdb.org/t/p/w1280'

        self.tmdb_info_link = 'http://api.themoviedb.org/3/tv/%s?api_key=%s&language=%s&append_to_response=credits,content_ratings,external_ids' % ('%s', self.tmdb_key, self.lang)
###                                                                                  other "append_to_response" options                                           alternative_titles,videos,images

        self.tmdb_art_link = 'http://api.themoviedb.org/3/tv/%s/images?api_key=%s&include_image_language=en,%s,null' % ('%s', self.tmdb_key, self.lang)

        self.disable_fanarttv = control.setting('disable.fanarttv')


    def get_request(self, url):
        try:
            try:
                response = requests.get(url)
            except requests.exceptions.SSLError:
                response = requests.get(url, verify=False)
        except requests.exceptions.ConnectionError:
            control.notification(title='default', message=32024, icon='INFO')
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
        except:
            next = ''

        for item in items:
            try:
                title = (item.get('name')).encode('utf-8')

                year = item['first_air_date']
                year = re.compile('(\d{4})').findall(year)[-1]
                year = year.encode('utf-8')

                tmdb = item['id']
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

                poster = item.get('poster_path')
                if not poster == '' and not poster is None:
                    poster = ('%s%s' % (self.tmdb_poster, poster)).encode('utf-8')
                else:
                    poster = '0'

                fanart = item.get('backdrop_path')
                if not fanart == '' and not fanart is None:
                    fanart = ('%s%s' % (self.tmdb_fanart, fanart)).encode('utf-8')
                else:
                    fanart = '0'

                premiered = item['first_air_date']
                try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')

                rating = str(item['vote_average'])
                if rating == '' or rating is None: rating = '0'
                rating = rating.encode('utf-8')

                votes = str(item['vote_count'])
                try: votes = str(format(int(votes),',d'))
                except: pass
                if votes == '' or votes is None: votes = '0'
                votes = votes.encode('utf-8')

                plot = (item.get('overview')).encode('utf-8')

                tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                try: tagline = tagline.encode('utf-8')
                except: tagline = 'NA'

##--TMDb additional info
                url = self.tmdb_info_link % tmdb
                item = self.get_request(url)

                tvdb = item['external_ids']['tvdb_id']
                if tvdb == '' or tvdb is None or tvdb == 'N/A' or tvdb == 'NA': tvdb = '0'
                tvdb = re.sub('[^0-9]', '', str(tvdb))
                tvdb = tvdb.encode('utf-8')

                imdb = item['external_ids']['imdb_id']
                if imdb == '' or imdb is None or imdb == 'N/A' or imdb == 'NA': imdb = '0'
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
                if studio == '' or studio is None: studio = '0'
                studio = studio.encode('utf-8')

                director = item['credits']['crew']
                try: director = [x['name'] for x in director if x['job'].encode('utf-8') == 'Director']
                except: director = '0'
                if director == '' or director is None or director == []: director = '0'
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
                item = {'content': 'tvshow', 'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes,
                                'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline, 'code': tmdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'poster': poster,
                                'poster2': '0', 'banner': '0', 'banner2': '0', 'fanart': fanart, 'fanart2': '0', 'clearlogo': '0', 'clearart': '0', 'landscape': '0', 'metacache': False, 'next': next}

                meta = {}
                meta = {'tmdb': tmdb, 'imdb': imdb, 'tvdb': tvdb, 'lang': self.lang, 'user': self.tmdb_key, 'item': item}

                # fanart_thread = threading.Thread
                if not self.disable_fanarttv == 'true':
                    from resources.lib.indexers import fanarttv
                    extended_art = fanarttv.get_tvshow_art(tvdb)
                    if not extended_art is None:
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
                title = (item.get('name')).encode('utf-8')

                year = item['first_air_date']
                year = re.compile('(\d{4})').findall(year)[-1]
                year = year.encode('utf-8')

                tmdb = item['id']
                if tmdb == '' or tmdb is None:
                    tmdb = '0'
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

                imdb = '0'
                tvdb = '0'

                poster = item.get('poster_path')
                if not poster == '' and not poster is None:
                    poster = ('%s%s' % (self.tmdb_poster, poster)).encode('utf-8')
                else:
                    poster = '0'

                fanart = item.get('backdrop_path')
                if not fanart == '' and not fanart is None:
                    fanart = ('%s%s' % (self.tmdb_fanart, fanart)).encode('utf-8')
                else:
                    fanart = '0'

                premiered = item['first_air_date']
                try:
                    premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except:
                    premiered = '0'
                premiered = premiered.encode('utf-8')

                rating = str(item['vote_average'])
                if rating == '' or rating is None:
                    rating = '0'
                rating = rating.encode('utf-8')

                votes = str(item['vote_count'])
                try:
                    votes = str(format(int(votes),',d'))
                except:
                    pass
                if votes == '' or votes is None:
                    votes = '0'
                votes = votes.encode('utf-8')

                plot = (item.get('overview')).encode('utf-8')

                try:
                    tagline = item['tagline']
                    if tagline == '' or tagline == '0' or tagline is None:
                        tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                    tagline = tagline.encode('utf-8')
                except: tagline = '0'

##--TMDb additional info
                url = self.tmdb_info_link % tmdb
                item = self.get_request(url)

                tvdb = item['external_ids']['tvdb_id']
                if tvdb == '' or tvdb is None or tvdb == 'N/A' or tvdb == 'NA': tvdb = '0'
                tvdb = re.sub('[^0-9]', '', str(tvdb))
                tvdb = tvdb.encode('utf-8')

                imdb = item['external_ids']['imdb_id']
                if imdb == '' or imdb is None or imdb == 'N/A' or imdb == 'NA': imdb = '0'
                imdb = imdb.encode('utf-8')

                genre = item['genres']
                try: genre = [x['name'] for x in genre]
                except: genre = '0'
                genre = ' / '.join(genre)
                genre = genre.encode('utf-8')
                if not genre: genre = 'NA'

                try: duration = str(item['runtime'])
                except: duration = '0'
                if duration == '' or duration is None or duration == 'N/A': duration = '0'
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
                if studio == '' or studio is None: studio = '0'
                studio = studio.encode('utf-8')

                director = item['credits']['crew']
                try: director = [x['name'] for x in director if x['job'].encode('utf-8') == 'Director']
                except: director = '0'
                if director == '' or director is None or director == []: director = '0'
                director = ' / '.join(director)
                director = director.encode('utf-8')

                writer = item['credits']['crew']
                try: writer = [x['name'] for x in writer if x['job'].encode('utf-8') in ['Writer', 'Screenplay']]
                except: writer = '0'
                try: writer = [x for n,x in enumerate(writer) if x not in writer[:n]]
                except: writer = '0'
                if writer == '' or writer is None or writer == []: writer = '0'
                writer = ' / '.join(writer)
                writer = writer.encode('utf-8')

                cast = item['credits']['cast']
                try: cast = [(x['name'].encode('utf-8'), x['character'].encode('utf-8')) for x in cast]
                except: cast = []

                item = {}
                item = {'content': 'movie', 'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes,
                                'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline, 'code': tmdb, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'poster': poster,
                                'poster2': '0', 'poster3': '0', 'banner': '0', 'fanart': fanart, 'fanart2': '0', 'fanart3': '0', 'clearlogo': '0', 'clearart': '0', 'landscape': '0', 'metacache': False, 'next': next}
                meta = {}
                meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.lang, 'user': self.tmdb_key, 'item': item}

                # fanart_thread = threading.Thread
                if not self.disable_fanarttv == 'true':
                    from resources.lib.indexers import fanarttv
                    extended_art =  fanarttv.get_tvshow_art(tvdb)
                    if not extended_art is None:
                        item.update(extended_art)
                        meta.update(item)

                self.list.append(item)
                self.meta.append(meta)
                metacache.insert(self.meta)
            except:
                pass
        return self.list


    def tmdb_art(self, tmdb):
        try:
            if self.tmdb_key == '':
                raise Exception()
            art3 = self.get_request(self.tmdb_art_link % tmdb)
        except:
            return None

        try:
            poster3 = art3['posters']
            log_utils.log('poster3 = %s' % str(poster3), __name__, log_utils.LOGDEBUG)
            poster3 = [(x['width'], x['file_path']) for x in poster3]
            log_utils.log('poster3 = %s' % str(poster3), __name__, log_utils.LOGDEBUG)
            poster3 = [x[1] for x in poster3]
            log_utils.log('poster3 = %s' % str(poster3), __name__, log_utils.LOGDEBUG)
            poster3 = self.tmdb_poster + poster3[0]
            log_utils.log('poster3 = %s' % str(poster3), __name__, log_utils.LOGDEBUG)
        except:
            poster3 = '0'
            log_utils.log('poster3 = %s' % str(poster3), __name__, log_utils.LOGDEBUG)
        try:
            fanart3 = art3['backdrops']
            fanart3 = [(x['width'], x['file_path']) for x in fanart3]
            fanart3 = [x[1] for x in fanart3]
            fanart3 = self.tmdb_fanart + fanart3[0]
        except:
            fanart3 = '0'

        extended_art = {'extended': True, 'poster3': poster3, 'fanart3': fanart3}
        return extended_art
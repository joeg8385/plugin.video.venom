# -*- coding: utf-8 -*-

'''
    Venom Add-on
'''

import os,sys,re,json,urlparse,datetime

from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import metacache
from resources.lib.modules import workers
from resources.lib.modules import trakt



class movies:
    def __init__(self):
        self.count = 40
        self.list = []

        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
        self.systime = (self.datetime).strftime('%Y%m%d%H%M%S%f')
        self.today_date = (self.datetime).strftime('%Y-%m-%d')
        self.month_date = (self.datetime - datetime.timedelta(days = 30)).strftime('%Y-%m-%d')
        self.year_date = (self.datetime - datetime.timedelta(days = 365)).strftime('%Y-%m-%d')

        self.imdb_link = 'https://www.imdb.com'
        self.imdb_user = control.setting('imdb.user').replace('ur', '')

        self.lang = control.apiLanguage()['trakt']

        self.tmdb_key = control.setting('tm.user')
        if self.tmdb_key == '' or self.tmdb_key == None:
            self.tmdb_key = '3320855e65a9758297fec4f7c9717698'

        # self.tm_art_link = 'https://api.themoviedb.org/3/movie/%s/images?api_key=%s&language=en-US&include_image_language=en,%s,null' % ('%s', self.tmdb_key, self.lang)
        self.tm_art_link = 'http://api.themoviedb.org/3/movie/%s/images?api_key=' + self.tmdb_key
        self.tm_img_link = 'https://image.tmdb.org/t/p/w%s%s'

        self.fanart_tv_user = control.setting('fanart.tv.user')
        if self.fanart_tv_user == '' or self.fanart_tv_user == None:
            self.fanart_tv_user = 'cf0ebcc2f7b824bd04cf3a318f15c17d'
        self.user = str(self.fanart_tv_user) + str(self.tmdb_key)
        self.fanart_tv_art_link = 'http://webservice.fanart.tv/v3/movies/%s'
        self.fanart_tv_level_link = 'http://webservice.fanart.tv/v3/level'


    def imdb_list(self, url):
        list = []
        try:
            for i in re.findall('date\[(\d+)\]', url):
                url = url.replace('date[%s]' % i, (self.datetime - datetime.timedelta(days = int(i))).strftime('%Y-%m-%d'))

            def imdb_watchlist_id(url):
                return client.parseDOM(client.request(url), 'meta', ret='content', attrs = {'property': 'pageId'})[0]
            if url == self.imdbwatchlist_link:
                url = cache.get(imdb_watchlist_id, 8640, url)
                url = self.imdblist_link % url
            elif url == self.imdbwatchlist2_link:
                url = cache.get(imdb_watchlist_id, 8640, url)
                url = self.imdblist2_link % url
            result = client.request(url)
            result = result.replace('\n', ' ')
            result = result.decode('iso-8859-1').encode('utf-8')

            items = client.parseDOM(result, 'div', attrs = {'class': '.+? lister-item'}) + client.parseDOM(result, 'div', attrs = {'class': 'lister-item .+?'})
            items += client.parseDOM(result, 'div', attrs = {'class': 'list_item.+?'})
        except:
            return

        try:
            # HTML syntax error, " directly followed by attribute name. Insert space in between. parseDOM can otherwise not handle it.
            result = result.replace('"class="lister-page-next', '" class="lister-page-next')

#            next = client.parseDOM(result, 'a', ret='href', attrs = {'class': '.+?ister-page-nex.+?'})
            next = client.parseDOM(result, 'a', ret='href', attrs = {'class': 'lister-page-next.+?'})

            if len(next) == 0:
                next = client.parseDOM(result, 'div', attrs = {'class': 'pagination'})[0]
                next = zip(client.parseDOM(next, 'a', ret='href'), client.parseDOM(next, 'a'))
                next = [i[0] for i in next if 'Next' in i[1]]

            next = url.replace(urlparse.urlparse(url).query, urlparse.urlparse(next[0]).query)
            next = client.replaceHTMLCodes(next)
            next = next.encode('utf-8')
        except:
            next = ''

        for item in items:
            try:
                title = client.parseDOM(item, 'a')[1]
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = client.parseDOM(item, 'span', attrs = {'class': 'lister-item-year.+?'})
                year = re.findall('(\d{4})', year[0])[0]
                year = year.encode('utf-8')

                try: show = '–'.decode('utf-8') in str(year).decode('utf-8') or '-'.decode('utf-8') in str(year).decode('utf-8')
                except: show = False
                if show: raise Exception() # Some lists contain TV shows.

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                try: mpaa = client.parseDOM(item, 'span', attrs = {'class': 'certificate'})[0]
                except: mpaa = '0'
                if mpaa == '' or mpaa == 'NOT_RATED': mpaa = '0'
                mpaa = mpaa.replace('_', '-')
                mpaa = client.replaceHTMLCodes(mpaa)
                mpaa = mpaa.encode('utf-8')

                imdb = client.parseDOM(item, 'a', ret='href')[0]
                imdb = re.findall('(tt\d*)', imdb)[0]
                imdb = imdb.encode('utf-8')

#                parseDOM cannot handle elements without a closing tag.
#                try: poster = client.parseDOM(item, 'img', ret='loadlate')[0]
#                except: poster = '0'
                try:
                    from bs4 import BeautifulSoup
                    html = BeautifulSoup(item, "html.parser")
                    poster = html.find_all('img')[0]['loadlate']
                except:
                    poster = '0'

                if '/nopicture/' in poster: poster = '0'
                poster = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', poster)
                poster = client.replaceHTMLCodes(poster)
                poster = poster.encode('utf-8')

                try: genre = client.parseDOM(item, 'span', attrs = {'class': 'genre'})[0]
                except: genre = '0'
                genre = ' / '.join([i.strip() for i in genre.split(',')])
                if genre == '': genre = '0'
                genre = client.replaceHTMLCodes(genre)
                genre = genre.encode('utf-8')

                try: duration = re.findall('(\d+?) min(?:s|)', item)[-1]
                except: duration = '0'
                duration = duration.encode('utf-8')

                rating = '0'
                try: rating = client.parseDOM(item, 'span', attrs = {'class': 'rating-rating'})[0]
                except:
                    try: rating = client.parseDOM(rating, 'span', attrs = {'class': 'value'})[0]
                    except:
                        try: rating = client.parseDOM(item, 'div', ret='data-value', attrs = {'class': '.*?imdb-rating'})[0]
                        except: pass
                if rating == '' or rating == '-': rating = '0'
                if rating == '0':
                    try:
                        rating = client.parseDOM(item, 'span', attrs = {'class': 'ipl-rating-star__rating'})[0]
                        if rating == '' or rating == '-': rating = '0'
                    except: pass
                rating = client.replaceHTMLCodes(rating)
                rating = rating.encode('utf-8')

                votes = '0'
                try: votes = client.parseDOM(item, 'span', attrs = {'name': 'nv'})[0]
                except:
                    try: votes = client.parseDOM(item, 'div', ret='title', attrs = {'class': '.*?rating-list'})[0]
                    except:
                        try: votes = re.findall('\((.+?) vote(?:s|)\)', votes)[0]
                        except: pass
                if votes == '': votes = '0'
                votes = client.replaceHTMLCodes(votes)
                votes = votes.encode('utf-8')

                try: director = re.findall('Director(?:s|):(.+?)(?:\||</div>)', item)[0]
                except: director = '0'
                director = client.parseDOM(director, 'a')
                director = ' / '.join(director)
                if director == '': director = '0'
                director = client.replaceHTMLCodes(director)
                director = director.encode('utf-8')

                try: cast = re.findall('Stars(?:s|):(.+?)(?:\||</div>)', item)[0]
                except: cast = '0'
                cast = client.replaceHTMLCodes(cast)
                cast = cast.encode('utf-8')
                cast = client.parseDOM(cast, 'a')
                if cast == []: cast = '0'

                plot = '0'
                try: plot = client.parseDOM(item, 'p', attrs = {'class': 'text-muted'})[0]
                except:
                    try: plot = client.parseDOM(item, 'div', attrs = {'class': 'item_description'})[0]
                    except: pass
                plot = plot.rsplit('<span>', 1)[0].strip()
                plot = re.sub('<.+?>|</.+?>', '', plot)
                if plot == '': plot = '0'
                if plot == '0':
                    try:
                        plot = client.parseDOM(item, 'div', attrs = {'class': 'lister-item-content'})[0]
                        plot = re.sub('<p\s*class="">', '<p class="plot_">', plot)
                        plot = client.parseDOM(plot, 'p', attrs = {'class': 'plot_'})[0]
                        plot = re.sub('<.+?>|</.+?>', '', plot)
                        if plot == '': plot = '0'
                    except: pass
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                list.append({'title': title, 'originaltitle': title, 'year': year, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'cast': cast, 'plot': plot, 'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'poster': poster, 'next': next})
            except:
                pass

        return list


    def imdb_person_list(self, url):
        try:
            result = client.request(url)
            result = result.decode('iso-8859-1').encode('utf-8')
#            items = client.parseDOM(result, 'div', attrs = {'class': '.+?etail'})
            items = client.parseDOM(result, 'div', attrs = {'class': '.+? lister-item'}) + client.parseDOM(result, 'div', attrs = {'class': 'lister-item .+?'})
        except:
            tools.Logger.error()

        for item in items:
            try:
                name = client.parseDOM(item, 'a')[1]
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = client.parseDOM(item, 'a', ret='href')[0]
                url = re.findall('(nm\d*)', url, re.I)[0]
                url = self.person_link % url
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                image = client.parseDOM(item, 'img', ret='src')[0]
                # if not ('._SX' in image or '._SY' in image): raise Exception()
                image = re.sub('(?:_SX|_SY|_UX|_UY|_CR|_AL)(?:\d+|_).+?\.', '_SX500.', image)
                image = client.replaceHTMLCodes(image)
                image = image.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'image': image})
            except:
                pass
        return self.list


    def imdb_user_list(self, url):
        try:
            result = client.request(url)
            result = result.decode('iso-8859-1').encode('utf-8')
            items = client.parseDOM(result, 'li', attrs = {'class': 'ipl-zebra-list__item user-list'})
#            items = client.parseDOM(result, 'div', attrs = {'class': 'list_name'})
        except:
            pass

        for item in items:
            try:
                name = client.parseDOM(item, 'a')[0]
                name = client.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = client.parseDOM(item, 'a', ret='href')[0]
                url = url.split('/list/', 1)[-1].strip('/')
                url = self.imdblist_link % url
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'context': url})
            except:
                pass
        self.list = sorted(self.list, key=lambda k: re.sub('(^the |^a |^an )', '', k['name'].lower()))
        return self.list


    def worker(self, level=1):
        if self.list == None or self.list == []: return
        self.meta = []
        total = len(self.list)

        self.fanart_tv_headers = {'api-key': '9f846e7ec1ea94fad5d8a431d1d26b43'}
        if not self.fanart_tv_user == '': self.fanart_tv_headers.update({'client-key': self.fanart_tv_user})

        for i in range(0, total): self.list[i].update({'metacache': False})

        self.list = metacache.fetch(self.list, self.lang, self.user)

        for r in range(0, total, 40):
            threads = []
            for i in range(r, r+40):
                if i <= total: threads.append(workers.Thread(self.super_info, i))
            [i.start() for i in threads]
            [i.join() for i in threads]
        if self.meta: metacache.insert(self.meta)

        self.list = [i for i in self.list if not i['imdb'] == '0']

        # self.list = metacache.local(self.list, self.tm_img_link, 'poster3', 'fanart2')

        if self.fanart_tv_user == '':
            for i in self.list: i.update({'clearlogo': '0', 'clearart': '0'})


    def super_info(self, i):
        try:
            if self.list[i]['metacache'] == True: raise Exception()

            imdb = self.list[i]['imdb']

            item = trakt.getMovieSummary(id=imdb)

            title = item.get('title')
            title = client.replaceHTMLCodes(title)

            originaltitle = title

            year = item.get('year', 0)
            year = re.sub('[^0-9]', '', str(year))

            imdb = item.get('ids', {}).get('imdb', '0')
            imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

            tmdb = str(item.get('ids', {}).get('tmdb', 0))

            premiered = item.get('released', '0')
            try: premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
            except: premiered = '0'

            genre = item.get('genres', [])
            genre = [x.title() for x in genre]
            genre = ' / '.join(genre).strip()
            if not genre: genre = '0'

            duration = str(item.get('runtime', 0))

            rating = item.get('rating', '0')
            if not rating or rating == '0.0': rating = '0'

            votes = item.get('votes', '0')
            try: votes = str(format(int(votes), ',d'))
            except: pass

            mpaa = item.get('certification', '0')
            if not mpaa: mpaa = '0'

            tagline = item.get('tagline', '0')

            plot = item.get('overview', '0')

            people = trakt.getPeople(imdb, 'movies')

            director = writer = ''
            if 'crew' in people and 'directing' in people['crew']:
                director = ', '.join([director['person']['name'] for director in people['crew']['directing'] if director['job'].lower() == 'director'])
            if 'crew' in people and 'writing' in people['crew']:
                writer = ', '.join([writer['person']['name'] for writer in people['crew']['writing'] if writer['job'].lower() in ['writer', 'screenplay', 'author']])

            cast = []
            for person in people.get('cast', []):
                cast.append({'name': person['person']['name'], 'role': person['character']})
            cast = [(person['name'], person['role']) for person in cast]

            try:
                if self.lang == 'en' or self.lang not in item.get('available_translations', [self.lang]): raise Exception()
                trans_item = trakt.getMovieTranslation(imdb, self.lang, full = True)

                title = trans_item.get('title') or title
                tagline = trans_item.get('tagline') or tagline
                plot = trans_item.get('overview') or plot
            except:
                pass


###--Fanart.tv artwork
            try:
                artmeta = True
                art = client.request(self.fanart_tv_art_link % imdb, headers = self.fanart_tv_headers, timeout = '10', error = True)
                try: art = json.loads(art)
                except: artmeta = False
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
                if 'moviebackground' in art: fanart = art['moviebackground']
                else: fanart = art['moviethumb']
                fanart = [(x['url'], x['likes']) for x in fanart if x.get('lang') == self.lang] + [(x['url'], x['likes']) for x in fanart if x.get('lang') == '']
                fanart = [(x[0], x[1]) for x in fanart]
                fanart = sorted(fanart, key=lambda x: int(x[1]), reverse=True)
                fanart = [x[0] for x in fanart][0]
                fanart = fanart.encode('utf-8')
            except:
                fanart = '0'

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






            try:
                if self.tmdb_key == '': raise Exception()
                art2 = client.request(self.tm_art_link % imdb, timeout= '10', error = True)
                art2 = json.loads(art2)
            except:
                pass

            try:
                poster3 = art2['posters']
                poster3 = [x for x in poster3 if x.get('iso_639_1') == 'en'] + [x for x in poster3 if not x.get('iso_639_1') == 'en']
                poster3 = [(x['width'], x['file_path']) for x in poster3]
                poster3 = [(x[0], x[1]) if x[0] < 300 else ('300', x[1]) for x in poster3]
                poster3 = self.tm_img_link % poster3[0]
                poster3 = poster3.encode('utf-8')
            except:
                poster3 = '0'

            try:
                fanart2 = art2['backdrops']
                fanart2 = [x for x in fanart2 if x.get('iso_639_1') == 'en'] + [x for x in fanart2 if not x.get('iso_639_1') == 'en']
                # fanart2 = [x for x in fanart2 if x.get('width') == 1920] + [x for x in fanart2 if x.get('width') < 1920]
                fanart2 = [x for x in fanart2 if x.get('width') == 1920] + [x for x in fanart2 if x.get('width') < 1920] + [x for x in fanart2 if x.get('width') <= 3840]
                fanart2 = [(x['width'], x['file_path']) for x in fanart2]
                fanart2 = [(x[0], x[1]) if x[0] < 1280 else ('1280', x[1]) for x in fanart2]
                fanart2 = self.tm_img_link % fanart2[0]
                fanart2 = fanart2.encode('utf-8')
            except:
                fanart2 = '0'

            item = {'title': title, 'originaltitle': originaltitle, 'year': year, 'imdb': imdb, 'tmdb': tmdb, 'poster2': poster2, 'poster3': poster3, 'banner': banner, 'fanart': fanart, 'fanart2': fanart2, 'clearlogo': clearlogo, 'clearart': clearart, 'landscape': landscape, 'premiered': premiered, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline}
            item = dict((k,v) for k, v in item.iteritems() if not v == '0')
            self.list[i].update(item)

            if artmeta == False: raise Exception()

            meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.lang, 'user': self.user, 'item': item}
            self.meta.append(meta)
        except:
            pass


class tvshows:
    def __init__(self, type = 'show', notifications = True):
        self.count = 40
        self.list = []
        self.meta = []
        self.threads = []
        self.type = type
        self.lang = control.apiLanguage()['tvdb']
        self.notifications = notifications

        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))

        self.fanart_tv_user = control.setting('fanart.tv.user')
        if self.fanart_tv_user == '' or self.fanart_tv_user == None:
            self.fanart_tv_user = 'cf0ebcc2f7b824bd04cf3a318f15c17d'
        self.user = self.fanart_tv_user + str('')
        self.fanart_tv_art_link = 'http://webservice.fanart.tv/v3/tv/%s'
        self.fanart_tv_level_link = 'http://webservice.fanart.tv/v3/level'

        # self.tvdb_key = control.setting('tvdb.user')
        # if self.tvdb_key == '' or self.tvdb_key == None:
            # self.tvdb_key = '1D62F2F90030C444'
        self.tvdb_key = 'MUQ2MkYyRjkwMDMwQzQ0NA=='
        self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/%s.xml' % (self.tvdb_key.decode('base64'), '%s', self.lang)
        self.tvdb_by_imdb = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s'
        self.tvdb_by_query = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s'
        self.tvdb_image = 'http://thetvdb.com/banners/'
        self.imdb_user = control.setting('imdb.user').replace('ur', '')
        self.imdb_link = 'http://www.imdb.com'
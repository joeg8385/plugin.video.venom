# -*- coding: utf-8 -*-

'''
    Venom Add-on
'''

import json,requests,threading,re,urllib
import datetime

from resources.lib.modules import control
from resources.lib.modules import log_utils
from resources.lib.modules import client
from resources.lib.modules import workers
from resources.lib.modules import trakt
from resources.lib.modules import cleantitle

networks_this_season = [
            ('A&E', '/networks/29/ae', 'https://i.imgur.com/xLDfHjH.png'),
            ('ABC', '/networks/3/abc', 'https://i.imgur.com/qePLxos.png'),
            ('Acorn TV', '/webchannels/129/acorn-tv', 'http://static.tvmaze.com/uploads/images/medium_landscape/74/185171.jpg'),
            ('Adult Swim', '/networks/10/adult-swim', 'https://i.imgur.com/jCqbRcS.png'),
            ('Amazon', '/webchannels/3/amazon', 'https://i.imgur.com/ru9DDlL.png'),
            ('AMC', '/networks/20/amc', 'https://i.imgur.com/ndorJxi.png'),
            ('Animal Planet', '/networks/92/animal-planet', 'https://i.imgur.com/olKc4RP.png'),
            ('Apple TV+', '/webchannels/310/apple-tv', 'http://static.tvmaze.com/uploads/images/medium_landscape/189/474058.jpg'),
            ('AT-X', '/networks/167/at-x', 'https://i.imgur.com/JshJYGN.png'),
            ('Audience', '/networks/31/audience-network', 'https://i.imgur.com/5Q3mo5A.png'),
            ('BBC America', '/networks/15/bbc-america', 'https://i.imgur.com/TUHDjfl.png'),
            ('BBC One', '/networks/12/bbc-one', 'https://i.imgur.com/u8x26te.png'),
            ('BBC Two', '/networks/37/bbc-two', 'https://i.imgur.com/SKeGH1a.png'),
            ('BBC Three', '/webchannels/71/bbc-three', 'https://i.imgur.com/SDLeLcn.png'),
            ('BBC Four', '/networks/51/bbc-four', 'https://i.imgur.com/PNDalgw.png'),
            ('BET', '/networks/56/bet', 'https://i.imgur.com/ZpGJ5UQ.png'),
            ('Blackpills', '/webchannels/186/blackpills', 'http://static.tvmaze.com/uploads/images/medium_landscape/108/270401.jpg'),
            ('Brat', '/webchannels/274/brat', 'http://static.tvmaze.com/uploads/images/medium_landscape/161/403172.jpg'),
            ('Bravo', '/networks/52/bravo', 'https://i.imgur.com/TmEO3Tn.png'),
            ('Cartoon Network', '/networks/11/cartoon-network', 'https://i.imgur.com/zmOLbbI.png'),
            ('CBC', '/networks/36/cbc', 'https://i.imgur.com/unQ7WCZ.png'),
            ('CBS', '/networks/2/cbs', 'https://i.imgur.com/8OT8igR.png'),
            ('Channel 4', '/networks/45/channel-4', 'https://i.imgur.com/6ZA9UHR.png'),
            ('Channel 5', '/networks/135/channel-5', 'https://i.imgur.com/5ubnvOh.png'),
            ('Cinemax', '/networks/19/cinemax', 'https://i.imgur.com/zWypFNI.png'),
            ('CNBC', '/networks/93/cnbc', 'https://static.tvmaze.com/uploads/images/original_untouched/10/27359.jpg'),

            ('Comedy Central', '/networks/23/comedy-central', 'https://i.imgur.com/ko6XN77.png'),
            ('Crackle', '/webchannels/4/crackle', 'https://i.imgur.com/53kqZSY.png'),
            ('CTV', '/networks/48/ctv', 'https://i.imgur.com/qUlyVHz.png'),
            ('CuriosityStream', '/webchannels/188/curiositystream', 'http://static.tvmaze.com/uploads/images/medium_landscape/108/272041.jpg'),
            ('CW', '/networks/5/the-cw', 'https://i.imgur.com/Q8tooeM.png'),
            ('CW Seed', '/webchannels/13/cw-seed', 'https://i.imgur.com/nOdKoEy.png'),
            ('DC Universe', '/webchannels/187/dc-universe', 'http://static.tvmaze.com/uploads/images/medium_landscape/155/388605.jpg'),
            ('Discovery Channel', '/networks/66/discovery-channel', 'https://i.imgur.com/8UrXnAB.png'),
            ('Discovery ID', '/networks/89/investigation-discovery', 'https://i.imgur.com/07w7BER.png'),
            ('Disney Channel', '/networks/78/disney-channel', 'https://i.imgur.com/ZCgEkp6.png'),
            ('Disney Junior', '/networks/1039/disney-junior', 'https://static.tvmaze.com/uploads/images/medium_landscape/46/116712.jpg'),
            ('Disney XD', '/networks/25/disney-xd', 'https://i.imgur.com/PAJJoqQ.png'),
            ('E! Entertainment', '/networks/43/e', 'https://i.imgur.com/3Delf9f.png'),
            ('E4', '/networks/41/e4', 'https://i.imgur.com/frpunK8.png'),
            # ('Fearnet', '/networks/466/fearnet', 'https://static.tvmaze.com/uploads/images/large_landscape/25/64861.jpg'),
            ('FOX', '/networks/4/fox', 'https://i.imgur.com/6vc0Iov.png'),
            ('Freeform', '/networks/26/freeform', 'https://i.imgur.com/f9AqoHE.png'),
            ('Fusion', '/networks/187/fusion', 'https://static.tvmaze.com/uploads/images/medium_untouched/11/29630.jpg'),
            ('FX', '/networks/13/fx', 'https://i.imgur.com/aQc1AIZ.png'),
            ('Hallmark', '/networks/50/hallmark-channel', 'https://i.imgur.com/zXS64I8.png'),
            # ('Hallmark Movies & Mysteries', '/networks/252/hallmark-movies-mysteries', 'https://static.tvmaze.com/uploads/images/original_untouched/13/34664.jpg'),
            ('HBO', '/networks/8/hbo', 'https://i.imgur.com/Hyu8ZGq.png'),
            ('HGTV', '/networks/192/hgtv', 'https://i.imgur.com/INnmgLT.png'),
            ('History Channel', '/networks/53/history', 'https://i.imgur.com/LEMgy6n.png'),
            # ('H2', '/networks/74/h2', 'https://static.tvmaze.com/uploads/images/medium_landscape/3/9115.jpg'),
            ('Hulu', '/webchannels/2/hulu', 'https://i.imgur.com/Tf81i9O.png'),
            ('ITV', '/networks/35/itv', 'https://i.imgur.com/5Hxp5eA.png'),
            ('Lifetime', '/networks/18/lifetime', 'https://i.imgur.com/tvYbhen.png'),
            ('MTV', '/networks/22/mtv', 'https://i.imgur.com/QM6DpNW.png'),
            ('National Geographic', '/networks/42/national-geographic-channel', 'https://i.imgur.com/XCGNKVQ.png'),
            ('NBC', '/networks/1/nbc', 'https://i.imgur.com/yPRirQZ.png'),
            ('Netflix', '/webchannels/1/netflix', 'https://i.imgur.com/jI5c3bw.png'),
            ('Nickelodeon', '/networks/27/nickelodeon', 'https://i.imgur.com/OUVoqYc.png'),
            ('Nicktoons', '/networks/73/nicktoons', 'https://static.tvmaze.com/uploads/images/medium_untouched/25/63394.jpg'),
            ('Oxygen', '/networks/79/oxygen', 'https://static.tvmaze.com/uploads/images/medium_untouched/116/290882.jpg'),
            ('PBS', '/networks/85/pbs', 'https://i.imgur.com/r9qeDJY.png'),
            # ('Playboy TV', '/networks/1035/playboy-tv', 'https://static.tvmaze.com/uploads/images/original_untouched/46/115366.jpg'),
            ('Showtime', '/networks/9/showtime', 'https://i.imgur.com/SawAYkO.png'),
            ('Sky1', '/networks/63/sky-1', 'https://i.imgur.com/xbgzhPU.png'),
            ('Starz', '/networks/17/starz', 'https://i.imgur.com/Z0ep2Ru.png'),
            ('Sundance', '/networks/33/sundance-tv', 'https://i.imgur.com/qldG5p2.png'),
            ('Syfy', '/networks/16/syfy', 'https://i.imgur.com/9yCq37i.png'),
            ('TBS', '/networks/32/tbs', 'https://i.imgur.com/RVCtt4Z.png'),
            ('TLC', '/networks/80/tlc', 'https://i.imgur.com/c24MxaB.png'),
            ('TNT', '/networks/14/tnt', 'https://i.imgur.com/WnzpAGj.png'),
            ('Travel Channel', '/networks/82/travel-channel', 'https://i.imgur.com/mWXv7SF.png'),
            ('TruTV', '/networks/84/trutv', 'https://i.imgur.com/HnB3zfc.png'),
            ('TV Land', '/networks/57/tvland', 'https://i.imgur.com/1nIeDA5.png'),

            ('TV One', '/networks/224/tv-one', 'https://static.tvmaze.com/uploads/images/original_untouched/25/63413.jpg'),

            ('USA', '/networks/30/usa-network', 'https://i.imgur.com/Doccw9E.png'),
            ('VH1', '/networks/55/vh1', 'https://i.imgur.com/IUtHYzA.png'),
            ('Viceland', '/networks/1006/viceland', 'https://static.tvmaze.com/uploads/images/original_untouched/42/105775.jpg'),
            ('WGN', '/networks/28/wgn-america', 'https://i.imgur.com/TL6MzgO.png'),
            ('WWE Network', '/webchannels/15/wwe-network', 'https://static.tvmaze.com/uploads/images/original_untouched/11/29695.jpg')
            # ('YouTube', '/webchannels/21/youtube', 'https://i.imgur.com/ZfewP1Y.png'),
            # ('YouTube Premium', '/webchannels/43/youtube-premium', 'https://static.tvmaze.com/uploads/images/medium_landscape/160/401362.jpg')
        ]

networks_view_all = [
            ('A&E', '/shows?Show[network_id]=29&page=1', 'https://i.imgur.com/xLDfHjH.png'),
            ('ABC', '/shows?Show[network_id]=3&page=1', 'https://i.imgur.com/qePLxos.png'),
            ('Acorn TV', '/shows?Show[network_id]=129&page=1', 'http://static.tvmaze.com/uploads/images/medium_landscape/74/185171.jpg'),
            ('Adult Swim', '/shows?Show[network_id]=10&page=1', 'https://i.imgur.com/jCqbRcS.png'),
            ('Amazon', '/shows?Show[webChannel_id]=3&page=1', 'https://i.imgur.com/ru9DDlL.png'),
            ('AMC', '/shows?Show[network_id]=20&page=1', 'https://i.imgur.com/ndorJxi.png'),
            ('Animal Planet', '/shows?Show[network_id]=92&page=1', 'https://i.imgur.com/olKc4RP.png'),
            ('Apple TV+', '/shows?Show[webChannel_id]=310&page=1', 'http://static.tvmaze.com/uploads/images/medium_landscape/189/474058.jpg'),
            ('AT-X', '/shows?Show[network_id]=167&page=1', 'https://i.imgur.com/JshJYGN.png'),
            ('Audience', '/shows?Show[network_id]=31&page=1', 'https://i.imgur.com/5Q3mo5A.png'),
            ('BBC America', '/shows?Show[network_id]=15&page=1', 'https://i.imgur.com/TUHDjfl.png'),
            ('BBC One', '/shows?Show[network_id]=12&page=1', 'https://i.imgur.com/u8x26te.png'),
            ('BBC Two', '/shows?Show[network_id]=37&page=1', 'https://i.imgur.com/SKeGH1a.png'),
            ('BBC Three', '/shows?Show[network_id]=71&page=1', 'https://i.imgur.com/SDLeLcn.png'),
            ('BBC Four', '/shows?Show[network_id]=51&page=1', 'https://i.imgur.com/PNDalgw.png'),
            ('BET', '/shows?Show[network_id]=56&page=1', 'https://i.imgur.com/ZpGJ5UQ.png'),
            ('Blackpills', '/shows?Show[webChannel_id]=186&page=1', 'http://static.tvmaze.com/uploads/images/medium_landscape/108/270401.jpg'),
            ('Brat', '/shows?Show[webChannel_id]=274&page=1', 'http://static.tvmaze.com/uploads/images/medium_landscape/161/403172.jpg'),
            ('Bravo', '/shows?Show[network_id]=52&page=1', 'https://i.imgur.com/TmEO3Tn.png'),
            ('Cartoon Network', '/shows?Show[network_id]=11&page=1', 'https://i.imgur.com/zmOLbbI.png'),
            ('CBC', '/shows?Show[network_id]=36&page=1', 'https://i.imgur.com/unQ7WCZ.png'),
            ('CBS', '/shows?Show[network_id]=2&page=1', 'https://i.imgur.com/8OT8igR.png'),
            ('Channel 4', '/shows?Show[network_id]=45&page=1', 'https://i.imgur.com/6ZA9UHR.png'),
            ('Channel 5', '/shows?Show[network_id]=135&page=1', 'https://i.imgur.com/5ubnvOh.png'),
            ('Cinemax', '/shows?Show[network_id]=19&page=1', 'https://i.imgur.com/zWypFNI.png'),
            ('CNBC', '/shows?Show[network_id]=93&page=1', 'https://static.tvmaze.com/uploads/images/original_untouched/10/27359.jpg'),

            ('Comedy Central', '/shows?Show[network_id]=23&page=1', 'https://i.imgur.com/ko6XN77.png'),
            ('Crackle', '/shows?Show%5BwebChannel_id%5D=4&page=1', 'https://i.imgur.com/53kqZSY.png'),
            ('CTV', '/shows?Show[network_id]=48&page=1', 'https://i.imgur.com/qUlyVHz.png'),
            ('CuriosityStream', '/shows?Show[webChannel_id]=188&page=1', 'http://static.tvmaze.com/uploads/images/medium_landscape/108/272041.jpg'),
            ('CW', '/shows?Show[network_id]=5&page=1', 'https://i.imgur.com/Q8tooeM.png'),
            ('CW Seed', '/shows?Show[webChannel_id]=13&page=1', 'https://i.imgur.com/nOdKoEy.png'),
            ('DC Universe', '/shows?Show%5BwebChannel_id%5D=187&page=1', 'http://static.tvmaze.com/uploads/images/medium_landscape/155/388605.jpg'),
            ('Discovery Channel', '/shows?Show[network_id]=66&page=1', 'https://i.imgur.com/8UrXnAB.png'),
            ('Discovery ID', '/shows?Show[network_id]=89&page=1', 'https://i.imgur.com/07w7BER.png'),
            ('Disney Channel', '/shows?Show[network_id]=78&page=1', 'https://i.imgur.com/ZCgEkp6.png'),
            ('Disney Junior', '/shows?Show[network_id]=1039&page=1', 'https://static.tvmaze.com/uploads/images/medium_landscape/46/116712.jpg'),
            ('Disney XD', '/shows?Show[network_id]=25&page=1', 'https://i.imgur.com/PAJJoqQ.png'),
            ('E! Entertainment', '/shows?Show[network_id]=43&page=1', 'https://i.imgur.com/3Delf9f.png'),
            ('E4', '/shows?Show[network_id]=41&page=1', 'https://i.imgur.com/frpunK8.png'),
            ('Fearnet', '/shows?Show[network_id]=466&page=1', 'https://static.tvmaze.com/uploads/images/large_landscape/25/64861.jpg'),
            ('FOX', '/shows?Show[network_id]=4&page=1', 'https://i.imgur.com/6vc0Iov.png'),
            ('Freeform', '/shows?Show[network_id]=26&page=1', 'https://i.imgur.com/f9AqoHE.png'),
            ('Fusion', '/shows?Show[network_id]=187&page=1', 'https://static.tvmaze.com/uploads/images/medium_untouched/11/29630.jpg'),
            ('FX', '/shows?Show[network_id]=13&page=1', 'https://i.imgur.com/aQc1AIZ.png'),
            ('Hallmark', '/shows?Show[network_id]=50&page=1', 'https://i.imgur.com/zXS64I8.png'),
            ('Hallmark Movies & Mysteries', '/shows?Show[network_id]=252&page=1', 'https://static.tvmaze.com/uploads/images/original_untouched/13/34664.jpg'),
            ('HBO', '/shows?Show[network_id]=8&page=1', 'https://i.imgur.com/Hyu8ZGq.png'),
            ('HGTV', '/shows?Show[network_id]=192&page=1', 'https://i.imgur.com/INnmgLT.png'),
            ('History Channel', '/shows?Show[network_id]=53&page=1', 'https://i.imgur.com/LEMgy6n.png'),
            ('H2', '/shows?Show[network_id]=74&page=1', 'https://static.tvmaze.com/uploads/images/medium_landscape/3/9115.jpg'),
            ('Hulu', '/shows?Show[webChannel_id]=2&page=1', 'https://i.imgur.com/Tf81i9O.png'),
            ('ITV', '/shows?Show[network_id]=35&page=1', 'https://i.imgur.com/5Hxp5eA.png'),
            ('Lifetime', '/shows?Show[network_id]=18&page=1', 'https://i.imgur.com/tvYbhen.png'),
            ('MTV', '/shows?Show[network_id]=22&page=1', 'https://i.imgur.com/QM6DpNW.png'),
            ('National Geographic', '/shows?Show[network_id]=42&page=1', 'https://i.imgur.com/XCGNKVQ.png'),
            ('NBC', '/shows?Show[network_id]=1&page=1', 'https://i.imgur.com/yPRirQZ.png'),
            ('Netflix', '/shows?Show[webChannel_id]=1&page=1', 'https://i.imgur.com/jI5c3bw.png'),
            ('Nickelodeon', '/shows?Show[network_id]=27&page=1', 'https://i.imgur.com/OUVoqYc.png'),
            ('Nicktoons', '/shows?Show[network_id]=73&page=1', 'https://static.tvmaze.com/uploads/images/medium_untouched/25/63394.jpg'),
            ('Oxygen', '/shows?Show[network_id]=79&page=1', 'https://static.tvmaze.com/uploads/images/medium_untouched/116/290882.jpg'),
            ('PBS', '/shows?Show[network_id]=85&page=1', 'https://i.imgur.com/r9qeDJY.png'),
            ('Showtime', '/shows?Show[network_id]=9&page=1', 'https://i.imgur.com/SawAYkO.png'),
            ('Sky1', '/shows?Show[network_id]=63&page=1', 'https://i.imgur.com/xbgzhPU.png'),
            ('Starz', '/shows?Show[network_id]=17&page=1', 'https://i.imgur.com/Z0ep2Ru.png'),
            ('Sundance', '/shows?Show[network_id]=33&page=1', 'https://i.imgur.com/qldG5p2.png'),
            ('Syfy', '/shows?Show[network_id]=16&page=1', 'https://i.imgur.com/9yCq37i.png'),
            ('TBS', '/shows?Show[network_id]=32&page=1', 'https://i.imgur.com/RVCtt4Z.png'),
            ('TLC', '/shows?Show[network_id]=80&page=1', 'https://i.imgur.com/c24MxaB.png'),
            ('TNT', '/shows?Show[network_id]=14&page=1', 'https://i.imgur.com/WnzpAGj.png'),
            ('Travel Channel', '/shows?Show[network_id]=82&page=1', 'https://i.imgur.com/mWXv7SF.png'),
            ('TruTV', '/shows?Show[network_id]=84&page=1', 'https://i.imgur.com/HnB3zfc.png'),
            ('TV Land', '/shows?Show[network_id]=57&page=1', 'https://i.imgur.com/1nIeDA5.png'),

            ('TV One', '/shows?Show[network_id]=224&page=1', 'https://static.tvmaze.com/uploads/images/original_untouched/25/63413.jpg'),

            ('USA', '/shows?Show[network_id]=30&page=1', 'https://i.imgur.com/Doccw9E.png'),
            ('VH1', '/shows?Show[network_id]=55&page=1', 'https://i.imgur.com/IUtHYzA.png'),
            ('Viceland', '/shows?Show[network_id]=1006&page=1', 'https://static.tvmaze.com/uploads/images/original_untouched/42/105775.jpg'),
            ('WGN', '/shows?Show[network_id]=28&page=1', 'https://i.imgur.com/TL6MzgO.png'),
            ('WWE Network', '/shows?Show[webChannel_id]=15&page=1', 'https://static.tvmaze.com/uploads/images/original_untouched/11/29695.jpg')

            # ('YouTube', '/webchannels/21/youtube', 'https://i.imgur.com/ZfewP1Y.png'),
            # ('YouTube Premium', '/webchannels/43/youtube-premium', 'https://static.tvmaze.com/uploads/images/medium_landscape/160/401362.jpg')
        ]


class tvshows:
    def __init__(self, type = 'show', notifications = True):
        last = []
        self.count = 40
        self.list = []
        self.meta = []
        self.threads = []
        self.type = type
        self.lang = control.apiLanguage()['tvdb']
        self.notifications = notifications

        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))

        self.tvmaze_link = 'http://www.tvmaze.com'
        self.tvmaze_info_link = 'http://api.tvmaze.com/shows/%s?embed=cast'

        # self.tvdb_key = control.setting('tvdb.user')
        # if self.tvdb_key == '' or self.tvdb_key == None:
            # self.tvdb_key = '1D62F2F90030C444'
        self.tvdb_key = 'MUQ2MkYyRjkwMDMwQzQ0NA=='
        self.tvdb_info_link = 'http://thetvdb.com/api/%s/series/%s/%s.xml' % (self.tvdb_key.decode('base64'), '%s', self.lang)
        self.tvdb_by_imdb = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s'
        self.tvdb_by_query = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s'
        self.tvdb_image = 'http://thetvdb.com/banners/'


        self.tmdb_key = control.setting('tm.user')
        if self.tmdb_key == '' or self.tmdb_key == None:
            self.tmdb_key = '3320855e65a9758297fec4f7c9717698'
        self.tmdb_art_link = 'http://api.themoviedb.org/3/tv/%s/images?api_key=' + self.tmdb_key

        # self.tmdb_info_link = 'http://api.themoviedb.org/3/tv/%s?api_key=%s&language=%s' % ('%s', self.tmdb_key, self.tmdb_lang)
# ###                                                                                  other "append_to_response" options                                           alternative_titles,videos,images

        self.tmdb_img_link = 'http://image.tmdb.org/t/p/w%s%s'

        self.fanart_tv_user = control.setting('fanart.tv.user')
        if self.fanart_tv_user == '' or self.fanart_tv_user == None:
            self.fanart_tv_user = 'cf0ebcc2f7b824bd04cf3a318f15c17d'
        self.user = self.fanart_tv_user + str('')
        self.fanart_tv_art_link = 'http://webservice.fanart.tv/v3/tv/%s'


    def get_TMDb_request(self, url):
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


    def tvmaze_list(self, url):
        try:
            result = client.request(url)
            if control.setting('tvshows.networks.view') == '0':
                result = client.parseDOM(result, 'section', attrs = {'id': 'this-seasons-shows'})
                items = client.parseDOM(result, 'span', attrs = {'class': 'title .*'})
                next = '0'
                list_count = 60

            if control.setting('tvshows.networks.view') == '1':
                result = client.parseDOM(result, 'div', attrs = {'id': 'w1'})
                # result = client.parseDOM(result, 'div', attrs = {'class': 'content auto cell'})
                items = client.parseDOM(result, 'span', attrs = {'class': 'title'})
                next = url
                list_count = 25
                page = int(str(url.split('&page=', 1)[1]))
                next = '%s&page=%s' % (next.split('&page=', 1)[0], str(page+1))

                last = client.parseDOM(result, 'li', attrs = {'class': 'last disabled'})
                if not last == []: next = '0'

            items = [client.parseDOM(i, 'a', ret='href') for i in items]
            items = [i[0] for i in items if len(i) > 0]
            items = [re.findall('/(\d+)/', i) for i in items]
            items = [i[0] for i in items if len(i) > 0]
            items = items[:list_count]
        except:
            return

        def items_list(i):
            try:
                url = self.tvmaze_info_link % i
                item = client.request(url)
                item = json.loads(item)
                # if control.setting('tvshows.networks.filter') == '0' and not item['status'] == 'Running' or not item['status'] == 'In Development':
                    # raise exception()
                # if control.setting('tvshows.networks.filter') == '1' and not item['status'] == 'Ended':
                    # raise exception()
                # if control.setting('tvshows.networks.filter') == '2' and not item['type'] == 'Documentary':
                    # raise exception()
                # if control.setting('tvshows.networks.filter') == '3' and not item['type'] == 'talk show':
                    # raise exception()
                # if control.setting('tvshows.networks.filter') == '4' and not item['status'] == 'Running' or not item['status'] == 'In Development' or not item['status'] == 'Ended':
                    # raise exception()
                    # # and not item['type'] == 'reality':
                    # # and not item['type'] == 'news':
                title = item['name']
                title = re.sub('\s(|[(])(UK|US|AU|\d{4})(|[)])$', '', title)
                title = client.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                try:
                    year = item['premiered']
                    year = re.findall('(\d{4})', year)[0]
                    year = year.encode('utf-8')
                except: yeat = '0'

                try:
                    imdb = item['externals']['imdb']
                    if imdb == None or imdb == '': imdb = '0'
                    else: imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))
                    imdb = imdb.encode('utf-8')
                except: imdb = '0'

                try:
                    tvdb = item['externals']['thetvdb']
                    if tvdb == None or tvdb == '': tvdb = '0'
                    else: tvdb = re.sub('[^0-9]', '', str(tvdb))
                    tvdb = tvdb.encode('utf-8')
                except: tvdb = '0'

                tmdb = '0'

                premiered = item['premiered']
                try: premiered = re.findall('(\d{4}-\d{2}-\d{2})', premiered)[0]
                except: premiered = '0'
                premiered = premiered.encode('utf-8')

                try: studio = item['network']['name']
                except: studio = '0'
                if studio == '0':
                    try: studio = item['webChannel']['name']
                    except: studio = '0'
                if studio == None: studio = '0'
                studio = studio.encode('utf-8')

                try:
                    genre = item['genres']
                    genre = [i.title() for i in genre]
                    genre = (' / '.join(genre)).encode('utf-8')
                    if genre == '' or genre == None: raise Exception()
                except: genre = 'NA'

                try:
                    duration = str(item['runtime']).encode('utf-8')
                except: duration = '0'

                try:
                    rating = str(item['rating']['average']).encode('utf-8')
                except: rating = '0.0'

                try:
                    plot = item['summary']
                    plot = re.sub('<.+?>|</.+?>|\n', '', plot)
                    plot = client.replaceHTMLCodes(plot)
                    plot = plot.encode('utf-8')
                except: plot = '0'

                try:
                    content = item['type'].lower()
                    content = content.encode('utf-8')
                except: content = '0'

                # try: status = item['status']
                # except: status = '0'
                # if status == None or status == '': status = '0'
                # status = status.encode('utf-8')

                # cast = []
                # try:
                    # people = item['_embedded']['cast']
                    # cast.append({'name': people['person']['name']})
                    # # cast.append({'name': people['person']['name'], 'role': people['character']['name']})
                # except: cast = []

                try:
                    poster = item['image']['original']
                    poster = poster.encode('utf-8')
                except: poster = '0'

                fanart = '0' ; banner = '0'


###--Check TVDb for missing info
                if tvdb == '0' or imdb == '0':
                    url = self.tvdb_by_query % (urllib.quote_plus(title))
                    item2 = client.request(url, timeout='20')
                    item2 = re.sub(r'[^\x00-\x7F]+', '', item2)
                    item2 = client.replaceHTMLCodes(item2)
                    item2 = client.parseDOM(item2, 'Series')
                    if tvdb == '0':
                        try: tvdb = client.parseDOM(item2, 'seriesid')[0]
                        except: tvdb = '0'
                    if imdb == '0':
                        try: imdb = client.parseDOM(item2, 'IMDB_ID')[0]
                        except: imdb = '0'

                try:
                    if self.tvdb_key == '' or tvdb == '0': raise Exception()
                    url = self.tvdb_info_link % tvdb
                    item3 = client.request(url, timeout='20', error=True)
                except: item3 = None ; fanart = '0'

                if poster == '0' and not item3 == None :
                    try:
                        poster = client.parseDOM(item3, 'poster')[0]
                        if not poster == '' or not poster == None: poster = self.tvdb_image + poster
                        else: poster = '0'
                        poster = client.replaceHTMLCodes(poster)
                        poster = poster.encode('utf-8')
                    except: poster = '0'

                if not item3 == None:
                    try:
                        banner = client.parseDOM(item3, 'banner')[0]
                        if not banner == '' or not banner == None: banner = self.tvdb_image + banner
                        else: banner = '0'
                        banner = client.replaceHTMLCodes(banner)
                        banner = banner.encode('utf-8')
                    except: banner = '0'

                    try:
                        fanart = client.parseDOM(item3, 'fanart')[0]
                        if not fanart == '': fanart = self.tvdb_image + fanart
                        fanart = client.replaceHTMLCodes(fanart)
                        fanart = fanart.encode('utf-8')
                    except: fanart = '0'

                    try:
                        cast = client.parseDOM(item3, 'Actors')[0]
                        cast = [x for x in cast.split('|') if not x == '']
                        cast = [(x.encode('utf-8'), '') for x in cast]
                    except: cast = '0'

                    try:
                        mpaa = client.parseDOM(item3, 'ContentRating')[0]
                        mpaa = client.replaceHTMLCodes(mpaa)
                        mpaa = mpaa.encode('utf-8')
                    except: mpaa = 'NR'

                    if duration == '0':
                        try:
                            duration = client.parseDOM(item3, 'Runtime')[0]
                            duration = client.replaceHTMLCodes(duration)
                            duration = duration.encode('utf-8')
                        except: duration = '0'

                    try:
                        votes = client.parseDOM(item3, 'RatingCount')[0]
                        votes = client.replaceHTMLCodes(votes)
                        votes = votes.encode('utf-8')
                    except: votes = '0'

                    if year == '0':
                        try:
                            year = client.parseDOM(item3, 'FirstAired')[0]
                            year = re.compile('(\d{4})').findall(year)[0]
                            year = year.encode('utf-8')
                        except: year = '0'
###-----

                if next == '0':
                    item = {}
                    item = {'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'mpaa': mpaa, 'genre': genre, 'duration': duration, 'cast': cast, 'rating': rating, 'votes': votes, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'tmdb': tmdb, 'poster': poster, 'poster2': '0', 'banner': banner, 'banner2': '0', 'fanart': fanart, 'fanart2': '0', 'clearlogo': '0', 'clearart': '0', 'landscape': '0', 'metacache': False, 'content': content}

                    meta = {}
                    meta = {'tmdb': tmdb, 'imdb': imdb, 'tvdb': tvdb, 'lang': self.lang, 'user': self.user, 'item': item}

                else:
                    item = {}
                    item = {'title': title, 'originaltitle': title, 'year': year, 'premiered': premiered, 'studio': studio, 'mpaa': mpaa, 'genre': genre, 'duration': duration, 'cast': cast, 'rating': rating, 'votes': votes, 'plot': plot, 'imdb': imdb, 'tvdb': tvdb, 'tmdb': tmdb, 'poster': poster, 'poster2': '0', 'banner': banner, 'banner2': '0', 'fanart': fanart, 'fanart2': '0', 'clearlogo': '0', 'clearart': '0', 'landscape': '0', 'metacache': False, 'next': next, 'content': content}

                    meta = {}
                    meta = {'tmdb': tmdb, 'imdb': imdb, 'tvdb': tvdb, 'lang': self.lang, 'user': self.user, 'item': item}

                # fanart_thread = threading.Thread
                from resources.lib.indexers import fanarttv
                extended_art = fanarttv.get_tvshow_art(tvdb)
                if not extended_art == None:
                    item.update(extended_art)
                    meta.update(item)

                self.list.append(item)
                self.meta.append(meta)
                metacache.insert(self.meta)
            except:
                pass

        try:
            threads = []
            for i in items: threads.append(workers.Thread(items_list, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

            filter = [i for i in self.list if i['content'] == 'scripted']
            filter += [i for i in self.list if not i['content'] == 'scripted']
            self.list = filter

            return self.list
        except:
            return

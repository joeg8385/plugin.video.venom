# -*- coding: utf-8 -*-

'''
    Venom Add-on
'''

import os, sys, xbmc

from resources.lib.modules import control
from resources.lib.modules import trakt
from resources.lib.modules import cache

try:
    sysaddon = sys.argv[0]
    syshandle = int(sys.argv[1])
except:
    sysaddon = ''
    syshandle = '1'
    pass


artPath = control.artPath()
addonFanart = control.addonFanart()

imdbCredentials = False if control.setting('imdb.user') == '' else True
traktCredentials = trakt.getTraktCredentialsInfo()
traktIndicators = trakt.getTraktIndicatorsInfo()


class Navigator:
    def root(self):
        self.addDirectoryItem(32001, 'movieNavigator', 'movies.png', 'movies.png')
        self.addDirectoryItem(32002, 'tvNavigator', 'tvshows.png', 'tvshows.png')

        if self.getMenuEnabled('mylists.widget') is True:
            self.addDirectoryItem(32003, 'mymovieNavigator', 'mymovies.png', 'mymovies.png')
            self.addDirectoryItem(32004, 'mytvNavigator', 'mytvshows.png', 'mytvshows.png')

        if not control.setting('newmovies.widget') == '0':
            self.addDirectoryItem(32005, 'newMovies', 'latest-movies.png', 'latest-movies.png')

        if (traktIndicators is True and not control.setting('tv.widget.alt') == '0') or (traktIndicators is False and not control.setting('tv.widget') == '0'):
            self.addDirectoryItem(32006, 'tvWidget', 'latest-episodes.png', 'DefaultRecentlyAddedEpisodes.png')
            self.addDirectoryItem('Recently Aired', 'calendar&url=added', 'latest-episodes.png', 'DefaultRecentlyAddedEpisodes.png', queue=True)

        if not control.setting('furk.api') == '' or None:
            self.addDirectoryItem('Furk.net', 'furkNavigator', 'movies.png', 'movies.png')

        self.addDirectoryItem(32010, 'searchNavigator', 'search.png', 'search.png')
        self.addDirectoryItem(32008, 'toolNavigator', 'tools.png', 'tools.png')

        downloads = True if control.setting('downloads') == 'true' and (len(control.listDir(control.setting('movie.download.path'))[0]) > 0 or len(control.listDir(control.setting('tv.download.path'))[0]) > 0) else False
        if downloads is True:
            self.addDirectoryItem(32009, 'downloadNavigator', 'downloads.png', 'downloads.png')

        self.addDirectoryItem('News and Info!!', 'ShowNews', 'icon.png', 'icon.png')
        self.addDirectoryItem('Change Log!!', 'ShowChangelog', 'icon.png', 'icon.png')
        self.endDirectory()


    def furk(self):
        self.addDirectoryItem('User Files', 'furkUserFiles', 'mytvnavigator.png', 'mytvnavigator.png')
        self.addDirectoryItem('Search', 'furkSearch', 'search.png', 'search.png')
        self.endDirectory()


    def getMenuEnabled(self, menu_title):
        is_enabled = control.setting(menu_title).strip()
        if (is_enabled == '' or is_enabled == 'false'):
            return False
        return True


    def movies(self, lite=False):
        if self.getMenuEnabled('navi.movie.imdb.intheater') is True:
            self.addDirectoryItem(32022, 'movies&url=theaters', 'imdb.png', 'in-theaters.png')
        if self.getMenuEnabled('navi.movie.tmdb.nowplaying') is True:
            self.addDirectoryItem('Now Playing', 'tmdbmovies&url=tmdb_nowplaying', 'tmdb.png', 'in-theaters.png')
        if self.getMenuEnabled('navi.movie.trakt.anticipated') is True:
            self.addDirectoryItem('Anticipated', 'movies&url=traktanticipated', 'trakt.png', 'in-theaters.png')
        if self.getMenuEnabled('navi.movie.tmdb.upcoming') is True:
            self.addDirectoryItem('Upcoming', 'tmdbmovies&url=tmdb_upcoming', 'tmdb.png', 'in-theaters.png')
        if self.getMenuEnabled('navi.movie.imdb.popular') is True:
            self.addDirectoryItem(32018, 'movies&url=mostpopular', 'imdb.png', 'most-popular.png')
        if self.getMenuEnabled('navi.movie.tmdb.popular') is True:
            self.addDirectoryItem('Popular', 'tmdbmovies&url=tmdb_popular', 'tmdb.png', 'most-popular.png')
        if self.getMenuEnabled('navi.movie.trakt.popular') is True:
            self.addDirectoryItem('Popular', 'movies&url=traktpopular', 'trakt.png', 'most-popular.png')
        if self.getMenuEnabled('navi.movie.imdb.boxoffice') is True:
            self.addDirectoryItem(32020, 'movies&url=imdbboxoffice', 'imdb.png', 'box-office.png')
        if self.getMenuEnabled('navi.movie.trakt.boxoffice') is True:
            self.addDirectoryItem('Box Office', 'movies&url=traktboxoffice', 'trakt.png', 'box-office.png')

        self.addDirectoryItem(32019, 'movies&url=mostvoted', 'imdb.png', 'most-voted.png')
        self.addDirectoryItem('Top Rated', 'tmdbmovies&url=tmdb_toprated', 'tmdb.png', 'most-voted.png')
        self.addDirectoryItem(32017, 'movies&url=trakttrending', 'trakt.png', 'most-voted.png')

        self.addDirectoryItem(33662, 'movies&url=traktrecommendations', 'trakt.png', 'people-watching.png')
        self.addDirectoryItem(32035, 'movies&url=featured', 'imdb.png', 'people-watching.png')

        if not control.setting('newmovies.widget') == '0':
            self.addDirectoryItem(32005, 'newMovies', 'imdb.png', 'latest-movies.png')

        self.addDirectoryItem(32000, 'collectionsNavigator', 'boxsets.png', 'boxsets.png')
        self.addDirectoryItem(32021, 'movies&url=oscars', 'imdb.png', 'oscar-winners.png')
        self.addDirectoryItem(32659, 'movies&url=oscarsnominees', 'imdb.png', 'oscar-winners.png')
        self.addDirectoryItem(32011, 'movieGenres', 'imdb.png', 'genres.png')
        self.addDirectoryItem(32012, 'movieYears', 'imdb.png', 'years.png')
        self.addDirectoryItem(32013, 'moviePersons', 'imdb.png', 'people.png')
        self.addDirectoryItem(32014, 'movieLanguages', 'imdb.png', 'languages.png')
        self.addDirectoryItem(32015, 'movieCertificates', 'imdb.png', 'certificates.png')

        if lite is False:
            if self.getMenuEnabled('mylists.widget') is True:
               self.addDirectoryItem(32003, 'mymovieliteNavigator', 'mymovies.png', 'mymovies.png')
            self.addDirectoryItem(32028, 'moviePerson', 'people-search.png', 'people-search.png')
            self.addDirectoryItem(32010, 'movieSearch', 'search.png', 'search.png')
        self.endDirectory()


    def mymovies(self, lite=False):
        self.accountCheck()
        self.addDirectoryItem(32039, 'movieUserlists', 'userlists.png', 'userlists.png')
        # self.addDirectoryItem(33662, 'movies&url=traktrecommendations', 'trakt.png', 'trakt.png', queue = True)

        if traktCredentials is True and imdbCredentials is True:
            self.addDirectoryItem(32032, 'movies&url=traktcollection', 'trakt.png', 'trakt.png', queue=True, context=(32551, 'moviesToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'movies&url=traktwatchlist', 'trakt.png', 'trakt.png', queue=True, context=(32551, 'moviesToLibrary&url=traktwatchlist'))

            if traktIndicators is True:
                self.addDirectoryItem(35308, 'movies&url=traktunfinished', 'trakt.png', 'trakt.png', queue=True)
                self.addDirectoryItem(32036, 'movies&url=trakthistory', 'trakt.png', 'trakt.png', queue=True)
                self.addDirectoryItem(32033, 'movies&url=imdbwatchlist2', 'imdb.png', 'imdb.png', queue=True)

        elif traktCredentials is True:
            self.addDirectoryItem(32032, 'movies&url=traktcollection', 'trakt.png', 'trakt.png', queue=True, context=(32551, 'moviesToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'movies&url=traktwatchlist', 'trakt.png', 'trakt.png', queue=True, context=(32551, 'moviesToLibrary&url=traktwatchlist'))

            if traktIndicators is True:
                self.addDirectoryItem(35308, 'movies&url=traktunfinished', 'trakt.png', 'trakt.png', queue=True)
                self.addDirectoryItem(32036, 'movies&url=trakthistory', 'trakt.png', 'trakt.png', queue=True)

        elif imdbCredentials is True:
#            self.addDirectoryItem(32032, 'movies&url=imdbwatchlist', 'imdb.png', 'imdb.png', queue=True)
            self.addDirectoryItem(32033, 'movies&url=imdbwatchlist2', 'imdb.png', 'imdb.png', queue=True)

        if lite is False:
            self.addDirectoryItem(32031, 'movieliteNavigator', 'movies.png', 'movies.png')
            self.addDirectoryItem(32028, 'moviePerson', 'people-search.png', 'people-search.png')
            self.addDirectoryItem(32010, 'movieSearch', 'search.png', 'search.png')
        self.endDirectory()


    def tvshows(self, lite=False):
        if self.getMenuEnabled('navi.tv.imdb.popular') is True:
            self.addDirectoryItem(32050, 'tvshows&url=popular', 'imdb.png', 'most-popular.png')
        if self.getMenuEnabled('navi.tv.tmdb.popular') is True:
            self.addDirectoryItem(32050, 'tmdbTvshows&url=tmdb_popular', 'tmdb.png', 'most-popular.png')
        if self.getMenuEnabled('navi.tv.trakt.popular') is True:
            self.addDirectoryItem(32050, 'tvshows&url=traktpopular', 'trakt.png', 'most-popular.png', queue=True)
        if self.getMenuEnabled('navi.tv.imdb.mostvoted') is True:
            self.addDirectoryItem(32019, 'tvshows&url=views', 'imdb.png', 'most-voted.png')
        if self.getMenuEnabled('navi.tv.tmdb.toprated') is True:
            self.addDirectoryItem(32051, 'tmdbTvshows&url=tmdb_toprated', 'tmdb.png', 'most-voted.png')

        self.addDirectoryItem(32017, 'tvshows&url=trakttrending', 'trakt.png', 'most-voted.png')
        self.addDirectoryItem(32023, 'tvshows&url=rating', 'imdb.png', 'highly-rated.png')
        self.addDirectoryItem(33662, 'tvshows&url=traktrecommendations', 'trakt.png', 'highly-rated.png', queue=True)
        self.addDirectoryItem(32011, 'tvGenres', 'genres.png', 'genres.png')
        self.addDirectoryItem(32016, 'tvNetworks', 'networks.png', 'networks.png')
        self.addDirectoryItem(32014, 'tvLanguages', 'languages.png', 'languages.png')
        self.addDirectoryItem(32015, 'tvCertificates', 'certificates.png', 'certificates.png')
        self.addDirectoryItem("Trakt On Deck", 'calendar&url=onDeck', 'trakt.png', 'airing-today.png')
        self.addDirectoryItem(32364, 'tmdbTvshows&url=tmdb_airingtoday', 'tmdb.png', 'airing-today.png')
        self.addDirectoryItem(32024, 'tvshows&url=airing', 'imdb.png', 'airing-today.png')
        self.addDirectoryItem(32052, 'tmdbTvshows&url=tmdb_ontheair', 'tmdb.png', 'returning-tvshows.png')
        self.addDirectoryItem(32025, 'tvshows&url=active', 'imdb.png', 'returning-tvshows.png')
        self.addDirectoryItem(32026, 'tvshows&url=premiere', 'imdb.png', 'new-tvshows.png')
        self.addDirectoryItem(32027, 'calendars', 'calendar.png', 'calendar.png')

        if (traktIndicators is True and not control.setting('tv.widget.alt') == '0') or (traktIndicators is False and not control.setting('tv.widget') == '0'):
            self.addDirectoryItem(32006, 'tvWidget', 'latest-episodes.png', 'latest-episodes.png')

        if lite is False:
            if self.getMenuEnabled('mylists.widget') is True:
               self.addDirectoryItem(32004, 'mytvliteNavigator', 'mytvshows.png', 'mytvshows.png')

            self.addDirectoryItem(32028, 'tvPerson', 'people-search.png', 'people-search.png')
            self.addDirectoryItem(32010, 'tvSearch', 'search.png', 'search.png')
        self.endDirectory()


    def mytvshows(self, lite=False):
        self.accountCheck()
        self.addDirectoryItem(32040, 'tvUserlists', 'userlists.png', 'userlists.png')
        if traktCredentials is True and imdbCredentials is True:
            self.addDirectoryItem(32032, 'tvshows&url=traktcollection', 'trakt.png', 'trakt.png', context=(32551, 'tvshowsToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'tvshows&url=traktwatchlist', 'trakt.png', 'trakt.png', context=(32551, 'tvshowsToLibrary&url=traktwatchlist'))
            self.addDirectoryItem(32041, 'episodesUserlists', 'userlists.png', 'userlists.png')

            if traktIndicators is True:
                self.addDirectoryItem(35308, 'episodesUnfinished', 'trakt.png', 'trakt.png', queue=True)
                self.addDirectoryItem(32036, 'calendar&url=trakthistory', 'trakt.png', 'trakt.png', queue=True)
                self.addDirectoryItem(32037, 'calendar&url=progress', 'trakt.png', 'trakt.png', queue=True)
                self.addDirectoryItem(32027, 'calendar&url=mycalendar', 'trakt.png', 'calendar.png', queue=True)
#                self.addDirectoryItem(32032, 'tvshows&url=imdbwatchlist', 'imdb.png', 'imdb.png')  #sorts alphabetical
                self.addDirectoryItem(32033, 'tvshows&url=imdbwatchlist2', 'imdb.png', 'imdb.png')  # sorts by date added

        elif traktCredentials is True:
            self.addDirectoryItem(32032, 'tvshows&url=traktcollection', 'trakt.png', 'trakt.png', context=(32551, 'tvshowsToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'tvshows&url=traktwatchlist', 'trakt.png', 'trakt.png', context=(32551, 'tvshowsToLibrary&url=traktwatchlist'))
            self.addDirectoryItem(32041, 'episodesUserlists', 'trakt.png', 'trakt.png')

            if traktIndicators is True:
                self.addDirectoryItem(35308, 'episodesUnfinished', 'trakt.png', 'trakt.png', queue=True)
                self.addDirectoryItem(32036, 'calendar&url=trakthistory', 'trakt.png', 'trakt.png', queue=True)
                self.addDirectoryItem(32037, 'calendar&url=progress', 'trakt.png', 'trakt.png', queue=True)
                self.addDirectoryItem(32027, 'calendar&url=mycalendar', 'trakt.png', 'calendar.png', queue=True)

        elif imdbCredentials is True:
#            self.addDirectoryItem(32032, 'tvshows&url=imdbwatchlist', 'imdb.png', 'imdb.png')    #sorts alphabetical
            self.addDirectoryItem(32033, 'tvshows&url=imdbwatchlist2', 'imdb.png', 'imdb.png')  # sorts by date added

        if lite is False:
            self.addDirectoryItem(32031, 'tvliteNavigator', 'tvshows.png', 'tvshows.png')
            self.addDirectoryItem(32028, 'tvPerson', 'people-search.png', 'people-search.png')
            self.addDirectoryItem(32010, 'tvSearch', 'search.png', 'search.png')
        self.endDirectory()


    def tools(self):
        self.addDirectoryItem(32510, 'cfNavigator', 'tools.png', 'tools.png')
        self.addDirectoryItem(32609, 'urlResolver', 'urlresolver.png', 'urlresolver.png')
        #-- Providers - 4
        self.addDirectoryItem(32651, 'openscrapersSettings&query=0.0', 'OpenScrapers.png', 'OpenScrapers.png')
        #-- General - 0
        self.addDirectoryItem(32043, 'openSettings&query=0.1', 'tools.png', 'tools.png')
        #-- Navigation - 1
        self.addDirectoryItem(32362, 'openSettings&query=1.0', 'tools.png', 'tools.png')
        #-- Playback - 3
        self.addDirectoryItem(32045, 'openSettings&query=3.0', 'tools.png', 'tools.png')
        #-- Api-keys - 8
        self.addDirectoryItem(32044, 'openSettings&query=8.0', 'tools.png', 'tools.png')
        #-- Downloads - 10
        self.addDirectoryItem(32048, 'openSettings&query=10.0', 'tools.png', 'tools.png')
        #-- Subtitles - 11
        self.addDirectoryItem(32046, 'openSettings&query=11.0', 'tools.png', 'tools.png')
        self.addDirectoryItem(32556, 'libraryNavigator', 'tools.png', 'tools.png')
        self.addDirectoryItem(32049, 'viewsNavigator', 'tools.png', 'tools.png')
        self.addDirectoryItem(32361, 'resetViewTypes', 'tools.png', 'tools.png')
        self.addDirectoryItem(32073, 'authTrakt&opensettings=false', 'trakt.png', 'tools.png')
        self.endDirectory()


    def cf(self):
        self.addDirectoryItem(32610, 'clearAllCache', 'tools.png', 'tools.png')
        self.addDirectoryItem(32611, 'clearSources&opensettings=false', 'tools.png', 'tools.png')
        self.addDirectoryItem(32612, 'clearMetaCache', 'tools.png', 'tools.png')
        self.addDirectoryItem(32613, 'clearCache', 'tools.png', 'tools.png')
        self.addDirectoryItem(32614, 'clearCacheSearch', 'tools.png', 'tools.png')
        self.addDirectoryItem(32615, 'clearBookmarks', 'tools.png', 'tools.png')
        self.endDirectory()


    def library(self):
#-- Library - 9
        self.addDirectoryItem(32557, 'openSettings&query=9.0', 'tools.png', 'tools.png')
        self.addDirectoryItem(32558, 'updateLibrary&query=tool', 'library_update.png', 'library_update.png')
        self.addDirectoryItem(32559, control.setting('library.movie'), 'movies.png', 'movies.png', isAction=False)
        self.addDirectoryItem(32560, control.setting('library.tv'), 'tvshows.png', 'tvshows.png', isAction=False)
        if trakt.getTraktCredentialsInfo():
            self.addDirectoryItem(32561, 'moviesToLibrary&url=traktcollection', 'trakt.png', 'movies.png')
            self.addDirectoryItem(32562, 'moviesToLibrary&url=traktwatchlist', 'trakt.png', 'movies.png')
            self.addDirectoryItem(32563, 'tvshowsToLibrary&url=traktcollection', 'trakt.png', 'tvshows.png')
            self.addDirectoryItem(32564, 'tvshowsToLibrary&url=traktwatchlist', 'trakt.png', 'tvshows.png')
        self.endDirectory()


    def downloads(self):
        movie_downloads = control.setting('movie.download.path')
        tv_downloads = control.setting('tv.download.path')
        if len(control.listDir(movie_downloads)[0]) > 0:
            self.addDirectoryItem(32001, movie_downloads, 'movies.png', 'DefaultMovies.png', isAction=False)
        if len(control.listDir(tv_downloads)[0]) > 0:
            self.addDirectoryItem(32002, tv_downloads, 'tvshows.png', 'DefaultTVShows.png', isAction=False)
        self.endDirectory()


    def search(self):
        self.addDirectoryItem(32001, 'movieSearch', 'search.png', 'DefaultMovies.png')
        self.addDirectoryItem(32002, 'tvSearch', 'search.png', 'DefaultTVShows.png')
        self.addDirectoryItem(32029, 'moviePerson', 'people-search.png', 'DefaultMovies.png')
        self.addDirectoryItem(32030, 'tvPerson', 'people-search.png', 'DefaultTVShows.png')
        self.endDirectory()


    def views(self):
        try:
            control.idle()
            items = [ (control.lang(32001).encode('utf-8'), 'movies'), (control.lang(32002).encode('utf-8'), 'tvshows'),
                            (control.lang(32054).encode('utf-8'), 'seasons'), (control.lang(32038).encode('utf-8'), 'episodes') ]

            select = control.selectDialog([i[0] for i in items], control.lang(32049).encode('utf-8'))

            if select == -1:
                return

            content = items[select][1]
            title = control.lang(32059).encode('utf-8')
            url = '%s?action=addView&content=%s' % (sys.argv[0], content)
            poster, banner, fanart = control.addonPoster(), control.addonBanner(), control.addonFanart()
            item = control.item(label=title)
            item.setInfo(type='video', infoLabels = {'title': title})
            item.setArt({'icon': poster, 'thumb': poster, 'poster': poster, 'banner': banner})
            item.setProperty('Fanart_Image', fanart)
            control.addItem(handle = int(sys.argv[1]), url=url, listitem=item, isFolder=False)
            control.content(int(sys.argv[1]), content)
            control.directory(int(sys.argv[1]), cacheToDisc=True)
            from resources.lib.modules import views
            views.setView(content, {})
        except:
            return


    def accountCheck(self):
        if traktCredentials is False and imdbCredentials is False:
            control.idle()
            control.notification(title='default', message=32042, icon='WARNING', sound=True)
            sys.exit()


    def infoCheck(self, version):
        try:
            control.notification(title='default', message=32074, icon='WARNING',  time=5000, sound=True)
            return '1'
        except:
            return '1'


    def clearCacheAll(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')

        if not yes:
            return

        try:
            from resources.lib.modules import cache
            cache.cache_clear_all()
            control.notification(title='default', message='All Cache Successfully Cleared!', icon='default', sound=True)
        except:
            import traceback
            traceback.print_exc()
            pass


    def clearCacheProviders(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')

        if not yes:
            return

        try:
            from resources.lib.modules import cache
            cache.cache_clear_providers()
            control.notification(title='default', message='Provider Cache Successfully Cleared!', icon='default', sound=True)
        except:
            import traceback
            traceback.print_exc()
            pass


    def clearCacheMeta(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')

        if not yes:
            return

        try:
            from resources.lib.modules import cache
            cache.cache_clear_meta()
            control.notification(title = 'default', message = 'Metadata Cache Successfully Cleared!', icon = 'default', sound = True)
        except:
            import traceback
            traceback.print_exc()
            pass


    def clearCache(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')

        if not yes:
            return

        try:
            from resources.lib.modules import cache
            cache.cache_clear()
            control.notification(title = 'default', message = 'Cache Successfully Cleared!', icon = 'default', sound = True)
        except:
            import traceback
            traceback.print_exc()
            pass


    def clearCacheSearch(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')

        if not yes:
            return

        try:
            from resources.lib.modules import cache
            cache.cache_clear_search()
            control.notification(title = 'default', message = 'Search History Successfully Cleared!', icon = 'default', sound = True)
        except:
            import traceback
            traceback.print_exc()
            pass


    def clearBookmarks(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')

        if not yes:
            return

        try:
            from resources.lib.modules import cache
            cache.cache_clear_bookmarks()
            control.notification(title = 'default', message = 'Bookmarks Successfully Cleared!', icon = 'default', sound = True)
        except:
            import traceback
            traceback.print_exc()
            pass


    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, isPlayable=False):
        try:
            if type(name) is str or type(name) is unicode:
                name = str(name)
            if type(name) is int:
                name = control.lang(name).encode('utf-8')
        except:
            import traceback
            traceback.print_exc()

        url = '%s?action=%s' % (sysaddon, query) if isAction else query

        thumb = os.path.join(artPath, thumb) if not artPath is None else icon

        if not icon.startswith('Default'):
             icon = os.path.join(artPath, icon)

        cm = []
        queueMenu = control.lang(32065).encode('utf-8')

        if queue is True:
            cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))

        if not context is None:
            cm.append((control.lang(context[0]).encode('utf-8'), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))

        cm.append(('[COLOR red]Venom Settings[/COLOR]', 'RunPlugin(%s?action=openSettings&query=0.0)' % sysaddon))

        item = control.item(label=name)
        item.addContextMenuItems(cm)

        if isPlayable:
            item.setProperty('IsPlayable', 'true')
        else:
            item.setProperty('IsPlayable', 'false')

        item.setArt({'icon': icon, 'poster': icon, 'thumb': thumb})

        if not addonFanart is None:
            item.setProperty('Fanart_Image', addonFanart)

        control.addItem(handle=syshandle, url=url, listitem=item, isFolder= isFolder)


    def endDirectory(self):
        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=True)
        control.sleep(200)
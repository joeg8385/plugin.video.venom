# -*- coding: utf-8 -*-

'''
    Venom Add-on
'''

import os, base64, sys, urllib2, urlparse
import xbmc, xbmcaddon, xbmcgui

from resources.lib.modules import control
from resources.lib.modules import trakt
from resources.lib.modules import cache

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])
artPath = control.artPath() ; addonFanart = control.addonFanart()

imdbCredentials = False if control.setting('imdb.user') == '' else True
traktCredentials = trakt.getTraktCredentialsInfo()
traktIndicators = trakt.getTraktIndicatorsInfo()


class navigator:
    ADDON_ID      = xbmcaddon.Addon().getAddonInfo('id')
    HOMEPATH      = xbmc.translatePath('special://home/')
    ADDONSPATH    = os.path.join(HOMEPATH, 'addons')
    THISADDONPATH = os.path.join(ADDONSPATH, ADDON_ID)
    NEWSFILE      = 'https://raw.githubusercontent.com/123Venom/zips/master/plugin.video.venom/newsinfo.txt'
    LOCALNEWS     = os.path.join(THISADDONPATH, 'newsinfo.txt')


    def root(self):
        self.addDirectoryItem(32001, 'movieNavigator', 'movies.png', 'movies.png')
        self.addDirectoryItem(32002, 'tvNavigator', 'tvshows.png', 'tvshows.png')

        if self.getMenuEnabled('mylists.widget') == True:
            self.addDirectoryItem(32003, 'mymovieNavigator', 'mymovies.png', 'mymovies.png')
            self.addDirectoryItem(32004, 'mytvNavigator', 'mytvshows.png', 'mytvshows.png')

        if not control.setting('newmovies.widget') == '0':
            self.addDirectoryItem(32005, 'newMovies', 'latest-movies.png', 'latest-movies.png')

        if (traktIndicators == True and not control.setting('tv.widget.alt') == '0') or (traktIndicators == False and not control.setting('tv.widget') == '0'):
            self.addDirectoryItem(32006, 'tvWidget', 'latest-episodes.png', 'DefaultRecentlyAddedEpisodes.png')
            self.addDirectoryItem('Recently Aired', 'calendar&url=added', 'latest-episodes.png', 'DefaultRecentlyAddedEpisodes.png', queue=True)

        if not control.setting('furk.api') == '' or None:
            self.addDirectoryItem('Furk.net', 'furkNavigator', 'movies.png', 'movies.png')

        self.addDirectoryItem(32010, 'searchNavigator', 'search.png', 'DefaultFolder.png')
        self.addDirectoryItem(32008, 'toolNavigator', 'tools.png', 'DefaultAddonProgram.png')

        downloads = True if control.setting('downloads') == 'true' and (len(control.listDir(control.setting('movie.download.path'))[0]) > 0 or len(control.listDir(control.setting('tv.download.path'))[0]) > 0) else False
        if downloads == True:
            self.addDirectoryItem(32009, 'downloadNavigator', 'downloads.png', 'DefaultFolder.png')

        self.addDirectoryItem('News and Info!!', 'newsNavigator', 'icon.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem('Change Log!!', 'ShowChangelog', 'icon.png', 'DefaultAddonProgram.png')
        self.endDirectory()


    def furk(self):
        self.addDirectoryItem('User Files', 'furkUserFiles', 'mytvnavigator.png', 'mytvnavigator.png')
        self.addDirectoryItem('Search', 'furkSearch', 'search.png', 'search.png')
        self.endDirectory()


    def getMenuEnabled(self, menu_title):
        is_enabled = control.setting(menu_title).strip()
        if (is_enabled == '' or is_enabled == 'false'): return False
        return True


# News and Info
    def news(self):
            message = self.open_news_url(self.NEWSFILE)
            r = open(self.LOCALNEWS)
            compfile = r.read()
            if len(message) > 1:
                    if compfile == message: pass
                    else:
                            text_file = open(self.LOCALNEWS, "w")
                            text_file.write(message)
                            text_file.close()
                            compfile = message
            self.showText('[B][COLOR red]Update Information[/COLOR][/B]', compfile)


    def open_news_url(self, url):
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'klopp')
            response = urllib2.urlopen(req)
            link = response.read()
            response.close()
            print link
            return link


    def news_local(self):
            r = open(self.LOCALNEWS)
            compfile = r.read()
            self.showText('[B]Updates and Information[/B]', compfile)


    def showText(self, heading, text):
        id = 10147
        xbmc.executebuiltin('ActivateWindow(%d)' % id)
        xbmc.sleep(500)
        win = xbmcgui.Window(id)
        retry = 50
        while (retry > 0):
            try:
                xbmc.sleep(10)
                retry -= 1
                win.getControl(1).setLabel(heading)
                win.getControl(5).setText(text)
                quit()
                return
            except: pass


    def movies(self, lite=False):
        self.addDirectoryItem(32022, 'movies&url=theaters', 'imdb.png', 'in-theaters.png')
        self.addDirectoryItem('Now Playing', 'tmdbmovies&url=tmdb_nowplaying', 'tmdb.png', 'in-theaters.png')

        self.addDirectoryItem('Anticipated', 'movies&url=traktanticipated', 'trakt.png', 'DefaultMovies.png')
        self.addDirectoryItem('Upcoming', 'tmdbmovies&url=tmdb_upcoming', 'tmdb.png', 'DefaultMovies.png')

        self.addDirectoryItem(32018, 'movies&url=mostpopular', 'imdb.png', 'most-popular.png')
        self.addDirectoryItem('Popular', 'tmdbmovies&url=tmdb_popular', 'tmdb.png', 'most-popular.png')
        self.addDirectoryItem('Popular', 'movies&url=traktpopular', 'trakt.png', 'most-popular.png')

        self.addDirectoryItem(32019, 'movies&url=mostvoted', 'imdb.png', 'most-voted.png')
        self.addDirectoryItem('Top Rated', 'tmdbmovies&url=tmdb_toprated', 'tmdb.png', 'most-voted.png')
        self.addDirectoryItem(32017, 'movies&url=trakttrending', 'trakt.png', 'most-voted.png')

        self.addDirectoryItem(33662, 'movies&url=traktrecommendations', 'trakt.png', 'people-watching.png')
        self.addDirectoryItem(32035, 'movies&url=featured', 'imdb.png', 'people-watching.png')

        if not control.setting('newmovies.widget') == '0':
            self.addDirectoryItem(32005, 'newMovies', 'imdb.png', 'latest-movies.png')

        self.addDirectoryItem(32020, 'movies&url=imdbboxoffice', 'imdb.png', 'box-office.png')
        # self.addDirectoryItem('Box Office', 'movies&url=traktboxoffice', 'trakt.png', 'box-office.png')

        self.addDirectoryItem(32000, 'collectionsNavigator', 'boxsets.png', 'boxsets.png')
        self.addDirectoryItem(32021, 'movies&url=oscars', 'imdb.png', 'oscar-winners.png')
        self.addDirectoryItem(32659, 'movies&url=oscarsnominees', 'imdb.png', 'oscar-winners.png')
        self.addDirectoryItem(32011, 'movieGenres', 'imdb.png', 'genres.png')
        self.addDirectoryItem(32012, 'movieYears', 'imdb.png', 'years.png')
        self.addDirectoryItem(32013, 'moviePersons', 'imdb.png', 'people.png')
        self.addDirectoryItem(32014, 'movieLanguages', 'imdb.png', 'languages.png')
        self.addDirectoryItem(32015, 'movieCertificates', 'imdb.png', 'certificates.png')

        if lite == False:
            if self.getMenuEnabled('mylists.widget') == True:
               self.addDirectoryItem(32003, 'mymovieliteNavigator', 'mymovies.png', 'DefaultVideoPlaylists.png')
            self.addDirectoryItem(32028, 'moviePerson', 'people-search.png', 'DefaultMovies.png')
            self.addDirectoryItem(32010, 'movieSearch', 'search.png', 'DefaultMovies.png')
        self.endDirectory()


    def mymovies(self, lite=False):
        self.accountCheck()
        self.addDirectoryItem(32039, 'movieUserlists', 'userlists.png', 'userlists.png')
        # self.addDirectoryItem(33662, 'movies&url=traktrecommendations', 'trakt.png', 'trakt.png', queue = True)

        if traktCredentials == True and imdbCredentials == True:
            self.addDirectoryItem(32032, 'movies&url=traktcollection', 'trakt.png', 'trakt.png', queue = True, context=(32551, 'moviesToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'movies&url=traktwatchlist', 'trakt.png', 'trakt.png', queue = True, context=(32551, 'moviesToLibrary&url=traktwatchlist'))

            if traktIndicators == True:
                self.addDirectoryItem(35308, 'movies&url=traktunfinished', 'trakt.png', 'trakt.png', queue = True)
                self.addDirectoryItem(32036, 'movies&url=trakthistory', 'trakt.png', 'trakt.png', queue = True)
                self.addDirectoryItem(32033, 'movies&url=imdbwatchlist2', 'imdb.png', 'imdb.png', queue = True)

        elif traktCredentials == True:
            self.addDirectoryItem(32032, 'movies&url=traktcollection', 'trakt.png', 'trakt.png', queue = True, context=(32551, 'moviesToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'movies&url=traktwatchlist', 'trakt.png', 'trakt.png', queue = True, context=(32551, 'moviesToLibrary&url=traktwatchlist'))

            if traktIndicators == True:
                self.addDirectoryItem(35308, 'movies&url=traktunfinished', 'trakt.png', 'trakt.png', queue = True)
                self.addDirectoryItem(32036, 'movies&url=trakthistory', 'trakt.png', 'trakt.png', queue = True)

        elif imdbCredentials == True:
#            self.addDirectoryItem(32032, 'movies&url=imdbwatchlist', 'imdb.png', 'imdb.png', queue = True)
            self.addDirectoryItem(32033, 'movies&url=imdbwatchlist2', 'imdb.png', 'imdb.png', queue = True)

        if lite == False:
            self.addDirectoryItem(32031, 'movieliteNavigator', 'movies.png', 'movies.png')
            self.addDirectoryItem(32028, 'moviePerson', 'people-search.png', 'people-search.png')
            self.addDirectoryItem(32010, 'movieSearch', 'search.png', 'search.png')
        self.endDirectory()


    def tvshows(self, lite = False):
        self.addDirectoryItem(32050, 'tvshows&url=popular', 'imdb.png', 'most-popular.png')
        self.addDirectoryItem(32050, 'tmdbTvshows&url=tmdb_popular', 'tmdb.png', 'most-popular.png')
        self.addDirectoryItem(32050, 'tvshows&url=traktpopular', 'trakt.png', 'most-popular.png', queue = True)
        self.addDirectoryItem(32019, 'tvshows&url=views', 'imdb.png', 'most-voted.png')
        self.addDirectoryItem(32051, 'tmdbTvshows&url=tmdb_toprated', 'tmdb.png', 'most-voted.png')
        self.addDirectoryItem(32017, 'tvshows&url=trakttrending', 'trakt.png', 'trakt.png')
        self.addDirectoryItem(32023, 'tvshows&url=rating', 'imdb.png', 'highly-rated.png')
        self.addDirectoryItem(33662, 'tvshows&url=traktrecommendations', 'trakt.png', 'trakt.png', queue = True)
        self.addDirectoryItem(32011, 'tvGenres', 'genres.png', 'genres.png')
        self.addDirectoryItem(32016, 'tvNetworks', 'networks.png', 'networks.png')
        self.addDirectoryItem(32014, 'tvLanguages', 'languages.png', 'languages.png')
        self.addDirectoryItem(32015, 'tvCertificates', 'certificates.png', 'certificates.png')
        self.addDirectoryItem("Trakt On Deck", 'calendar&url=onDeck', 'trakt.png', 'DefaultTVShows.png')
        self.addDirectoryItem(32364, 'tmdbTvshows&url=tmdb_airingtoday', 'tmdb.png', 'airing-today.png')
        self.addDirectoryItem(32024, 'tvshows&url=airing', 'imdb.png', 'airing-today.png')
        self.addDirectoryItem(32052, 'tmdbTvshows&url=tmdb_ontheair', 'tmdb.png', 'returning-tvshows.png')
        self.addDirectoryItem(32025, 'tvshows&url=active', 'imdb.png', 'returning-tvshows.png')
        self.addDirectoryItem(32026, 'tvshows&url=premiere', 'imdb.png', 'new-tvshows.png')
        self.addDirectoryItem(32027, 'calendars', 'calendar.png', 'calendar.png')

        if (traktIndicators == True and not control.setting('tv.widget.alt') == '0') or (traktIndicators == False and not control.setting('tv.widget') == '0'):
            self.addDirectoryItem(32006, 'tvWidget', 'latest-episodes.png', 'DefaultRecentlyAddedEpisodes.png')

        if lite == False:
            if self.getMenuEnabled('mylists.widget') == True:
               self.addDirectoryItem(32004, 'mytvliteNavigator', 'mytvshows.png', 'DefaultVideoPlaylists.png')

            self.addDirectoryItem(32028, 'tvPerson', 'people-search.png', 'DefaultTVShows.png')
            self.addDirectoryItem(32010, 'tvSearch', 'search.png', 'DefaultTVShows.png')
        self.endDirectory()


    def mytvshows(self, lite = False):
        self.accountCheck()
        self.addDirectoryItem(32040, 'tvUserlists', 'userlists.png', 'DefaultTVShows.png')
        if traktCredentials == True and imdbCredentials == True:
            self.addDirectoryItem(32032, 'tvshows&url=traktcollection', 'trakt.png', 'DefaultTVShows.png', context=(32551, 'tvshowsToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'tvshows&url=traktwatchlist', 'trakt.png', 'DefaultTVShows.png', context=(32551, 'tvshowsToLibrary&url=traktwatchlist'))
            self.addDirectoryItem(32041, 'episodesUserlists', 'userlists.png', 'DefaultTVShows.png')

            if traktIndicators == True:
                self.addDirectoryItem(35308, 'episodesUnfinished', 'trakt.png', 'DefaultTVShows.png', queue = True)
                self.addDirectoryItem(32036, 'calendar&url=trakthistory', 'trakt.png', 'DefaultTVShows.png', queue = True)
                self.addDirectoryItem(32037, 'calendar&url=progress', 'trakt.png', 'DefaultRecentlyAddedEpisodes.png', queue = True)
                self.addDirectoryItem(32027, 'calendar&url=mycalendar', 'trakt.png', 'DefaultRecentlyAddedEpisodes.png', queue = True)
#                self.addDirectoryItem(32032, 'tvshows&url=imdbwatchlist', 'imdb.png', 'DefaultTVShows.png')  #sorts alphabetical
                self.addDirectoryItem(32033, 'tvshows&url=imdbwatchlist2', 'imdb.png', 'DefaultTVShows.png')  # sorts by date added

        elif traktCredentials == True:
            self.addDirectoryItem(32032, 'tvshows&url=traktcollection', 'trakt.png', 'DefaultTVShows.png', context=(32551, 'tvshowsToLibrary&url=traktcollection'))
            self.addDirectoryItem(32033, 'tvshows&url=traktwatchlist', 'trakt.png', 'DefaultTVShows.png', context=(32551, 'tvshowsToLibrary&url=traktwatchlist'))
            self.addDirectoryItem(32041, 'episodesUserlists', 'trakt.png', 'DefaultTVShows.png')

            if traktIndicators == True:
                self.addDirectoryItem(35308, 'episodesUnfinished', 'trakt.png', 'DefaultTVShows.png', queue = True)
                self.addDirectoryItem(32036, 'calendar&url=trakthistory', 'trakt.png', 'DefaultTVShows.png', queue = True)
                self.addDirectoryItem(32037, 'calendar&url=progress', 'trakt.png', 'DefaultRecentlyAddedEpisodes.png', queue = True)
                self.addDirectoryItem(32027, 'calendar&url=mycalendar', 'trakt.png', 'DefaultRecentlyAddedEpisodes.png', queue = True)

        elif imdbCredentials == True:
#            self.addDirectoryItem(32032, 'tvshows&url=imdbwatchlist', 'imdb.png', 'DefaultTVShows.png')    #sorts alphabetical
            self.addDirectoryItem(32033, 'tvshows&url=imdbwatchlist2', 'imdb.png', 'DefaultTVShows.png')  # sorts by date added

        if lite == False:
            self.addDirectoryItem(32031, 'tvliteNavigator', 'tvshows.png', 'DefaultTVShows.png')
            self.addDirectoryItem(32028, 'tvPerson', 'people-search.png', 'DefaultTVShows.png')
            self.addDirectoryItem(32010, 'tvSearch', 'search.png', 'DefaultTVShows.png')
        self.endDirectory()


    def tools(self):
        self.addDirectoryItem('[B]Cache Functions[/B]', 'cfNavigator', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32609, 'urlResolver', 'urlresolver.png', 'DefaultAddonProgram.png')
        # Providers - 4
        self.addDirectoryItem(32651, 'openscrapersSettings&query=0.0', 'OpenScrapers.png', 'DefaultAddonProgram.png')
        # General - 0
        self.addDirectoryItem(32043, 'openSettings&query=0.1', 'tools.png', 'DefaultAddonProgram.png')
        # Playback - 2
        self.addDirectoryItem(32045, 'openSettings&query=2.0', 'tools.png', 'DefaultAddonProgram.png')
        # Api-keys - 7
        self.addDirectoryItem(32044, 'openSettings&query=7.0', 'tools.png', 'DefaultAddonProgram.png')
        # Downloads - 9
        self.addDirectoryItem(32048, 'openSettings&query=9.0', 'tools.png', 'DefaultAddonProgram.png')
        # Subtitles - 10
        self.addDirectoryItem(32046, 'openSettings&query=10.0', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32556, 'libraryNavigator', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32049, 'viewsNavigator', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32073, 'authTrakt&opensettings=false', 'trakt.png', 'DefaultAddonProgram.png')
        self.endDirectory()


    def cf(self):
        self.addDirectoryItem(32610, 'clearAllCache', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32611, 'clearSources&opensettings=false', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32612, 'clearMetaCache', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32613, 'clearCache', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32614, 'clearCacheSearch', 'tools.png', 'DefaultAddonProgram.png')
        self.endDirectory()


    def library(self):
        self.addDirectoryItem(32557, 'openSettings&query=8.0', 'tools.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32558, 'updateLibrary&query=tool', 'library_update.png', 'DefaultAddonProgram.png')
        self.addDirectoryItem(32559, control.setting('library.movie'), 'movies.png', 'DefaultMovies.png', isAction = False)
        self.addDirectoryItem(32560, control.setting('library.tv'), 'tvshows.png', 'DefaultTVShows.png', isAction = False)
        if trakt.getTraktCredentialsInfo():
            self.addDirectoryItem(32561, 'moviesToLibrary&url=traktcollection', 'trakt.png', 'DefaultMovies.png')
            self.addDirectoryItem(32562, 'moviesToLibrary&url=traktwatchlist', 'trakt.png', 'DefaultMovies.png')
            self.addDirectoryItem(32563, 'tvshowsToLibrary&url=traktcollection', 'trakt.png', 'DefaultTVShows.png')
            self.addDirectoryItem(32564, 'tvshowsToLibrary&url=traktwatchlist', 'trakt.png', 'DefaultTVShows.png')
        self.endDirectory()


    def downloads(self):
        movie_downloads = control.setting('movie.download.path')
        tv_downloads = control.setting('tv.download.path')
        if len(control.listDir(movie_downloads)[0]) > 0:
            self.addDirectoryItem(32001, movie_downloads, 'movies.png', 'DefaultMovies.png', isAction = False)
        if len(control.listDir(tv_downloads)[0]) > 0:
            self.addDirectoryItem(32002, tv_downloads, 'tvshows.png', 'DefaultTVShows.png', isAction = False)
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
            items = [ (control.lang(32001).encode('utf-8'), 'movies'), (control.lang(32002).encode('utf-8'), 'tvshows'), (control.lang(32054).encode('utf-8'), 'seasons'), (control.lang(32038).encode('utf-8'), 'episodes') ]
            select = control.selectDialog([i[0] for i in items], control.lang(32049).encode('utf-8'))
            if select == -1: return
            content = items[select][1]
            title = control.lang(32059).encode('utf-8')
            url = '%s?action=addView&content=%s' % (sys.argv[0], content)
            poster, banner, fanart = control.addonPoster(), control.addonBanner(), control.addonFanart()
            item = control.item(label=title)
            item.setInfo(type = 'Video', infoLabels = {'title': title})
            item.setArt({'icon': poster, 'thumb': poster, 'poster': poster, 'banner': banner})
            item.setProperty('Fanart_Image', fanart)
            control.addItem(handle = int(sys.argv[1]), url = url, listitem = item, isFolder = False)
            control.content(int(sys.argv[1]), content)
            control.directory(int(sys.argv[1]), cacheToDisc = True)
            from resources.lib.modules import views
            views.setView(content, {})
        except:
            return


    def accountCheck(self):
        if traktCredentials == False and imdbCredentials == False:
            control.idle()
            control.notification(title = 'default', message = 32042, icon = 'WARNING', sound = True)
            sys.exit()


    def infoCheck(self, version):
        try:
            control.notification(title = 'default', message = 32074, icon = 'WARNING',  time = 5000, sound = True)
            return '1'
        except:
            return '1'


    def clearCacheAll(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')
        if not yes: return
        from resources.lib.modules import cache
        cache.cache_clear_all()
        control.notification(title = 'default', message = 'All Cache Successfully Cleared!', icon = 'default', sound = True)


    def clearCacheProviders(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')
        if not yes: return
        from resources.lib.modules import cache
        cache.cache_clear_providers()
        control.notification(title = 'default', message = 'Provider Cache Successfully Cleared!', icon = 'default', sound = True)


    def clearCacheMeta(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')
        if not yes: return
        from resources.lib.modules import cache
        cache.cache_clear_meta()
        control.notification(title = 'default', message = 'Metadata Cache Successfully Cleared!', icon = 'default', sound = True)


    def clearCache(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')
        if not yes: return
        from resources.lib.modules import cache
        cache.cache_clear()
        control.notification(title = 'default', message = 'Cache Successfully Cleared!', icon = 'default', sound = True)


    def clearCacheSearch(self):
        control.idle()
        yes = control.yesnoDialog(control.lang(32056).encode('utf-8'), '', '')
        if not yes: return
        from resources.lib.modules import cache
        cache.cache_clear_search()
        control.notification(title = 'default', message = 'Search History Successfully Cleared!', icon = 'default', sound = True)


    def addDirectoryItem(self, name, query, thumb, icon, context = None, queue = False, isAction = True, isFolder = True):
        try: name = control.lang(name).encode('utf-8')
        except: pass
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query

        thumb = os.path.join(artPath, thumb) if not artPath == None else icon

        cm = []
        queueMenu = control.lang(32065).encode('utf-8')

        if queue == True: cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
        if not context == None: cm.append((control.lang(context[0]).encode('utf-8'), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
        cm.append(('[COLOR red]Venom Settings[/COLOR]', 'RunPlugin(%s?action=openSettings&query=(0,0))' % sysaddon))

        item = control.item(label = name)
        item.addContextMenuItems(cm)

        item.setArt({'icon': icon, 'thumb': thumb})
        if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
        control.addItem(handle=syshandle, url=url, listitem=item, isFolder= isFolder)


    def endDirectory(self):
        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc = True)

# -*- coding: utf-8 -*-

'''
Venom
'''

import os, sys, re, datetime, xbmc
import urllib, urlparse, json

from resources.lib.modules import trakt
from resources.lib.modules import cleangenre
from resources.lib.modules import control
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import metacache
from resources.lib.modules import playcount
from resources.lib.modules import workers
from resources.lib.modules import views

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])
artPath = control.artPath() ; addonFanart = control.addonFanart()

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?',''))) if len(sys.argv) > 1 else dict()
action = params.get('action')


class collections:
    def __init__(self):
        self.list = []

        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
        self.systime = (self.datetime).strftime('%Y%m%d%H%M%S%f')
        self.today_date = (self.datetime).strftime('%Y-%m-%d')
        self.month_date = (self.datetime - datetime.timedelta(days = 30)).strftime('%Y-%m-%d')
        self.year_date = (self.datetime - datetime.timedelta(days = 365)).strftime('%Y-%m-%d')

        self.imdb_link = 'https://www.imdb.com'
        self.imdb_user = control.setting('imdb.user').replace('ur', '')
        # self.imdbinfo = 'https://www.omdbapi.com/?i=%s&plot=short&r=json'

        self.lang = control.apiLanguage()['trakt']

        self.tmdb_key = control.setting('tm.user')
        if self.tmdb_key == '' or self.tmdb_key == None:
            self.tmdb_key = '3320855e65a9758297fec4f7c9717698'

        self.tmdb_link = 'https://api.themoviedb.org'
        self.tmdb_api_link = 'https://api.themoviedb.org/3/list/%s?api_key=%s' % ('%s', '%s')
        # self.tmdb_info_link = 'https://api.themoviedb.org/3/movie/%s?api_key=%s&language=%s&append_to_response=credits,releases,external_ids' % ('%s', self.tmdb_key, self.lang)
        self.tmdb_art_link = 'http://api.themoviedb.org/3/movie/%s/images?api_key=%s&include_image_language=en,%s,null' % ('%s', self.tmdb_key, self.lang)
        self.tmdb_background_path = 'http://image.tmdb.org/t/p/w1280'
        self.tmdb_poster_path = "https://image.tmdb.org/t/p/w500"

        # self.tmdb_img_link = 'https://image.tmdb.org/t/p/w%s%s'

        self.fanart_tv_user = control.setting('fanart.tv.user')
        if self.fanart_tv_user == '' or self.fanart_tv_user == None:
            self.fanart_tv_user = 'cf0ebcc2f7b824bd04cf3a318f15c17d'
        self.user = str('self.fanart_tv_user') + str(control.setting('tm.user'))
        self.fanart_tv_art_link = 'http://webservice.fanart.tv/v3/movies/%s'
        self.fanart_tv_level_link = 'http://webservice.fanart.tv/v3/level'

        self.imdblists_link = 'https://www.imdb.com/user/ur%s/lists?tab=all&sort=mdfd&order=desc&filter=titles' % self.imdb_user
        self.imdblist_link = 'https://www.imdb.com/list/%s/?view=detail&sort=alpha,asc&title_type=movie,short,tvMovie,tvSpecial,video&start=1'
        self.imdblist2_link = 'https://www.imdb.com/list/%s/?view=detail&sort=date_added,desc&title_type=movie,short,tvMovie,tvSpecial,video&start=1'
        self.imdbwatchlist_link = 'https://www.imdb.com/user/ur%s/watchlist?sort=alpha,asc' % self.imdb_user
        self.imdbwatchlist2_link = 'https://www.imdb.com/user/ur%s/watchlist?sort=date_added,desc' % self.imdb_user


# Christmas Movies
        self.xmasmovies_link = 'https://api.themoviedb.org/3/list/32770?api_key=%s' % (self.tmdb_key)

# DC Comics Movies
        self.dcmovies_link = 'https://api.themoviedb.org/3/list/32799?api_key=%s' % (self.tmdb_key)

# Disney Movies
        self.disneymovies_link = 'https://api.themoviedb.org/3/list/32800?api_key=%s' % (self.tmdb_key)

# Kids Movies
        self.kidsmovies_link = 'https://api.themoviedb.org/3/list/32802?api_key=%s' % (self.tmdb_key)

# Marvel Movies
        self.marvelmovies_link = 'https://api.themoviedb.org/3/list/32793?api_key=%s' % (self.tmdb_key)

# Boxset Collection
        self.rounds_link = self.tmdb_api_link % ('13120', self.tmdb_key)
        self.tmdb300_link = self.tmdb_api_link % ('13132', self.tmdb_key)
        self.fortyeighthours_link = self.tmdb_api_link % ('33259', self.tmdb_key)
        self.aceventura_link = self.tmdb_api_link % ('33260', self.tmdb_key)
        self.aceventura_link = self.tmdb_api_link % ('33260', self.tmdb_key)
        self.airplane_link = self.tmdb_api_link % ('33261', self.tmdb_key)
        self.airport_link = self.tmdb_api_link % ('33262', self.tmdb_key)
        self.americangraffiti_link = self.tmdb_api_link % ('33263', self.tmdb_key)
        self.anaconda_link = self.tmdb_api_link % ('33264', self.tmdb_key)
        self.analyzethis_link = self.tmdb_api_link % ('33265', self.tmdb_key)
        self.anchorman_link = self.tmdb_api_link % ('33266', self.tmdb_key)
        self.austinpowers_link = self.tmdb_api_link % ('33267', self.tmdb_key)
        self.backtothefuture_link = self.tmdb_api_link % ('33268', self.tmdb_key)
        self.badboys_link = self.tmdb_api_link % ('33269', self.tmdb_key)
        self.badsanta_link = self.tmdb_api_link % ('33270', self.tmdb_key)
        self.basicinstinct_link = self.tmdb_api_link % ('33271', self.tmdb_key)
        self.beverlyhillscop_link = self.tmdb_api_link % ('33272', self.tmdb_key)
        self.bigmommashouse_link = self.tmdb_api_link % ('33273', self.tmdb_key)
        self.bluesbrothers_link = self.tmdb_api_link % ('33274', self.tmdb_key)
        self.bourne_link = self.tmdb_api_link % ('33275', self.tmdb_key)
        self.brucealmighty_link = self.tmdb_api_link % ('33276', self.tmdb_key)
        self.brucelee_link = self.tmdb_api_link % ('13295', self.tmdb_key)
        self.caddyshack_link = self.tmdb_api_link % ('33277', self.tmdb_key)
        self.cheaperbythedozen_link = self.tmdb_api_link % ('33278', self.tmdb_key)
        self.cheechandchong_link = self.tmdb_api_link % ('33420', self.tmdb_key)
        self.childsplay_link = self.tmdb_api_link % ('33279', self.tmdb_key)
        self.cityslickers_link = self.tmdb_api_link % ('33280', self.tmdb_key)
        self.conan_link = self.tmdb_api_link % ('33281', self.tmdb_key)
        self.crank_link = self.tmdb_api_link % ('33282', self.tmdb_key)
        self.crocodiledundee_link = self.tmdb_api_link % ('33419', self.tmdb_key)
        self.thecrow_link = self.tmdb_api_link % ('13294', self.tmdb_key)
        self.davincicode_link = self.tmdb_api_link % ('33283', self.tmdb_key)
        self.daddydaycare_link = self.tmdb_api_link % ('33284', self.tmdb_key)
        self.deathwish_link = self.tmdb_api_link % ('33285', self.tmdb_key)
        self.deltaforce_link = self.tmdb_api_link % ('33286', self.tmdb_key)
        self.diehard_link = self.tmdb_api_link % ('33287', self.tmdb_key)
        self.dirtydancing_link = self.tmdb_api_link % ('33288', self.tmdb_key)
        self.dirtyharry_link = self.tmdb_api_link % ('33289', self.tmdb_key)
        self.divergent_link = self.tmdb_api_link % ('13311', self.tmdb_key)
        self.dumbanddumber_link = self.tmdb_api_link % ('33290', self.tmdb_key)
        self.escapefromnewyork_link = self.tmdb_api_link % ('33291', self.tmdb_key)
        self.everywhichwaybutloose_link = self.tmdb_api_link % ('33292', self.tmdb_key)
        self.exorcist_link = self.tmdb_api_link % ('33293', self.tmdb_key)
        self.theexpendables_link = self.tmdb_api_link % ('33294', self.tmdb_key)
        self.fastandthefurious_link = self.tmdb_api_link % ('13062', self.tmdb_key)
        self.fatherofthebride_link = self.tmdb_api_link % ('33295', self.tmdb_key)
        self.fletch_link = self.tmdb_api_link % ('33296', self.tmdb_key)
        self.thefly_link = self.tmdb_api_link % ('13303', self.tmdb_key)
        self.friday_link = self.tmdb_api_link % ('33297', self.tmdb_key)
        self.fridaythe13th_link = self.tmdb_api_link % ('33298', self.tmdb_key)
        self.fugitive_link = self.tmdb_api_link % ('33299', self.tmdb_key)
        self.gijoe_link = self.tmdb_api_link % ('33300', self.tmdb_key)
        self.getshorty_link = self.tmdb_api_link % ('33301', self.tmdb_key)
        self.gettysburg_link = self.tmdb_api_link % ('33302', self.tmdb_key)
        self.ghostrider_link = self.tmdb_api_link % ('33303', self.tmdb_key)
        self.ghostbusters_link = self.tmdb_api_link % ('33201', self.tmdb_key)
        self.godsnotdead_link = self.tmdb_api_link % ('33304', self.tmdb_key)
        self.godfather_link = self.tmdb_api_link % ('33305', self.tmdb_key)
        self.godzilla_link = self.tmdb_api_link % ('33306', self.tmdb_key)
        self.grownups_link = self.tmdb_api_link % ('33307', self.tmdb_key)
        self.grumpyoldmen_link = self.tmdb_api_link % ('33308', self.tmdb_key)
        self.gunsofnavarone_link = self.tmdb_api_link % ('33309', self.tmdb_key)
        self.halloween_link = self.tmdb_api_link % ('33310', self.tmdb_key)
        self.hangover_link = self.tmdb_api_link % ('33311', self.tmdb_key)
        self.hanniballector_link = self.tmdb_api_link % ('33312', self.tmdb_key)
        self.hellraiser_link = self.tmdb_api_link % ('33313', self.tmdb_key)
        self.highlander_link = self.tmdb_api_link % ('13256', self.tmdb_key)
        self.thehobbit_link = 'https://www.imdb.com/search/title?title=the+hobbit&title_type=feature,tv_movie&num_votes=1000,&countries=us&languages=en'
        self.hollowman_link = self.tmdb_api_link % ('13251', self.tmdb_key)
        self.honeyishrunkthekids_link = self.tmdb_api_link % ('33208', self.tmdb_key)
        self.horriblebosses_link = self.tmdb_api_link % ('33314', self.tmdb_key)
        self.hostel_link = self.tmdb_api_link % ('33315', self.tmdb_key)
        self.hotshots_link = self.tmdb_api_link % ('33316', self.tmdb_key)
        self.hungergames_link = 'https://www.imdb.com/search/title?title=hunger+games&title_type=feature&num_votes=1000,&countries=us&languages=en&sort=release_date,desc'
        self.huntsman_link = self.tmdb_api_link % ('13235', self.tmdb_key)
        self.independenceday_link = self.tmdb_api_link % ('33317', self.tmdb_key)
        self.indianajones_link = self.tmdb_api_link % ('33318', self.tmdb_key)
        self.insidious_link = self.tmdb_api_link % ('33319', self.tmdb_key)
        self.ironeagle_link = self.tmdb_api_link % ('33320', self.tmdb_key)
        self.jackreacher_link = self.tmdb_api_link % ('33321', self.tmdb_key)
        self.jackryan_link = self.tmdb_api_link % ('33322', self.tmdb_key)
        self.jackass_link = self.tmdb_api_link % ('33323', self.tmdb_key)
        self.jamesbond_link = self.tmdb_api_link % ('33324', self.tmdb_key)
        self.jaws_link = self.tmdb_api_link % ('33325', self.tmdb_key)
        self.jeeperscreepers_link = self.tmdb_api_link % ('33326', self.tmdb_key)
        self.johnwick_link = self.tmdb_api_link % ('33327', self.tmdb_key)
        self.journeytocenter_link = self.tmdb_api_link % ('13216', self.tmdb_key)
        self.judgedredd_link = self.tmdb_api_link % ('13215', self.tmdb_key)
        self.jumanji_link = self.tmdb_api_link % ('33328', self.tmdb_key)
        self.jumpst_link = self.tmdb_api_link % ('13213', self.tmdb_key)
        self.jurassicpark_link = self.tmdb_api_link % ('33217', self.tmdb_key)
        self.kickass_link = self.tmdb_api_link % ('33329', self.tmdb_key)
        self.killbill_link = self.tmdb_api_link % ('33330', self.tmdb_key)

        self.kingkong_link = self.tmdb_api_link % ('113082', self.tmdb_key)
        # self.kingkong_link = self.tmdb_api_link % ('33331', self.tmdb_key)
        self.laracroft_link = self.tmdb_api_link % ('33332', self.tmdb_key)
        self.legallyblonde_link = self.tmdb_api_link % ('33333', self.tmdb_key)
        self.lethalweapon_link = self.tmdb_api_link % ('33334', self.tmdb_key)
        self.lookwhostalking_link = self.tmdb_api_link % ('33335', self.tmdb_key)
        self.lordoftherings_link = 'https://www.imdb.com/search/title?title=the+lord+of+the+rings&title_type=feature&num_votes=1000,&countries=us&languages=en'
        self.machete_link = self.tmdb_api_link % ('33336', self.tmdb_key)
        self.madmax_link = self.tmdb_api_link % ('13188', self.tmdb_key)
        self.magicmike_link = self.tmdb_api_link % ('33337', self.tmdb_key)
        self.majorleague_link = self.tmdb_api_link % ('33338', self.tmdb_key)
        self.manfromsnowyriver_link = self.tmdb_api_link % ('33339', self.tmdb_key)
        self.mask_link = self.tmdb_api_link % ('33340', self.tmdb_key)
        self.matrix_link = self.tmdb_api_link % ('33341', self.tmdb_key)
        self.mazerunner_link = self.tmdb_api_link % ('13182', self.tmdb_key)
        self.themechanic_link = self.tmdb_api_link % ('33342', self.tmdb_key)
        self.meettheparents_link = self.tmdb_api_link % ('33343', self.tmdb_key)
        self.meninblack_link = self.tmdb_api_link % ('33344', self.tmdb_key)
        self.mightyducks_link = self.tmdb_api_link % ('33345', self.tmdb_key)
        self.misscongeniality_link = self.tmdb_api_link % ('33346', self.tmdb_key)
        self.missinginaction_link = self.tmdb_api_link % ('33347', self.tmdb_key)
        self.missionimpossible_link = self.tmdb_api_link % ('33348', self.tmdb_key)
        self.themummy_link = 'https://www.imdb.com/search/title?title=mummy&title_type=feature&release_date=1999-01-01,&num_votes=1000,&countries=us&languages=en&sort=release_date,desc'
        self.nakedgun_link = self.tmdb_api_link % ('33349', self.tmdb_key)
        self.nationallampoon_link = self.tmdb_api_link % ('33350', self.tmdb_key)
        self.nationallampoonsvacation_link = self.tmdb_api_link % ('33351', self.tmdb_key)
        self.nationaltreasure_link = self.tmdb_api_link % ('33352', self.tmdb_key)
        self.neighbors_link = self.tmdb_api_link % ('33353', self.tmdb_key)
        self.nightatthemuseum_link = self.tmdb_api_link % ('33354', self.tmdb_key)
        self.nightmareonelmstreet_link = self.tmdb_api_link % ('33355', self.tmdb_key)
        self.nowyouseeme_link = self.tmdb_api_link % ('33356', self.tmdb_key)
        self.nuttyprofessor_link = self.tmdb_api_link % ('33357', self.tmdb_key)
        self.oceanseleven_link = self.tmdb_api_link % ('33358', self.tmdb_key)
        self.oddcouple_link = self.tmdb_api_link % ('33359', self.tmdb_key)
        self.ohgod_link = self.tmdb_api_link % ('33360', self.tmdb_key)
        self.olympushasfallen_link = self.tmdb_api_link % ('33361', self.tmdb_key)
        self.omen_link = self.tmdb_api_link % ('33362', self.tmdb_key)
        self.paulblart_link = self.tmdb_api_link % ('33363', self.tmdb_key)
        self.piratesofthecaribbean_link = self.tmdb_api_link % ('33364', self.tmdb_key)
        self.planetoftheapes_link = self.tmdb_api_link % ('13141', self.tmdb_key)
        self.policeacademy_link = self.tmdb_api_link % ('33366', self.tmdb_key)
        self.poltergeist_link = self.tmdb_api_link % ('33367', self.tmdb_key)
        self.porkys_link = self.tmdb_api_link % ('33368', self.tmdb_key)
        self.predator_link = self.tmdb_api_link % ('13136', self.tmdb_key)
        self.thepurge_link = self.tmdb_api_link % ('33370', self.tmdb_key)
        self.rambo_link = self.tmdb_api_link % ('33371', self.tmdb_key)
        self.red_link = self.tmdb_api_link % ('33372', self.tmdb_key)
        self.revengeofthenerds_link = self.tmdb_api_link % ('33373', self.tmdb_key)
        self.riddick_link = self.tmdb_api_link % ('33374', self.tmdb_key)
        self.ridealong_link = self.tmdb_api_link % ('33375', self.tmdb_key)
        self.thering_link = self.tmdb_api_link % ('33418', self.tmdb_key)
        self.robocop_link = self.tmdb_api_link % ('13115', self.tmdb_key)
        self.rocky_link = self.tmdb_api_link % ('33377', self.tmdb_key)
        self.romancingthestone_link = self.tmdb_api_link % ('33378', self.tmdb_key)
        self.rushhour_link = self.tmdb_api_link % ('33379', self.tmdb_key)
        self.santaclause_link = self.tmdb_api_link % ('33380', self.tmdb_key)
        self.saw_link = self.tmdb_api_link % ('33381', self.tmdb_key)
        self.sexandthecity_link = self.tmdb_api_link % ('33382', self.tmdb_key)
        self.shaft_link = self.tmdb_api_link % ('33383', self.tmdb_key)
        self.shanghainoon_link = self.tmdb_api_link % ('33384', self.tmdb_key)
        self.sincity_link = self.tmdb_api_link % ('33385', self.tmdb_key)
        self.sinister_link = self.tmdb_api_link % ('33386', self.tmdb_key)
        self.sisteract_link = self.tmdb_api_link % ('33387', self.tmdb_key)
        self.smokeyandthebandit_link = self.tmdb_api_link % ('33388', self.tmdb_key)
        self.speed_link = self.tmdb_api_link % ('33389', self.tmdb_key)
        self.stakeout_link = self.tmdb_api_link % ('33390', self.tmdb_key)
        self.startrek_link = self.tmdb_api_link % ('33391', self.tmdb_key)
        self.starwars_link = self.tmdb_api_link % ('12741', self.tmdb_key)
        self.thesting_link = self.tmdb_api_link % ('33392', self.tmdb_key)
        self.taken_link = self.tmdb_api_link % ('33393', self.tmdb_key)
        self.taxi_link = self.tmdb_api_link % ('33394', self.tmdb_key)
        self.ted_link = self.tmdb_api_link % ('33395', self.tmdb_key)
        self.teenwolf_link = self.tmdb_api_link % ('33396', self.tmdb_key)
        self.terminator_link = self.tmdb_api_link % ('33397', self.tmdb_key)
        self.termsofendearment_link = self.tmdb_api_link % ('33398', self.tmdb_key)
        self.texaschainsawmassacre_link = self.tmdb_api_link % ('33399', self.tmdb_key)
        self.thething_link = self.tmdb_api_link % ('33400', self.tmdb_key)
        self.thomascrownaffair_link = self.tmdb_api_link % ('33401', self.tmdb_key)
        self.transformers_link = 'https://www.imdb.com/search/title?title=transformers&title_type=feature&num_votes=1000,&countries=us&languages=en&sort=release_date,desc'
        self.transporter_link = self.tmdb_api_link % ('33402', self.tmdb_key)
        self.tron_link = 'https://www.imdb.com/search/title?title=tron&title_type=feature&num_votes=1000,&countries=us&languages=en&sort=release_date,desc'
        self.twilight_link = 'https://www.imdb.com/search/title?title=twilight&title_type=feature&num_votes=1000,&countries=us&languages=en&plot=vampire&sort=release_date,desc'
        self.undersiege_link = self.tmdb_api_link % ('33403', self.tmdb_key)
        self.underworld_link = 'https://www.imdb.com/search/title?title=Underworld&title_type=feature&num_votes=1000,&genres=action&countries=us&languages=en&sort=release_date,asc'
        self.universalsoldier_link = self.tmdb_api_link % ('33404', self.tmdb_key)
        self.wallstreet_link = self.tmdb_api_link % ('33405', self.tmdb_key)
        self.waynesworld_link = self.tmdb_api_link % ('33406', self.tmdb_key)
        self.weekendatbernies_link = self.tmdb_api_link % ('33407', self.tmdb_key)
        self.wholenineyards_link = self.tmdb_api_link % ('33408', self.tmdb_key)
        self.xfiles_link = self.tmdb_api_link % ('33409', self.tmdb_key)
        self.xxx_link = self.tmdb_api_link % ('33410', self.tmdb_key)
        self.youngguns_link = self.tmdb_api_link % ('33411', self.tmdb_key)
        self.zoolander_link = self.tmdb_api_link % ('33412', self.tmdb_key)
        self.zorro_link = self.tmdb_api_link % ('33413', self.tmdb_key)


# Boxset Collection Kids
        self.onehundredonedalmations_link = 'https://api.themoviedb.org/3/list/33182?api_key=%s' % (self.tmdb_key)
        self.addamsfamily_link = 'https://api.themoviedb.org/3/list/33183?api_key=%s' % (self.tmdb_key)
        self.aladdin_link = 'https://api.themoviedb.org/3/list/33184?api_key=%s' % (self.tmdb_key)
        self.alvinandthechipmunks_link = 'https://api.themoviedb.org/3/list/33185?api_key=%s' % (self.tmdb_key)
        self.atlantis_link = 'https://api.themoviedb.org/3/list/33186?api_key=%s' % (self.tmdb_key)
        self.babe_link = 'https://api.themoviedb.org/3/list/33187?api_key=%s' % (self.tmdb_key)
        self.balto_link = 'https://api.themoviedb.org/3/list/33188?api_key=%s' % (self.tmdb_key)
        self.bambi_link = 'https://api.themoviedb.org/3/list/33189?api_key=%s' % (self.tmdb_key)
        self.beautyandthebeast_link = 'https://api.themoviedb.org/3/list/33190?api_key=%s' % (self.tmdb_key)
        self.beethoven_link = 'https://api.themoviedb.org/3/list/33191?api_key=%s' % (self.tmdb_key)
        self.brotherbear_link = 'https://api.themoviedb.org/3/list/33192?api_key=%s' % (self.tmdb_key)
        self.cars_link = 'https://api.themoviedb.org/3/list/33193?api_key=%s' % (self.tmdb_key)
        self.cinderella_link = 'https://api.themoviedb.org/3/list/33194?api_key=%s' % (self.tmdb_key)
        self.cloudywithachanceofmeatballs_link = 'https://api.themoviedb.org/3/list/33195?api_key=%s' % (self.tmdb_key)
        self.despicableme_link = 'https://api.themoviedb.org/3/list/33197?api_key=%s' % (self.tmdb_key)
        self.findingnemo_link = 'https://api.themoviedb.org/3/list/33198?api_key=%s' % (self.tmdb_key)
        self.foxandthehound_link = 'https://api.themoviedb.org/3/list/33199?api_key=%s' % (self.tmdb_key)
        self.freewilly_link = 'https://api.themoviedb.org/3/list/33200?api_key=%s' % (self.tmdb_key)
        self.ghostbusters_link = 'https://api.themoviedb.org/3/list/33201?api_key=%s' % (self.tmdb_key)
        self.gremlins_link = 'https://api.themoviedb.org/3/list/33202?api_key=%s' % (self.tmdb_key)
        self.happyfeet_link = 'https://api.themoviedb.org/3/list/33204?api_key=%s' % (self.tmdb_key)
        self.harrypotter_link = 'https://api.themoviedb.org/3/list/33205?api_key=%s' % (self.tmdb_key)
        self.homealone_link = 'https://api.themoviedb.org/3/list/33206?api_key=%s' % (self.tmdb_key)
        self.homewardbound_link = 'https://api.themoviedb.org/3/list/33207?api_key=%s' % (self.tmdb_key)
        self.honeyishrunkthekids_link = 'https://api.themoviedb.org/3/list/33208?api_key=%s' % (self.tmdb_key)
        self.hoteltransylvania_link = 'https://api.themoviedb.org/3/list/33209?api_key=%s' % (self.tmdb_key)
        self.howtotrainyourdragon_link = 'https://api.themoviedb.org/3/list/33210?api_key=%s' % (self.tmdb_key)
        self.hunchbackofnotredame_link = 'https://api.themoviedb.org/3/list/33211?api_key=%s' % (self.tmdb_key)
        self.iceage_link = 'https://api.themoviedb.org/3/list/33212?api_key=%s' % (self.tmdb_key)
        self.jurassicpark_link = 'https://api.themoviedb.org/3/list/33217?api_key=%s' % (self.tmdb_key)
        self.kungfupanda_link = 'https://api.themoviedb.org/3/list/33218?api_key=%s' % (self.tmdb_key)
        self.ladyandthetramp_link = 'https://api.themoviedb.org/3/list/33219?api_key=%s' % (self.tmdb_key)
        self.liloandstitch_link = 'https://api.themoviedb.org/3/list/33220?api_key=%s' % (self.tmdb_key)
        self.madagascar_link = 'https://api.themoviedb.org/3/list/33221?api_key=%s' % (self.tmdb_key)
        self.monstersinc_link = 'https://api.themoviedb.org/3/list/33222?api_key=%s' % (self.tmdb_key)
        self.mulan_link = 'https://api.themoviedb.org/3/list/33223?api_key=%s' % (self.tmdb_key)
        self.narnia_link = 'https://api.themoviedb.org/3/list/33224?api_key=%s' % (self.tmdb_key)
        self.newgroove_link = 'https://api.themoviedb.org/3/list/33225?api_key=%s' % (self.tmdb_key)
        self.openseason_link = 'https://api.themoviedb.org/3/list/33226?api_key=%s' % (self.tmdb_key)
        self.planes_link = 'https://api.themoviedb.org/3/list/33227?api_key=%s' % (self.tmdb_key)
        self.pocahontas_link = 'https://api.themoviedb.org/3/list/33228?api_key=%s' % (self.tmdb_key)
        self.problemchild_link = 'https://api.themoviedb.org/3/list/33229?api_key=%s' % (self.tmdb_key)
        self.rio_link = 'https://api.themoviedb.org/3/list/33230?api_key=%s' % (self.tmdb_key)
        self.sammysadventures_link = 'https://api.themoviedb.org/3/list/33231?api_key=%s' % (self.tmdb_key)
        self.scoobydoo_link = 'https://api.themoviedb.org/3/list/33232?api_key=%s' % (self.tmdb_key)
        self.shortcircuit_link = 'https://api.themoviedb.org/3/list/33233?api_key=%s' % (self.tmdb_key)
        self.shrek_link = 'https://api.themoviedb.org/3/list/33234?api_key=%s' % (self.tmdb_key)
        self.spongebobsquarepants_link = 'https://api.themoviedb.org/3/list/33235?api_key=%s' % (self.tmdb_key)
        self.spykids_link = 'https://api.themoviedb.org/3/list/33236?api_key=%s' % (self.tmdb_key)
        self.starwars_link = 'https://api.themoviedb.org/3/list/12741?api_key=%s' % (self.tmdb_key)
        self.stuartlittle_link = 'https://api.themoviedb.org/3/list/33238?api_key=%s' % (self.tmdb_key)
        self.tarzan_link = 'https://api.themoviedb.org/3/list/33239?api_key=%s' % (self.tmdb_key)
        self.teenagemutantninjaturtles_link = 'https://api.themoviedb.org/3/list/33240?api_key=%s' % (self.tmdb_key)
        self.thejunglebook_link = 'https://api.themoviedb.org/3/list/33216?api_key=%s' % (self.tmdb_key)
        self.thekaratekid_link = 'https://api.themoviedb.org/3/list/33241?api_key=%s' % (self.tmdb_key)
        self.thelionking_link = 'https://api.themoviedb.org/3/list/33242?api_key=%s' % (self.tmdb_key)
        self.thelittlemermaid_link = 'https://api.themoviedb.org/3/list/33243?api_key=%s' % (self.tmdb_key)
        self.theneverendingstory_link = 'https://api.themoviedb.org/3/list/33248?api_key=%s' % (self.tmdb_key)
        self.thesmurfs_link = 'https://api.themoviedb.org/3/list/33249?api_key=%s' % (self.tmdb_key)
        self.toothfairy_link = 'https://api.themoviedb.org/3/list/33251?api_key=%s' % (self.tmdb_key)
        self.tinkerbell_link = 'https://api.themoviedb.org/3/list/33252?api_key=%s' % (self.tmdb_key)
        self.tomandjerry_link = 'https://api.themoviedb.org/3/list/33253?api_key=%s' % (self.tmdb_key)
        self.toystory_link = 'https://api.themoviedb.org/3/list/33254?api_key=%s' % (self.tmdb_key)
        self.veggietales_link = 'https://api.themoviedb.org/3/list/33255?api_key=%s' % (self.tmdb_key)
        self.winniethepooh_link = 'https://api.themoviedb.org/3/list/33257?api_key=%s' % (self.tmdb_key)
        self.wizardofoz_link = 'https://api.themoviedb.org/3/list/33258?api_key=%s' % (self.tmdb_key)

# Superhero Collection
        self.avengers_link = 'https://api.themoviedb.org/3/list/33128?api_key=%s' % (self.tmdb_key)
        self.batman_link = 'https://api.themoviedb.org/3/list/33129?api_key=%s' % (self.tmdb_key)
        self.captainamerica_link = 'https://api.themoviedb.org/3/list/33130?api_key=%s' % (self.tmdb_key)
        self.darkknight_link = 'https://api.themoviedb.org/3/list/33132?api_key=%s' % (self.tmdb_key)
        self.fantasticfour_link = 'https://api.themoviedb.org/3/list/33133?api_key=%s' % (self.tmdb_key)
        self.hulk_link = 'https://api.themoviedb.org/3/list/33134?api_key=%s' % (self.tmdb_key)
        self.ironman_link = 'https://api.themoviedb.org/3/list/33135?api_key=%s' % (self.tmdb_key)
        self.spiderman_link = 'https://api.themoviedb.org/3/list/33126?api_key=%s' % (self.tmdb_key)
        self.superman_link = 'https://api.themoviedb.org/3/list/33136?api_key=%s' % (self.tmdb_key)
        self.thor_link = 'https://www.imdb.com/search/title?title=thor&title_type=feature&num_votes=1000,&genres=action&countries=us&languages=en&sort=release_date,desc'
        self.xmen_link = 'https://api.themoviedb.org/3/list/33137?api_key=%s' % (self.tmdb_key)


    def collectionsNavigator(self, lite=False):
        self.addDirectoryItem('Movies', 'collectionBoxset', 'boxsets.png', 'boxsets.png')
        if self.getMenuEnabled('navi.xmascollections') == True:
            self.addDirectoryItem('Christmas Collections', 'collections&url=xmasmovies', 'boxsets.png', 'boxsets.png')
        self.addDirectoryItem('DC Comics', 'collections&url=dcmovies', 'boxsets.png', 'boxsets.png')
        self.addDirectoryItem('Marvel Comics', 'collections&url=marvelmovies', 'boxsets.png', 'boxsets.png')
        self.addDirectoryItem('Superheroes', 'collectionSuperhero', 'boxsets.png', 'boxsets.png')
        self.addDirectoryItem('Kids Collections', 'collectionKids', 'boxsets.png', 'boxsets.png')
        self.endDirectory()


    def collectionBoxset(self):
        self.addDirectoryItem('12 Rounds (2009-2015)', 'collections&url=rounds', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('300 (2007-2014)', 'collections&url=tmdb300', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('48 Hrs. (1982-1990)', 'collections&url=fortyeighthours', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Ace Ventura (1994-1995)', 'collections&url=aceventura', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Airplane (1980-1982)', 'collections&url=airplane', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Airport (1970-1979)', 'collections&url=airport', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('American Graffiti (1973-1979)', 'collections&url=americangraffiti', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Anaconda (1997-2004)', 'collections&url=anaconda', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Analyze This (1999-2002)', 'collections&url=analyzethis', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Anchorman (2004-2013)', 'collections&url=anchorman', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Austin Powers (1997-2002)', 'collections&url=austinpowers', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Back to the Future (1985-1990)', 'collections&url=backtothefuture', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Bad Boys (1995-2003)', 'collections&url=badboys', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Bad Santa (2003-2016)', 'collections&url=badsanta', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Basic Instinct (1992-2006)', 'collections&url=basicinstinct', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Beverly Hills Cop (1984-1994)', 'collections&url=beverlyhillscop', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Big Mommas House (2000-2011)', 'collections&url=bigmommashouse', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Blues Brothers (1980-1998)', 'collections&url=bluesbrothers', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Bourne (2002-2016)', 'collections&url=bourne', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Bruce Almighty (2003-2007)', 'collections&url=brucealmighty', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Bruce Lee (1965-2017)', 'collections&url=brucelee', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Caddyshack (1980-1988)', 'collections&url=caddyshack', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Cheaper by the Dozen (2003-2005)', 'collections&url=cheaperbythedozen', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Cheech and Chong (1978-1984)', 'collections&url=cheechandchong', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Childs Play (1988-2004)', 'collections&url=childsplay', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('City Slickers (1991-1994)', 'collections&url=cityslickers', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Conan (1982-2011)', 'collections&url=conan', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Crank (2006-2009)', 'collections&url=crank', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Crocodile Dundee (1986-2001)', 'collections&url=crocodiledundee', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('The Crow (1994-2005)', 'collections&url=thecrow', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Da Vinci Code (2006-2017)', 'collections&url=davincicode', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Daddy Day Care (2003-2007)', 'collections&url=daddydaycare', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Death Wish (1974-1994)', 'collections&url=deathwish', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Delta Force (1986-1990)', 'collections&url=deltaforce', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Die Hard (1988-2013)', 'collections&url=diehard', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Dirty Dancing (1987-2004)', 'collections&url=dirtydancing', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Dirty Harry (1971-1988)', 'collections&url=dirtyharry', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Divergent (2014-2016)', 'collections&url=divergent', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Dumb and Dumber (1994-2014)', 'collections&url=dumbanddumber', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Escape from New York (1981-1996)', 'collections&url=escapefromnewyork', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Every Which Way But Loose (1978-1980)', 'collections&url=everywhichwaybutloose', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Exorcist (1973-2005)', 'collections&url=exorcist', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('The Expendables (2010-2014)', 'collections&url=theexpendables', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Fast and the Furious (2001-2017)', 'collections&url=fastandthefurious', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Father of the Bride (1991-1995)', 'collections&url=fatherofthebride', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Fletch (1985-1989)', 'collections&url=fletch', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('The Fly (1986-1989)', 'collections&url=thefly', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Friday (1995-2002)', 'collections&url=friday', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Friday the 13th (1980-2009)', 'collections&url=fridaythe13th', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Fugitive (1993-1998)', 'collections&url=fugitive', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('G.I. Joe (2009-2013)', 'collections&url=gijoe', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Get Shorty (1995-2005)', 'collections&url=getshorty', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Gettysburg (1993-2003)', 'collections&url=gettysburg', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Ghost Rider (2007-2011)', 'collections&url=ghostrider', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Ghostbusters (1984-2016)', 'collections&url=ghostbusters', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Gods Not Dead (2014-2016)', 'collections&url=godsnotdead', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Godfather (1972-1990)', 'collections&url=godfather', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Godzilla (1956-2016)', 'collections&url=godzilla', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Grown Ups (2010-2013)', 'collections&url=grownups', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Grumpy Old Men (2010-2013)', 'collections&url=grumpyoldmen', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Guns of Navarone (1961-1978)', 'collections&url=gunsofnavarone', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Halloween (1978-2009)', 'collections&url=halloween', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Hangover (2009-2013)', 'collections&url=hangover', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Hannibal Lector (1986-2007)', 'collections&url=hanniballector', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Hellraiser (1987-1996)', 'collections&url=hellraiser', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Highlander', 'collections&url=highlander', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('The Hobbit (1977-2014)', 'collections&url=thehobbit', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Hollow Man (2000-2006)', 'collections&url=hollowman', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Honey I Shrunk the Kids (1989-1995)', 'collections&url=honeyishrunkthekids', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Horrible Bosses (2011-2014)', 'collections&url=horriblebosses', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Hostel (2005-2011)', 'collections&url=hostel', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Hot Shots (1991-1996)', 'collections&url=hotshots', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Hunger Games (2012-2015)', 'collections&url=hungergames', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('The Huntsman (2012-2016)', 'collections&url=huntsman', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Independence Day (1996-2016)', 'collections&url=independenceday', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Indiana Jones (1981-2008)', 'collections&url=indianajones', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Insidious (2010-2015)', 'collections&url=insidious', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Iron Eagle (1986-1992)', 'collections&url=ironeagle', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Jack Reacher (2012-2016)', 'collections&url=jackreacher', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Jack Ryan (1990-2014)', 'collections&url=jackryan', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Jackass (2002-2013)', 'collections&url=jackass', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('James Bond (1963-2015)', 'collections&url=jamesbond', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Jaws (1975-1987)', 'collections&url=jaws', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Jeepers Creepers (2001-2017)', 'collections&url=jeeperscreepers', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('John Wick (2014-2017)', 'collections&url=johnwick', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Journey to the Center of the Earth (2008-2012)', 'collections&url=journeytocenter', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Judge Dredd (1995-2012)', 'collections&url=judgedredd', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Jumanji (1995-2005)', 'collections&url=jumanji', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Jump Street (2012-2014)', 'collections&url=jumpst', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Jurassic Park (1993-2015)', 'collections&url=jurassicpark', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Kick-Ass (2010-2013)', 'collections&url=kickass', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Kill Bill (2003-2004)', 'collections&url=killbill', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('King Kong (1933-2016)', 'collections&url=kingkong', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Lara Croft (2001-2003)', 'collections&url=laracroft', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Legally Blonde (2001-2003)', 'collections&url=legallyblonde', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Lethal Weapon (1987-1998)', 'collections&url=lethalweapon', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Look Whos Talking (1989-1993)', 'collections&url=lookwhostalking', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Lord of The Rings (1978-2003)', 'collections&url=lordoftherings', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Machete (2010-2013)', 'collections&url=machete', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Mad Max (1979-2015)', 'collections&url=madmax', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Magic Mike (2012-2015)', 'collections&url=magicmike', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Major League (1989-1998)', 'collections&url=majorleague', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Man from Snowy River (1982-1988)', 'collections&url=manfromsnowyriver', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('The Mask (1994-2005)', 'collections&url=mask', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('The Matrix (1999-2003)', 'collections&url=matrix', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Maze Runner(2014-2018)', 'collections&url=mazerunner', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('The Mechanic (2011-2016)', 'collections&url=themechanic', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Meet the Parents (2000-2010)', 'collections&url=meettheparents', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Men in Black (1997-2012)', 'collections&url=meninblack', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Mighty Ducks (1995-1996)', 'collections&url=mightyducks', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Miss Congeniality (2000-2005)', 'collections&url=misscongeniality', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Missing in Action (1984-1988)', 'collections&url=missinginaction', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Mission Impossible (1996-2015)', 'collections&url=missionimpossible', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('The Mummy (1999-2017)', 'collections&url=themummy', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Naked Gun (1988-1994)', 'collections&url=nakedgun', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('National Lampoon (1978-2006)', 'collections&url=nationallampoon', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('National Lampoons Vacation (1983-2015)', 'collections&url=nationallampoonsvacation', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('National Treasure (2004-2007)', 'collections&url=nationaltreasure', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Neighbors (2014-2016)', 'collections&url=neighbors', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Night at the Museum (2006-2014)', 'collections&url=nightatthemuseum', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Nightmare on Elm Street (1984-2010)', 'collections&url=nightmareonelmstreet', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Now You See Me (2013-2016)', 'collections&url=nowyouseeme', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Nutty Professor (1996-2000)', 'collections&url=nuttyprofessor', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Oceans Eleven (2001-2007)', 'collections&url=oceanseleven', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Odd Couple (1968-1998)', 'collections&url=oddcouple', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Oh, God (1977-1984)', 'collections&url=ohgod', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Olympus Has Fallen (2013-2016)', 'collections&url=olympushasfallen', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('The Omen (1976-1981)', 'collections&url=omen', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Paul Blart Mall Cop (2009-2015)', 'collections&url=paulblart', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Pirates of the Caribbean (2003-2017)', 'collections&url=piratesofthecaribbean', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Planet of the Apes (1968-2017)', 'collections&url=planetoftheapes', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Police Academy (1984-1994)', 'collections&url=policeacademy', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Poltergeist (1982-1988)', 'collections&url=poltergeist', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Porkys (1981-1985)', 'collections&url=porkys', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Predator (1987-2018)', 'collections&url=predator', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('The Purge (2013-2016)', 'collections&url=thepurge', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Rambo (1982-2008)', 'collections&url=rambo', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('RED (2010-2013)', 'collections&url=red', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Revenge of the Nerds (1984-1987)', 'collections&url=revengeofthenerds', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Riddick (2000-2013)', 'collections&url=riddick', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Ride Along (2014-2016)', 'collections&url=ridealong', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('The Ring (2002-2017)', 'collections&url=thering', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('RoboCop (1987-1993)', 'collections&url=robocop', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Rocky (1976-2015)', 'collections&url=rocky', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Romancing the Stone (1984-1985)', 'collections&url=romancingthestone', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Rush Hour (1998-2007)', 'collections&url=rushhour', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Santa Clause (1994-2006)', 'collections&url=santaclause', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Saw (2004-2010)', 'collections&url=saw', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Sex and the City (2008-2010)', 'collections&url=sexandthecity', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Shaft (1971-2000)', 'collections&url=shaft', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Shanghai Noon (2000-2003)', 'collections&url=shanghainoon', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Sin City (2005-2014)', 'collections&url=sincity', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Sinister (2012-2015)', 'collections&url=sinister', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Sister Act (1995-1993)', 'collections&url=sisteract', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Smokey and the Bandit (1977-1986)', 'collections&url=smokeyandthebandit', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Speed (1994-1997)', 'collections&url=speed', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Stakeout (1987-1993)', 'collections&url=stakeout', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Star Trek (1979-2016)', 'collections&url=startrek', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Star Wars (1977-2017)', 'collections&url=starwars', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('The Sting (1973-1983)', 'collections&url=thesting', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Taken (2008-2014)', 'collections&url=taken', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Taxi (1998-2007)', 'collections&url=taxi', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Ted (2012-2015)', 'collections&url=ted', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Teen Wolf (1985-1987)', 'collections&url=teenwolf', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Terminator (1984-2015)', 'collections&url=terminator', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Terms of Endearment (1983-1996)', 'collections&url=termsofendearment', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Texas Chainsaw Massacre (1974-2013)', 'collections&url=texaschainsawmassacre', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('The Thing (1982-2011)', 'collections&url=thething', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Thomas Crown Affair (1968-1999)', 'collections&url=thomascrownaffair', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Transformers (2002-2017)', 'collections&url=transformers', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Transporter (2002-2015)', 'collections&url=transporter', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Tron (1982-2010)', 'collections&url=tron', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Twilight (2008-2012)', 'collections&url=twilight', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Under Siege (1992-1995)', 'collections&url=undersiege', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Underworld (2003-2016)', 'collections&url=underworld', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Universal Soldier (1992-2012)', 'collections&url=universalsoldier', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Wall Street (1987-2010)', 'collections&url=wallstreet', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Waynes World (1992-1993)', 'collections&url=waynesworld', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Weekend at Bernies (1989-1993)', 'collections&url=weekendatbernies', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Whole Nine Yards (2000-2004)', 'collections&url=wholenineyards', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('X-Files (1998-2008)', 'collections&url=xfiles', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('xXx (2002-2005)', 'collections&url=xxx', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Young Guns (1988-1990)', 'collections&url=youngguns', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Zoolander (2001-2016)', 'collections&url=zoolander', 'collectionboxset.png', 'collectionboxset.png')
        self.addDirectoryItem('Zorro (1998-2005)', 'collections&url=zorro', 'collectionboxset.png', 'collectionboxset.png')
        self.endDirectory()


    def collectionKids(self):
        self.addDirectoryItem('Disney Collection', 'collections&url=disneymovies', 'collectiondisney.png', 'collectiondisney.png')
        self.addDirectoryItem('Kids Boxset Collection', 'collectionBoxsetKids', 'collectionkidsboxset.png', 'collectiondisney.png')
        self.addDirectoryItem('Kids Movie Collection', 'collections&url=kidsmovies', 'collectionkids.png', 'collectiondisney.png')
        self.endDirectory()


    def collectionBoxsetKids(self):
        self.addDirectoryItem('101 Dalmations (1961-2003)', 'collections&url=onehundredonedalmations', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Addams Family (1991-1998)', 'collections&url=addamsfamily', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Aladdin (1992-1996)', 'collections&url=aladdin', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Alvin and the Chipmunks (2007-2015)', 'collections&url=alvinandthechipmunks', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Atlantis (2001-2003)', 'collections&url=atlantis', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Babe (1995-1998)', 'collections&url=babe', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Balto (1995-1998)', 'collections&url=balto', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Bambi (1942-2006)', 'collections&url=bambi', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Beauty and the Beast (1991-2017)', 'collections&url=beautyandthebeast', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Beethoven (1992-2014)', 'collections&url=beethoven', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Brother Bear (2003-2006)', 'collections&url=brotherbear', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Cars (2006-2017)', 'collections&url=cars', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Cinderella (1950-2007)', 'collections&url=cinderella', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Cloudy With a Chance of Meatballs (2009-2013)', 'collections&url=cloudywithachanceofmeatballs', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Despicable Me (2010-2015)', 'collections&url=despicableme', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Finding Nemo (2003-2016)', 'collections&url=findingnemo', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Fox and the Hound (1981-2006)', 'collections&url=foxandthehound', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Free Willy (1993-2010)', 'collections&url=freewilly', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Ghostbusters (1984-2016)', 'collections&url=ghostbusters', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Gremlins (1984-2016)', 'collections&url=gremlins', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Happy Feet (2006-2011)', 'collections&url=happyfeet', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Harry Potter (2001-2011)', 'collections&url=harrypotter', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Home Alone (1990-2012)', 'collections&url=homealone', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Homeward Bound (1993-1996)', 'collections&url=homewardbound', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Honey, I Shrunk the Kids (1989-1997)', 'collections&url=honeyishrunkthekids', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Hotel Transylvania (2012-2015)', 'collections&url=hoteltransylvania', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('How to Train Your Dragon (2010-2014)', 'collections&url=howtotrainyourdragon', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Hunchback of Notre Dame (1996-2002)', 'collections&url=hunchbackofnotredame', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Ice Age (2002-2016)', 'collections&url=iceage', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Jurassic Park (1993-2015)', 'collections&url=jurassicpark', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Kung Fu Panda (2008-2016)', 'collections&url=kungfupanda', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Lady and the Tramp (1955-2001)', 'collections&url=ladyandthetramp', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Lilo and Stitch (2002-2006)', 'collections&url=liloandstitch', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Madagascar (2005-2014)', 'collections&url=madagascar', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Monsters Inc (2001-2013)', 'collections&url=monstersinc', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Mulan (1998-2004)', 'collections&url=mulan', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Narnia (2005-2010)', 'collections&url=narnia', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('New Groove (2000-2005)', 'collections&url=newgroove', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Open Season (2006-2015)', 'collections&url=openseason', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Planes (2013-2014)', 'collections&url=planes', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Pocahontas (1995-1998)', 'collections&url=pocahontas', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Problem Child (1990-1995)', 'collections&url=problemchild', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Rio (2011-2014)', 'collections&url=rio', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Sammys Adventures (2010-2012)', 'collections&url=sammysadventures', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Scooby-Doo (2002-2014)', 'collections&url=scoobydoo', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Short Circuit (1986-1988)', 'collections&url=shortcircuit', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Shrek (2001-2011)', 'collections&url=shrek', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('SpongeBob SquarePants (2004-2017)', 'collections&url=spongebobsquarepants', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Spy Kids (2001-2011)', 'collections&url=spykids', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Stuart Little (1999-2002)', 'collections&url=stuartlittle', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Tarzan (1999-2016)', 'collections&url=tarzan', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Teenage Mutant Ninja Turtles (1978-2009)', 'collections&url=teenagemutantninjaturtles', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('The Jungle Book (1967-2003)', 'collections&url=thejunglebook', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('The Karate Kid (1984-2010)', 'collections&url=thekaratekid', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('The Lion King (1994-2016)', 'collections&url=thelionking', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('The Little Mermaid (1989-1995)', 'collections&url=thelittlemermaid', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('The Neverending Story (1984-1994)', 'collections&url=theneverendingstory', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('The Smurfs (2011-2013)', 'collections&url=thesmurfs', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Tooth Fairy (2010-2012)', 'collections&url=toothfairy', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Tinker Bell (2008-2014)', 'collections&url=tinkerbell', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Tom and Jerry (1992-2013)', 'collections&url=tomandjerry', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Toy Story (1995-2014)', 'collections&url=toystory', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('VeggieTales (2002-2008)', 'collections&url=veggietales', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Winnie the Pooh (2000-2005)', 'collections&url=winniethepooh', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.addDirectoryItem('Wizard of Oz (1939-2013)', 'collections&url=wizardofoz', 'collectionkidsboxset.png', 'collectionkidsboxset.png')
        self.endDirectory()


    def collectionSuperhero(self):
        self.addDirectoryItem('Avengers (2008-2017)', 'collections&url=avengers', 'collectionsuperhero.png', 'collectionsuperhero.png')
        self.addDirectoryItem('Batman (1989-2016)', 'collections&url=batman', 'collectionsuperhero.png', 'collectionsuperhero.png')
        self.addDirectoryItem('Captain America (2011-2016)', 'collections&url=captainamerica', 'collectionsuperhero.png', 'collectionsuperhero.png')
        self.addDirectoryItem('Dark Knight Trilogy (2005-2013)', 'collections&url=darkknight', 'collectionsuperhero.png', 'collectionsuperhero.png')
        self.addDirectoryItem('Fantastic Four (2005-2015)', 'collections&url=fantasticfour', 'collectionsuperhero.png', 'collectionsuperhero.png')
        self.addDirectoryItem('Hulk (2003-2008)', 'collections&url=hulk', 'collectionsuperhero.png', 'collectionsuperhero.png')
        self.addDirectoryItem('Iron Man (2008-2013)', 'collections&url=ironman', 'collectionsuperhero.png', 'collectionsuperhero.png')
        self.addDirectoryItem('Spider-Man (2002-2017)', 'collections&url=spiderman', 'collectionsuperhero.png', 'collectionsuperhero.png')
        self.addDirectoryItem('Thor (2011-2017)', 'collections&url=thor', 'collectionsuperhero.png', 'collectionsuperhero.png')
        self.addDirectoryItem('Superman (1978-2016)', 'collections&url=superman', 'collectionsuperhero.png', 'collectionsuperhero.png')
        self.addDirectoryItem('X-Men (2000-2016)', 'collections&url=xmen', 'collectionsuperhero.png', 'collectionsuperhero.png')
        self.endDirectory()


    def getMenuEnabled(self, menu_title):
        is_enabled = control.setting(menu_title).strip()
        if (is_enabled == '' or is_enabled == 'false'): return False
        return True


    def get(self, url, idx=True):
        try:
            try: url = getattr(self, url + '_link')
            except: pass
            try: u = urlparse.urlparse(url).netloc.lower()
            except:
                pass

            if u in self.tmdb_link and ('/user/' in url or '/list/' in url):
                from resources.lib.indexers import tmdb
                self.list = cache.get(tmdb.movies().tmdb_collections_list, 720, url)
                self.sort()

            elif u in self.tmdb_link and not ('/user/' in url or '/list/' in url):
                from resources.lib.indexers import tmdb
                self.list = cache.get(tmdb.movies().tmdb_list, 720, url)
                self.sort()

            elif u in self.imdb_link and ('/user/' in url or '/list/' in url):
                self.list = cache.get(self.imdb_list, 720, url)
                if idx == True: self.worker()
                self.sort()

            elif u in self.imdb_link:
                self.list = cache.get(self.imdb_list, 720, url)
                if idx == True: self.worker()
                self.sort()

            if idx == True: self.movieDirectory(self.list)
            return self.list
        except:
            pass


    def sort(self):
        try:
            attribute = int(control.setting('sort.movies.type'))
            reverse = int(control.setting('sort.movies.order')) == 1
            if attribute == 0: reverse = False
            if attribute > 0:
                if attribute == 1:
                    try:
                        self.list = sorted(self.list, key = lambda k: re.sub('(^the |^a |^an )', '', k['title'].lower()), reverse = reverse)
                    except: self.list = sorted(self.list, key = lambda k: k['title'].lower(), reverse = reverse)
                elif attribute == 2:
                    self.list = sorted(self.list, key = lambda k: float(k['rating']), reverse = reverse)
                elif attribute == 3:
                    self.list = sorted(self.list, key = lambda k: int(k['votes'].replace(',', '')), reverse = reverse)
                elif attribute == 4:
                    for i in range(len(self.list)):
                        if not 'premiered' in self.list[i]: self.list[i]['premiered'] = ''
                    self.list = sorted(self.list, key = lambda k: k['premiered'], reverse = reverse)
                elif attribute == 5:
                    for i in range(len(self.list)):
                        if not 'added' in self.list[i]: self.list[i]['added'] = ''
                    self.list = sorted(self.list, key = lambda k: k['added'], reverse = reverse)
                elif attribute == 6:
                    for i in range(len(self.list)):
                        if not 'watched' in self.list[i]: self.list[i]['watched'] = ''
                    self.list = sorted(self.list, key = lambda k: k['watched'], reverse = reverse)
            elif reverse:
                self.list = reversed(self.list)
        except:
            tools.Logger.error()


    def imdb_list(self, url):
        list = []
        try:
            for i in re.findall('date\[(\d+)\]', url):
                url = url.replace('date[%s]' % i, (self.datetime - datetime.timedelta(days = int(i))).strftime('%Y-%m-%d'))

            def imdb_watchlist_id(url):
                return client.parseDOM(client.request(url).decode('iso-8859-1').encode('utf-8'), 'meta', ret='content', attrs = {'property': 'pageId'})[0]

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
                # title = title.encode('utf-8')

                year = client.parseDOM(item, 'span', attrs = {'class': 'lister-item-year.+?'})
                year = re.findall('(\d{4})', year[0])[0]
                year = year.encode('utf-8')

                try: show = '–'.decode('utf-8') in str(year).decode('utf-8') or '-'.decode('utf-8') in str(year).decode('utf-8')
                except: show = False
                if show: raise Exception() # Some lists contain TV shows.

                if int(year) > int((self.datetime).strftime('%Y')): raise Exception()

                imdb = client.parseDOM(item, 'a', ret='href')[0]
                imdb = re.findall('(tt\d*)', imdb)[0]
                imdb = imdb.encode('utf-8')

                try: poster = client.parseDOM(item, 'img', ret='loadlate')[0]
                except: poster = '0'
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
                except: pass
                try: rating = client.parseDOM(rating, 'span', attrs = {'class': 'value'})[0]
                except: rating = '0'
                try: rating = client.parseDOM(item, 'div', ret='data-value', attrs = {'class': '.*?imdb-rating'})[0]
                except: pass
                if rating == '' or rating == '-': rating = '0'
                rating = client.replaceHTMLCodes(rating)
                rating = rating.encode('utf-8')

                try: votes = client.parseDOM(item, 'div', ret='title', attrs = {'class': '.*?rating-list'})[0]
                except: votes = '0'
                try: votes = re.findall('\((.+?) vote(?:s|)\)', votes)[0]
                except: votes = '0'
                if votes == '': votes = '0'
                votes = client.replaceHTMLCodes(votes)
                votes = votes.encode('utf-8')

                try: mpaa = client.parseDOM(item, 'span', attrs = {'class': 'certificate'})[0]
                except: mpaa = '0'
                if mpaa == '' or mpaa == 'NOT_RATED': mpaa = '0'
                mpaa = mpaa.replace('_', '-')
                mpaa = client.replaceHTMLCodes(mpaa)
                mpaa = mpaa.encode('utf-8')

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
                except: pass
                try: plot = client.parseDOM(item, 'div', attrs = {'class': 'item_description'})[0]
                except: pass
                plot = plot.rsplit('<span>', 1)[0].strip()
                plot = re.sub('<.+?>|</.+?>', '', plot)
                if plot == '': plot = '0'
                plot = client.replaceHTMLCodes(plot)
                plot = plot.encode('utf-8')

                self.list.append({'title': title, 'originaltitle': title, 'year': year, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'cast': cast, 'plot': plot, 'tagline': '0', 'imdb': imdb, 'tmdb': '0', 'tvdb': '0', 'poster': poster, 'next': next})
            except:
                pass

        return self.list


    def worker(self, level=1):
        if self.list == None or self.list == []: return
        self.meta = []
        total = len(self.list)

        self.fanart_tv_headers = {'api-key': '9f846e7ec1ea94fad5d8a431d1d26b43'}
        if not self.fanart_tv_user == '': self.fanart_tv_headers.update({'client-key': self.fanart_tv_user})

        for i in range(0, total): self.list[i].update({'metacache': False})

        self.list = metacache.fetch(self.list, self.lang, self.user)

        imdb_t = self.list[i]['imdb']
        tmdb_t = self.list[i]['tmdb']

        for r in range(0, total, 40):
            threads = []
            for i in range(r, r+40):
                if i <= total and imdb_t != '0': threads.append(workers.Thread(self.super_imdb_info, i))
                if i <= total and tmdb_t != '0': threads.append(workers.Thread(self.super_tmdb_info, i))
            [i.start() for i in threads]
            [i.join() for i in threads]
            if self.meta: metacache.insert(self.meta)

        self.list = [i for i in self.list]
        # self.list = metacache.local(self.list, self.tmdb_img_link, 'poster3', 'fanart2')

        if self.fanart_tv_user == '':
            for i in self.list:
                i.update({'clearlogo': '0', 'clearart': '0'})


    def super_imdb_info(self, i):
        try:
            if self.list[i]['metacache'] == True: raise Exception()

            imdb = self.list[i]['imdb']

            item = trakt.getMovieSummary(id = imdb)

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

##--TMDb artwork
            try:
                if self.tmdb_key == '': raise Exception()
                art2 = client.request(self.tmdb_art_link % imdb, timeout='20', error=True)
                art2 = json.loads(art2)
            except:
                pass

            try:
                poster3 = art2['posters']
                poster3 = [(x['width'], x['file_path']) for x in poster3]
                poster3 = [x[1] for x in poster3]
                poster3 = self.tmdb_poster_path + poster3[0]
            except:
                poster3 = '0'

            try:
                fanart2 = art2['backdrops']
                fanart2 = [(x['width'], x['file_path']) for x in fanart2]
                fanart2 = [x[1] for x in fanart2]
                fanart2 = self.tmdb_background_path + fanart2[0]
            except:
                fanart2 = '0'
##---

            item = {'title': title, 'originaltitle': originaltitle, 'year': year, 'imdb': imdb, 'tmdb': tmdb, 'poster': '0', 'poster2': poster2, 'poster3': poster3, 'banner': banner, 'fanart': fanart, 'fanart2': fanart2, 'clearlogo': clearlogo, 'clearart': clearart,
                    'discart': discart, 'landscape': landscape, 'premiered': premiered, 'genre': genre, 'duration': duration, 'rating': rating, 'votes': votes, 'mpaa': mpaa, 'director': director, 'writer': writer, 'cast': cast, 'plot': plot, 'tagline': tagline}
            item = dict((k,v) for k, v in item.iteritems() if not v == '0')
            self.list[i].update(item)

            if artmeta == False: raise Exception()

            meta = {'imdb': imdb, 'tmdb': tmdb, 'tvdb': '0', 'lang': self.lang, 'user': self.user, 'item': item}
            self.meta.append(meta)
        except:
            pass


    def movieDirectory(self, items):
        if items == None or len(items) == 0: 
            control.idle()
            control.notification(title = 32001, message = 33049, icon = 'INFO')
            sys.exit()

        addonPoster, addonBanner = control.addonPoster(), control.addonBanner()
        addonFanart, settingFanart = control.addonFanart(), control.setting('fanart')

        traktCredentials = trakt.getTraktCredentialsInfo()

        try: isOld = False ; control.item().getArt('type')
        except: isOld = True

        indicators = playcount.getMovieIndicators()

        isPlayable = 'true' if not 'plugin' in control.infoLabel('Container.PluginName') else 'false'

        playbackMenu = control.lang(32063).encode('utf-8') if control.setting('hosts.mode') == '2' else control.lang(32064).encode('utf-8')
        watchedMenu = control.lang(32068).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32066).encode('utf-8')
        unwatchedMenu = control.lang(32069).encode('utf-8') if trakt.getTraktIndicatorsInfo() == True else control.lang(32067).encode('utf-8')
        playlistManagerMenu = control.lang(35522).encode('utf-8')
        queueMenu = control.lang(32065).encode('utf-8')
        traktManagerMenu = control.lang(32070).encode('utf-8')
        nextMenu = control.lang(32053).encode('utf-8')
        addToLibrary = control.lang(32551).encode('utf-8')

        for i in items:
            try:
                imdb, tmdb, year = i['imdb'], i['tmdb'], i['year']
                try: title = i['originaltitle']
                except: title = i['title']
                label = '%s (%s)' % (i['title'], i['year'])

                # sysname = urllib.quote_plus('%s (%s)' % (title, year))
                sysname = urllib.quote_plus(label)
                systitle = urllib.quote_plus(title)

                meta = dict((k,v) for k, v in i.iteritems() if not v == '0')
                meta.update({'code': imdb, 'imdbnumber': imdb, 'imdb_id': imdb})
                meta.update({'tmdb_id': tmdb})
                meta.update({'mediatype': 'movie'})
                meta.update({'trailer': '%s?action=trailer&name=%s' % (sysaddon, sysname)})

                # Some descriptions have a link at the end that. Remove it.
                try:
                    plot = meta['plot']
                    index = plot.rfind('See full summary')
                    if index >= 0: plot = plot[:index]
                    plot = plot.strip()
                    if re.match('[a-zA-Z\d]$', plot): plot += ' ...'
                    meta['plot'] = plot
                except: pass

                try: meta.update({'duration': str(int(meta['duration']) * 60)})
                except: pass
                try: meta.update({'genre': cleangenre.lang(meta['genre'], self.lang)})
                except: pass
                try: meta.update({'year': int(meta['year'])})
                except: pass

                poster = [i[x] for x in ['poster3', 'poster', 'poster2'] if i.get(x, '0') != '0']
                poster = poster[0] if poster else addonPoster
                meta.update({'poster': poster})

                icon = '0'
                if icon == '0' and 'icon' in i: icon = i['icon']

                thumb = '0'
                if thumb == '0' and 'thumb' in i: thumb = i['thumb']

                banner = '0'
                if banner == '0' and 'banner' in i: banner = i['banner']

                poster = '0'
                if poster == '0' and 'poster3' in i: poster = i['poster3']
                if poster == '0' and 'poster2' in i: poster = i['poster2']
                if poster == '0' and 'poster' in i: poster = i['poster']

                fanart = '0'
                if settingFanart:
                    if fanart == '0' and 'fanart2' in i: fanart = i['fanart2']
                    if fanart == '0' and 'fanart' in i: fanart = i['fanart']

                clearlogo = '0'
                if clearlogo == '0' and 'clearlogo' in i: clearlogo = i['clearlogo']

                clearart = '0'
                if clearart == '0' and 'clearart' in i: clearart = i['clearart']

                landscape = '0'
                if landscape == '0' and 'landscape' in i: landscape = i['landscape']

                discart = '0'
                if discart == '0' and 'discart' in i: discart = i['discart']

                if poster == '0': poster = addonPoster
                if icon == '0': icon = poster
                if thumb == '0': thumb = poster
                if banner == '0': banner = addonBanner
                if fanart == '0': fanart = addonFanart

                art = {}
                if not icon == '0' and not icon == None: art.update({'icon' : icon})
                if not thumb == '0' and not thumb == None: art.update({'thumb' : thumb})
                if not banner == '0' and not banner == None: art.update({'banner' : banner})
                if not poster == '0' and not poster == None: art.update({'poster' : poster})
                if not fanart == '0' and not fanart == None: art.update({'fanart' : fanart})
                if not clearlogo == '0' and not clearlogo == None: art.update({'clearlogo' : clearlogo})
                if not clearart == '0' and not clearart == None: art.update({'clearart' : clearart})
                if not landscape == '0' and not landscape == None: art.update({'landscape' : landscape})
                if not discart == '0' and not discart == None: art.update({'discart' : discart})


####-Context Menu and Overlays-####
                cm = []
                if traktCredentials == True:
                    cm.append((traktManagerMenu, 'RunPlugin(%s?action=traktManager&name=%s&imdb=%s)' % (sysaddon, sysname, imdb)))

                try:
                    overlay = int(playcount.getMovieOverlay(indicators, imdb))
                    if overlay == 7:
                        cm.append((unwatchedMenu, 'RunPlugin(%s?action=moviePlaycount&imdb=%s&query=6)' % (sysaddon, imdb)))
                        meta.update({'playcount': 1, 'overlay': 7})
                    else:
                        cm.append((watchedMenu, 'RunPlugin(%s?action=moviePlaycount&imdb=%s&query=7)' % (sysaddon, imdb)))
                        meta.update({'playcount': 0, 'overlay': 6})
                except: pass

                sysmeta = urllib.quote_plus(json.dumps(meta))
                sysart = urllib.quote_plus(json.dumps(art))

                url = '%s?action=play&title=%s&year=%s&imdb=%s&meta=%s&t=%s' % (sysaddon, systitle, year, imdb, sysmeta, self.systime)
                sysurl = urllib.quote_plus(url)
#                path = '%s?action=play&title=%s&year=%s&imdb=%s' % (sysaddon, systitle, year, imdb)

                cm.append(('Find similar', 'ActivateWindow(10025,%s?action=movies&url=https://api.trakt.tv/movies/%s/related,return)' % (sysaddon, imdb)))
                cm.append((playlistManagerMenu, 'RunPlugin(%s?action=playlistManager&name=%s&url=%s&meta=%s&art=%s)' % (sysaddon, sysname, sysurl, sysmeta, sysart)))
                cm.append((queueMenu, 'RunPlugin(%s?action=queueItem&name=%s)' % (sysaddon, sysname)))
                cm.append((playbackMenu, 'RunPlugin(%s?action=alterSources&url=%s&meta=%s)' % (sysaddon, sysurl, sysmeta)))
                if isOld == True:
                    cm.append((control.lang2(19033).encode('utf-8'), 'Action(Info)'))
                cm.append((addToLibrary, 'RunPlugin(%s?action=movieToLibrary&name=%s&title=%s&year=%s&imdb=%s&tmdb=%s)' % (sysaddon, sysname, systitle, year, imdb, tmdb)))
                cm.append(('[COLOR red]Venom Settings[/COLOR]', 'RunPlugin(%s?action=openSettings&query=(0,0))' % sysaddon))
####################################

                item = control.item(label=label)
                if not fanart == '0' and not fanart == None: item.setProperty('Fanart_Image', fanart)
                item.setArt(art)
                item.setProperty('IsPlayable', isPlayable)
                item.setInfo(type='video', infoLabels=control.metadataClean(meta))
                video_streaminfo = {'codec': 'h264'}
                item.addStreamInfo('video', video_streaminfo)
                item.addContextMenuItems(cm)
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)
            except:
                pass

        try:
            url = items[0]['next']
            if url == '': raise Exception()

            icon = control.addonNext()
            url = '%s?action=moviePage&url=%s' % (sysaddon, urllib.quote_plus(url))

            item = control.item(label=nextMenu)

            item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'banner': icon})
            if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

            control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
        except:
            pass

        control.content(syshandle, 'movies')
        control.directory(syshandle, cacheToDisc=True)
        views.setView('movies', {'skin.estuary': 55, 'skin.confluence': 500})


    def addDirectory(self, items, queue=False):
        if items == None or len(items) == 0: control.idle() ; sys.exit()

        addonFanart, addonThumb, artPath = control.addonFanart(), control.addonThumb(), control.artPath()
        queueMenu = control.lang(32065).encode('utf-8')
        playRandom = control.lang(32535).encode('utf-8')
        addToLibrary = control.lang(32551).encode('utf-8')

        for i in items:
            try:
                name = i['name']

                if i['image'].startswith('http'): thumb = i['image']
                elif not artPath == None: thumb = os.path.join(artPath, i['image'])
                else: thumb = addonThumb

                url = '%s?action=%s' % (sysaddon, i['action'])
                try: url += '&url=%s' % urllib.quote_plus(i['url'])
                except: pass

                cm = []
                cm.append((playRandom, 'RunPlugin(%s?action=random&rtype=movie&url=%s)' % (sysaddon, urllib.quote_plus(i['url']))))
                if queue == True:
                    cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
                try: cm.append((addToLibrary, 'RunPlugin(%s?action=moviesToLibrary&url=%s)' % (sysaddon, urllib.quote_plus(i['context']))))
                except: pass
                cm.append(('[COLOR red]Venom Settings[/COLOR]', 'RunPlugin(%s?action=openSettings&query=(0,0))' % sysaddon))

                item = control.item(label = name)

                item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': thumb})
                if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)

                item.addContextMenuItems(cm)
                control.addItem(handle=syshandle, url=url, listitem=item, isFolder=True)
            except:
                pass

        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=True)


    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True):
        try: name = control.lang(name).encode('utf-8')
        except: pass

        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query

        thumb = os.path.join(artPath, thumb) if not artPath == None else icon

        cm = []
        if queue == True: cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
        if not context == None: cm.append((control.lang(context[0]).encode('utf-8'), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
        cm.append(('[COLOR red]Venom Settings[/COLOR]', 'RunPlugin(%s?action=openSettings&query=(0,0))' % sysaddon))

        item = control.item(label = name)
        item.addContextMenuItems(cm)

        item.setArt({'icon': thumb, 'thumb': thumb})
        if not addonFanart == None: item.setProperty('Fanart_Image', addonFanart)
        control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)


    def endDirectory(self):
        control.content(syshandle, 'addons')
        control.directory(syshandle, cacheToDisc=True)

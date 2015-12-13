# -*- coding: utf-8 -*-
from kivy.properties import ListProperty,ObjectProperty,DictProperty,StringProperty
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import AsyncImage, Image
from kivy.logger import Logger

from operator import attrgetter
import os.path
from kivy.loader import Loader
from functools import partial
from kivy.clock import Clock
from kivy.graphics import Fbo
from kivy.graphics import (Canvas, Translate, Fbo, ClearColor, ClearBuffers,
                            Scale)


class ComicCollection(object):

    # ids = DictProperty({})
    # name = StringProperty()
    def __init__(self,name=''):
        self.size = 65
        self.comics = []
        self.mynumber = 32
        self.name= name

    '''Group of Comics in bundlded together'''

    @property
    def do_sort_series(self):
        return sorted(self.comics,key=attrgetter('series'))

    @property
    def do_sort_issue(self):
        return sorted(self.comics,key=attrgetter('series','issue'))
        # return sorted(comic.issue for comic in sorted(comic.series for comic in self.comics) )

    @property
    def do_sort_pub_date(self):
        return sorted(self.comics,key=attrgetter('pubdate'))


    def do_sort(self,sort_by):
        if sort_by == 'Issue':
            comic_collection_sorted = self.do_sort_issue
        elif sort_by == 'Pub Date':
            comic_collection_sorted = self.do_sort_pub_date
        else:
            comic_collection_sorted = self.comics
        return comic_collection_sorted

    def add_comic(self, comic, index=0):

        '''
            Add Single comic book to this colection
        '''
        if index == 0 or len(self.comics) == 0:
            self.comics.insert(0, comic)
        else:
            comics = self.comics
            if index >= len(comics):
                index = len(comics)
            comics.insert(index, comic)
    def remove_comic(self, comic):
        '''
            Remove a comic from the comics of this collection.
        '''

        if comic not in self.comics:
            return
        self.comics.remove(comic)
        comic.collection = None

    def clear_comics(self, comics=None):
        '''
            Remove all Comics added to this Collection.
        '''

        if not comics:
            comics = self.comics
        remove_comic = self.remove_comic
        for comic in comics[:]:
            remove_comic(comic)

    def get_comic_by_number(self,comic_number):
        '''
            Will return the comic that matches id number x this number is ATM comicstreaer server id number.
        '''
        for comic in self.comics:
            if comic.comic_id_number == comic_number:
                return comic

class ComicBook(object):
    cover = ObjectProperty()
    '''
    class representing a single comic
    '''
    def __init__(self, data,*args, **kwargs):

        comic_data = data
        self.comic_json = data
        print 'comic_data:%s'%comic_data
        self.comic_id_number = comic_data['id']#this is the id number used for comicstream switched to this because of id of widget
        self.added_ts = comic_data['added_ts']
        self.month = comic_data['month']
        self.year = comic_data['year']
        self.comments = comic_data['comments']
        self.pubdate = comic_data['date']
        if comic_data['issue'].isdigit():
            self.issue = int(comic_data['issue'])
        elif comic_data['issue'].isdecimal():
            self.issue = float(comic_data['issue'])
        else:
            self.issue = 0
        self.page_count = comic_data['page_count']
        self.publisher = comic_data['publisher']
        self.series = comic_data['series']
        self.storyarcs = comic_data['storyarcs']
        self.title = comic_data['title']
        self.volume = comic_data['volume']
        self.weblink = comic_data['weblink']
        self.mod_ts = comic_data['mod_ts']
        self.page_count = comic_data['page_count']
        self.credits = comic_data['credits']
        self.characters =  comic_data['characters']
        self.characters =  comic_data['characters']

        #TODO:Add in & implement better into the comic
        #self.credits = comic_data['credits']
        #self.characters =  comic_data['characters']
        #self.characters =  comic_data['characters']

        base_url = App.get_running_app().config.get('Server', 'url')
        api_key = App.get_running_app().config.get('Server', 'api_key')
        src_thumb = "%s/comic/%s/thumbnail?api_key=%s#.jpg" % (base_url, self.comic_id_number, api_key)
        self.thumb_url  = src_thumb

    def save_cover(self,x,dt):
        data_folder = App.get_running_app().config.get('Server', 'storagedir')
        cover_file = '%s/%s.png'%(data_folder,str(self.comic_id_number))
        x.export_to_png(cover_file)
    def _proxy_loaded(self,proxyImage):
        if proxyImage.image.texture:
            x = Image(size=(130,200),allow_stretch=False,size_hint=(None, None))
            x.texture = proxyImage.image.texture
            Clock.schedule_once(partial(self.save_cover,x), .05)

    def get_cover(self):
        data_folder = App.get_running_app().config.get('Server', 'storagedir')
        cover_file = '%s/%s.png'%(data_folder,str(self.comic_id_number))
        try:
            if os.path.isfile(cover_file):
                return str(cover_file)
            else:
                proxyImage = Loader.image(self.thumb_url,nocache=True)
                proxyImage.bind(on_load=partial(self._proxy_loaded))
                return self.thumb_url

        except:
            Logger.critical('Something bad happened in loading cover')

    def json_data(self):
        pass

        # comic_data = data
        # self.comic_id_number = comic_data['id']
        # self.added_ts = comic_data['added_ts']
        # self.month = comic_data['month']
        # self.year = comic_data['year']
        # self.comments = comic_data['comments']
        # self.pubdate = comic_data['date']
        # self.issue = comic_data['issue']
        # self.page_count = comic_data['page_count']
        # self.publisher = comic_data['publisher']
        # self.series = comic_data['series']
        # self.storyarcs = comic_data['storyarcs']
        # self.title = comic_data['title']
        # self.volume = comic_data['volume']
        # self.weblink = comic_data['weblink']
        # self.mod_ts = comic_data['mod_ts']
        # self.page_count = comic_data['page_count']
        #self.credits = comic_data['credits']
        #self.characters =  comic_data['characters']
        #self.teams = comic_data['teams']


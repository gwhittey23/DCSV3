# -*- coding: utf-8 -*-
import gc
import pickle

from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from gui.widgets.custom_widgets import AppScreenTemplate
from gui.widgets.custom_widgets import CommonComicsCoverInnerGrid, \
    CommonComicsCoverLabel,CommonComicsCoverImage
from data.comic_data import ComicCollection, ComicBook
from tools.url_get import CustomUrlRequest
from data.favorites import add_collection
from utils import iterfy
from data.database import DataManager,FavCollection

class ComicCollectionScreen(AppScreenTemplate):
    comic_collection = ObjectProperty()
    def __init__(self, **kw):
        super(ComicCollectionScreen, self).__init__(**kw)




    def add_comic_items(self,comic,grid):
        comic_name = '%s #%s'%(comic.series,comic.issue)
        src_thumb = src_thumb = comic.get_cover()
        inner_grid = CommonComicsCoverInnerGrid(id='inner_grid'+str(comic.comic_id_number))
        comic_thumb = CommonComicsCoverImage(source=src_thumb,id=str(comic.comic_id_number),nocache=True,size=(dp(100),dp(154))
                                             ,allow_stretch=True,keep_ration=False
                                             )
        comic_thumb.comic = comic
        comic_thumb.comics_collection = self.collection
        inner_grid.add_widget(comic_thumb)
        # comic_thumb.bind(on_release=comic_thumb.click)
        smbutton = CommonComicsCoverLabel(text=comic_name,color=(0,0,0,1))
        inner_grid.add_widget(smbutton)
        grid.add_widget(inner_grid)

    def build_collection_from_entities(self, req, results):
        data = results
        new_collection = ComicCollection()
        comic_list_data = data['comics']
        for item in comic_list_data:
            print item
            new_comic = ComicBook(item)
            new_collection.add_comic(new_comic)

        self.collection = new_collection
        self.build_collection()

    def build_collection_from_favoritecollection(self, favorite_collection):
        new_collection = ComicCollection()

        for fav_item in iterfy(favorite_collection.fav_items):
            comic_json = fav_item.comic_json
            new_comic = ComicBook(comic_json)
            new_collection.add_comic(new_comic)
        self.collection = new_collection
        self.build_collection()


    def build_collection(self,*args):
        scroll = self.m_scroll
        scroll.clear_widgets()
        gc.collect()
        grid = GridLayout(cols=5, size_hint=(None,None),spacing=(10,40),padding=10, pos_hint = {.2,.2})
        grid.bind(minimum_height=grid.setter('height'))
        base_url = self.app.config.get('Server', 'url')
        for comic in self.collection.do_sort_issue:
            self.add_comic_items(comic,grid)
        scroll.add_widget(grid)

    def got_error(self,req, error):
        error_title = 'Server Error'
        self.app._dialog(error,error_title)
        Logger.critical('ERROR in %s %s'%(req,error))

    def get_collection_data(self,comic_collection_type,comic_collection_path):
        base_url = self.app.config.get('Server', 'url')
        api_key = self.app.config.get('Server', 'api_key')
        if comic_collection_type == 'entities':
                src_url = "%s/entities%s/comics?api_key=%s" % (base_url, comic_collection_path, api_key)
                src_url = src_url
                req = CustomUrlRequest(src_url,
                               self.build_collection_from_entities,
                               on_error=self.got_error,
                               on_failure=self.got_error,
                               on_redirect=self.got_error,
                               timeout = 55,debug=True
                               )
        elif comic_collection_type == 'favorite_collection':
            dm = DataManager()
            dm.create()
            session = dm.Session()
            if comic_collection_path is None:
                collection_name = 'Loose Comic'
                query = session.query(FavCollection).filter_by(name=collection_name).one()
                current_collection = query
                self.current_collection = current_collection
            else:
                query = session.query(FavCollection).filter_by(id=comic_collection_path).one()
                self.build_collection_from_favoritecollection(query)

    def add_collection(self):
        self.collection_pop = CollctionAddPopUp(collection=self.collection)
        self.collection_pop.hint_text = 'Enter a name you want this Collection to have'
        self.collection_pop.open()

    def submit_fav(self):
        print self.collection_pop.content.ids._textfield_name.text

class CollctionAddPopUp(Popup):
    collection = ObjectProperty()
    def __init__(self, **kwargs):
        super(CollctionAddPopUp, self).__init__(**kwargs)

    def submit_fav(self):
        if self.textfield_name.text:
            self.collection.name = self.textfield_name.text
            add_collection(self.collection)
            self.dismiss()
        else:
            self.err_lbl.text = 'You Must Enter a Name'

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


class ComicCollectionScreen(AppScreenTemplate):
    comic_collection = ObjectProperty()
    def __init__(self, **kw):
        super(ComicCollectionScreen, self).__init__(**kw)





    def build_collection(self,req, results):

        data = results
        new_collection = ComicCollection()
        comic_list_data = data['comics']
        for item in comic_list_data:
            new_comic = ComicBook(item)
            new_collection.add_comic(new_comic)

        self.collection = new_collection
        scroll = self.m_scroll
        scroll.clear_widgets()
        gc.collect()
        # scroll = ScrollView( size_hint=(.99,.85), do_scroll_y=True, do_scroll_x=False,
        #                      pos_hint={'x': .01, 'center_y': .6},id = 'scroller' )
        #TODO Chagne spaceing make vert spacing bigger and horz smaller

        grid = GridLayout(cols=5, size_hint=(None,None),spacing=(10,40),padding=10, pos_hint = {.2,.2})
        grid.bind(minimum_height=grid.setter('height'))
        base_url = self.app.config.get('Server', 'url')
        for comic in self.collection.do_sort_issue:
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
        base_url = self.app.config.get('Server', 'url')
        api_key = self.app.config.get('Server', 'api_key')
        src_url = src_url
        req = CustomUrlRequest(src_url,
                               self.build_collection,
                               on_error=self.got_error,
                               on_failure=self.got_error,
                               on_redirect=self.got_error,
                               timeout = 55,debug=True
                               )
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

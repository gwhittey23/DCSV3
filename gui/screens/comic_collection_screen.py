# -*- coding: utf-8 -*-
from gui.widgets.custom_widgets import AppScreenTemplate,AppNavDrawer
from kivy.properties import ObjectProperty
from gui.widgets.custom_widgets import CommonComicsInnerGrid,\
    CommonComicsOuterGrid,CommonComicsPagebntlbl,CommonComicsPageImage,CommonComicsScroll
from data.comic_data import ComicCollection, ComicBook
from comicstream.url_get import CustomUrlRequest
from kivy.logger import Logger
from operator import itemgetter, attrgetter, methodcaller
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import gc
class ComicCollectionScreen(AppScreenTemplate):
    comic_collection = ObjectProperty()
    def __init__(self, **kw):
        super(ComicCollectionScreen, self).__init__(**kw)

    def go_comic_screen(self):
        if self.app.comic_loaded == 'yes':
            self.app.manager.current = 'comic_book_screen'
        else:
            self.app.dialog_error('No Comic Loaded','Comic Screen Error')

    def build_comic_collection_screen(self,):

        self.toolbar.add_action_button("md-home", lambda *x:self.go_home())
        self.toolbar.add_action_button("md-my-library-books",lambda *x: self.go_comic_screen() )
        self.toolbar.add_action_button("md-settings",lambda *x: self.open_settings())
        self.tile_icon_data = [
                                {'icon': '', 'text': '',
                                'secondary_text': '',
                                'callback': ''},
                                {'icon': 'md-event', 'text': 'Event',
                                'secondary_text': "An event button",
                                'callback':''},
                                {'icon':  'md-search', 'text': 'Search',
                                'secondary_text': "A search button",
                                'callback': self.nav.toggle_state},
                                {'icon': 'md-thumb-up', 'text': 'Like',
                                'secondary_text': "A like button",
                                'callback': self.nav.toggle_state}

                               ]


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

        grid = GridLayout(cols=4, size_hint=(None,None),spacing=(10,40),padding=10, pos_hint = {.2,.2})
        grid.bind(minimum_height=grid.setter('height'))
        base_url = self.app.config.get('Server', 'url')
        for comic in self.collection.do_sort_issue:
            comic_name = '%s #%s'%(comic.series,comic.issue)
            src_thumb = comic.thumb_url
            inner_grid = CommonComicsInnerGrid(id='inner_grid'+str(comic.comic_id_number))
            comic_thumb = CommonComicsPageImage(source=src_thumb,id=str(comic.comic_id_number),nocache=True)
            comic_thumb.comic = comic
            comic_thumb.comics_collection = self.collection
            inner_grid.add_widget(comic_thumb)
            comic_thumb.bind(on_release=comic_thumb.click)
            smbutton = CommonComicsPagebntlbl(text=comic_name)
            inner_grid.add_widget(smbutton)
            grid.add_widget(inner_grid)
        scroll.add_widget(grid)

    def got_error(self,req, error):
        error_title = 'Server Error'
        self.app.dialog_error(error,error_title)
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

# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.properties import ObjectProperty, ListProperty
from kivy.logger import Logger

from gui.widgets.custom_widgets import AppScreenTemplate,AppNavDrawer
from data.comic_data import ComicCollection, ComicBook
from tools.url_get import CustomUrlRequest

from gui.widgets.custom_widgets import CommonComicsCoverInnerGrid,\
    CommonComicsOuterGrid,CommonComicsCoverLabel,CommonComicsCoverImage
from kivy.uix.popup import Popup

class HomeScreen(AppScreenTemplate):
    tile_icon_data = ListProperty()

    nav = ObjectProperty()
    def __init__(self,**kwargs):
        super(HomeScreen, self).__init__(**kwargs)

    def do_series(self):
        self.app.manager.current = 'favorites_screen'

    def on_enter(self, *args):
        self.build_recent_comics()
        super(HomeScreen, self).on_enter(*args)

    def do_entities(self):
        self.app.manager.current = 'entities_screen'

    def test_me(self):
      print  self.collection.do_sort_issue


    def build_collection(self,req, results):

        data = results
        new_collection = ComicCollection()
        for item in data['comics']:
            new_comic = ComicBook(item)
            new_collection.add_comic(new_comic)
            # f = open('comic_collection.pickle', 'w')
            # pickle.dump(new_collection,f)
        self.collection = new_collection
        scroll = self.ids.recent_comics_scroll
        scroll.clear_widgets()
        grid = CommonComicsOuterGrid(id='outtergrd')
        grid.bind(minimum_width=grid.setter('width'), )
        base_url = self.app.config.get('Server', 'url')
        for comic in self.collection.comics:
            comic_name = '%s #%s'%(str(comic.series),str(comic.issue))

            src_thumb = comic.get_cover()
            inner_grid = CommonComicsCoverInnerGrid(id='inner_grid'+str(comic.comic_id_number))
            comic_thumb = CommonComicsCoverImage(source=src_thumb,id=str(comic.comic_id_number))
            comic_thumb.comic = comic
            comic_thumb.comics_collection = self.collection
            inner_grid.add_widget(comic_thumb)
            # comic_thumb.bind(on_release=comic_thumb.click)
            smbutton = CommonComicsCoverLabel(text=comic_name)
            inner_grid.add_widget(smbutton)
            grid.add_widget(inner_grid)
        scroll.add_widget(grid)

    def got_error(self,req, error):
            error_title = 'Server Error'
            self.app._dialog(error,error_title)
            Logger.critical('ERROR in %s %s'%(req,error))

    def build_recent_comics(self):

        base_url = App.get_running_app().config.get('Server', 'url')
        api_key = App.get_running_app().config.get('Server', 'api_key')
        recent_url  = "%s/comiclist?api_key=%s&order=-added&per_page=10" % (base_url,api_key)
        req = CustomUrlRequest(recent_url,
                               self.build_collection,
                               on_error=self.got_error,
                               on_failure=self.got_error,
                               on_redirect=self.got_error,
                               timeout = 15,debug=True
                               )
    def do_pop(self):
        self.collection_pop = CollctionAddPopUp()
        self.collection_pop.open()

    def call_test(self):
        print self.collection

#<<<<Following are class for recent list>>>>>>>>>


#<<<<<<<<<<
class HomeScreeNavigationDrawer(AppNavDrawer):
    pass

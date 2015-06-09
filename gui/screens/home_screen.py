from kivy.app import App
from kivy.uix.image import AsyncImage
from kivy.uix.button import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from comicstream.comic_data import ComicCollection, ComicBook
from kivy.uix.screenmanager import Screen
from comicstream.url_get import CustomUrlRequest
from gui.widgets.custom_widgets import AppScreenTemplate,AppNavDrawer
from gui.widgets.custom_effects import RectangularRippleBehavior,CircularRippleBehavior

from kivy.logger import Logger
import inspect




class HomeScreen(AppScreenTemplate):
    def __init__(self,**kwargs):
        super(HomeScreen, self).__init__(**kwargs)


    def test_me(self):
        print self.collection.size
    def build_home_screen(self):
        root = self
        app = App.get_running_app()

        root.toolbar.nav_button = ["md-keyboard-backspace",'']
        root.toolbar.add_action_button("md-book")
        root.toolbar.add_action_button("md-settings",lambda *x: app.open_settings())


        self.tile_data = [{'text': "Button 1", 'secondary_text': "With a secondary text"},
                          {'text': "Button 2", 'secondary_text': "With a secondary text"},
                          {'text': "Button 3", 'secondary_text': "With a secondary text"},
                          {'text': "Button 4", 'secondary_text': "With a secondary text"}]

        self.tile_single_data = [{'text': "Button 1"},
                                  {'text': "Button 2"},
                                  {'text': "Button 3"},
                                  {'text': "Button 4"}]

        self.tile_icon_data = [
                                {'icon': 'md-alarm', 'text': 'Alarm',
                                'secondary_text': "An alarm button",
                                'callback': self.toggle_nav},
                                {'icon': 'md-event', 'text': 'Event',
                                'secondary_text': "An event button",
                                'callback':self.toggle_nav},
                                {'icon':  'md-search', 'text': 'Search',
                                'secondary_text': "A search button",
                                'callback': self.toggle_nav},
                                {'icon': 'md-thumb-up', 'text': 'Like',
                                'secondary_text': "A like button",
                                'callback': self.toggle_nav}

                               ]

        self.tile_link_data = [
                                {'icon': 'md-list', 'text': 'Series',
                                'secondary_text': "A list of Series",
                                'callback':''},
                                {'icon': 'md-event', 'text': 'Event',
                                'secondary_text': "An event button",
                                'callback':''},
                                {'icon':  'md-search', 'text': 'Search',
                                'secondary_text': "A search button",
                                'callback': self.toggle_nav},
                                {'icon': 'md-thumb-up', 'text': 'Like',
                                'secondary_text': "A like button",
                                'callback': self.toggle_nav}

                               ]




        self.build_recent_comics()
    def build_collection(self,req, results):
        print self.ids
        data = results
        new_collection = ComicCollection()
        for item in data['comics']:
            new_comic = ComicBook(item)
            new_collection.add_comic(new_comic)
        print new_collection.size
        self.collection = new_collection
        scroll = self.ids.recent_comics_scroll
        grid = RecentComicsOuterGrid(id='outtergrd')
        grid.bind(minimum_width=grid.setter('width'), )
        base_url = App.get_running_app().config.get('Server', 'url')
        for comic in self.collection.comics:
            comic_name = '%s #%s'%(str(comic.series),str(comic.issue))
            src_thumb = comic.thumb_url
            inner_grid = RecentComicsInnerGrid(id='inner_grid'+str(comic.comic_id_number))
            comic_thumb = RecentComicsPageImage(source=src_thumb,id=str(comic.comic_id_number))
            comic_thumb.comic = comic
            comic_thumb.comics_collection = self.collection
            inner_grid.add_widget(comic_thumb)
            comic_thumb.bind(on_release=comic_thumb.click)
            smbutton = RecentComicsPagebntlbl(text=comic_name)
            inner_grid.add_widget(smbutton)
            grid.add_widget(inner_grid)
        scroll.add_widget(grid)
    def got_error(self,req, results):
        print 'got_error'
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    def got_time_out(self,req, results):
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    def got_failure(self,req, results):
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    def got_redirect(self,req, results):
        Logger.critical('ERROR in %s %s > %s'%(inspect.stack()[0][3],req,results))
    def build_recent_comics(self):

        self.base_url = App.get_running_app().config.get('Server', 'url')
        recent_list  = "%s/comiclist?order=-added&per_page=10" % (self.base_url)
        req = CustomUrlRequest(recent_list,
                               self.build_collection,
                               on_error=self.got_error,
                               on_failure=self.got_failure,
                               on_redirect=self.got_redirect,
                               timeout = 15,
                               )

    def call_test(self):
        print self.collection

#<<<<Following are class for recent list>>>>>>>>>
class RecentComicsScroll(ScrollView):
    pass

class RecentComicsOuterGrid(GridLayout):
    pass

class RecentComicsPagebntlbl(Label):
    pass

class RecentComicsInnerGrid(GridLayout):
    pass

class RecentComicsPageImage(RectangularRippleBehavior,ButtonBehavior,AsyncImage):
    comic = ObjectProperty()
    comics_collection = ObjectProperty()
    def enable_me(self,instance):
        Logger.debug('enabling %s'%self.id)
        self.disabled = False
    # def on_press(self):
    #     self.disabled = True
    #     app = App.get_running_app()
    #     app.root.current = 'comic_screen'
    #     comic_screen = app.root.get_screen('comic_screen')
    #     comic_screen.load_comic(self.comic,self.comics_collection)
    #     Clock.schedule_once(lambda x:self.enable_me, .05)
    #
    # def on_release(self,instance):
    #     self.disabled = True
    #     app = App.get_running_app()
    #     app.root.current = 'comic_screen'
    #     comic_screen = app.root.get_screen('comic_screen')
    #     comic_screen.load_comic(self.comic,self.comics_collection)
    #     Clock.schedule_once(lambda x:self.enable_me, .05)
    #     return super(RecentComicsPageImage, self).on_release(instance)
    def click(self,instance):
        self.disabled = True
        app = App.get_running_app()
        app.root.current = 'comic_book_screen'
        comic_screen = app.root.get_screen('comic_book_screen')
        comic_screen.load_comic_book(self.comic,self.comics_collection)
        Clock.schedule_once(self.enable_me, .05)

#<<<<<<<<<<
class HomeScreeNavigationDrawer(AppNavDrawer):
    pass
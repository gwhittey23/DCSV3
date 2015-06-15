# -*- coding: utf-8 -*-
from urllib import quote
import inspect

from kivy.properties import ListProperty,ObjectProperty,StringProperty
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger

from gui.widgets.custom_widgets import AppNavDrawer
from tools.url_get import CustomUrlRequest
from gui.theme_engine.button import RaisedButton


class SeriesScreen(Screen):
    tile_icon_data = ListProperty()
    nav = ObjectProperty()
    series_list = ListProperty()
    series_data = ListProperty([])
    def __init__(self, **kw):
        super(SeriesScreen, self).__init__(**kw)

        app = App.get_running_app()
        self.toolbar.nav_button = ["md-keyboard-backspace",'']
        self.toolbar.add_action_button("md-book",lambda *x: self.switch_screen_comic() )
        self.toolbar.add_action_button("md-settings",lambda *x: app.open_settings())
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


    def on_pre_enter(self, *args):
        super(SeriesScreen, self).on_pre_enter(*args)
        self.get_series_data()

    def switch_screen_comic(self):
        if self.app.comic_loaded == 'yes':
            self.app.manager.current = 'comic_book_screen'
        else:
            self.app._dialog('No Comic Loaded','Comic Screen Error')

    def got_time_out(self,req, error):
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],error))

    def got_failure(self,req, error):
        Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],error))

    def got_redirect(self,req, error):
        Logger.critical('ERROR in %s %s > %s'%(inspect.stack()[0][3],req,error))

    def got_error(self,req, error):
        Logger.critical('ERROR in %s %s'%(req,error))

    def get_series_data(self):
        self.base_url = App.get_running_app().config.get('Server', 'url')
        recent_list  = "%s/entities/series" % (self.base_url)
        req = CustomUrlRequest(recent_list,
                               self.build_series_list,
                               on_error=self.got_error,
                               on_failure=self.got_failure,
                               on_redirect=self.got_redirect,
                               timeout = 15,debug=True,
                               )

    def build_list_display(self,req, results):
        print results
        # scroll = ScrollView( size_hint=(.95,.85), do_scroll_y=True, do_scroll_x=False,
        #                      pos_hint={'x': .05, 'y': .01} )
        # grid = GridLayout(cols=1, size_hint=(1,None),spacing=10,padding=10)
        # grid.bind(minimum_height=grid.setter('height'))
        # for letter, words in groupby(sorted(self.series_list), key=itemgetter(0)):
        #     print letter
        #     letter_button = Label(text=letter,height=(1), size_hint=(None,None),opacity=1,id=letter )
        #     grid.add_widget(letter_button)
        #     for word in words:
        #         page_button = Button(text=word,height=(25), size_hint=(.9, None))
        #         grid.add_widget(page_button)
        # scroll.add_widget(grid)
        # self.add_widget(scroll)

    def build_series_list(self,req, results):
        self.series_list = results['series']
        for  series_name in self.series_list:
            string = quote(series_name.encode('utf8'))


            url  = "%s/entities/series/%s" % (self.base_url,string)
            print url
            req = CustomUrlRequest(url,
                                   self.build_list_display,
                                   on_error=self.got_error,
                                   on_failure=self.got_failure,
                                   on_redirect=self.got_redirect,
                                   timeout = 15,
                                   )


    def on_leave(self):
        app = App.get_running_app()
        app.manager.last_screen = self

class SeriesScreenNavigationDrawer(AppNavDrawer):
    pass

class SeriesItemButton(RaisedButton):
    series_name = StringProperty()
    def load_series(self):
        print self.series_name
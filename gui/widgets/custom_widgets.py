# -*- coding: utf-8 -*-
from gui.theme_engine.theme import ThemeBehaviour
from gui.navigationdrawer import NavigationDrawer
from kivy.app import App
from kivy.properties import *
from kivy.uix.image import AsyncImage
from kivy.uix.button import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from gui.widgets.custom_effects import RectangularRippleBehavior
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger

class AppNavDrawer(ThemeBehaviour,NavigationDrawer):
    header_img = StringProperty()

    _header_bg = ObjectProperty()
    _bl_items = ObjectProperty()

class AppScreenTemplate(Screen):
    tile_icon_data = ListProperty()
    test_icon_data = ListProperty()
    tile_link_data = ListProperty()
    app =  ObjectProperty()
    last_screen = ObjectProperty()
    def __init__(self, **kw):
        super(AppScreenTemplate, self).__init__(**kw)
        self.app = App.get_running_app()
    def toggle_nav(self):
        if self.nav.state != "open":
            return
        self.nav.toggle_state()
    def on_leave(self):
        app = App.get_running_app()
        app.manager.last_screen = self
    def on_leave(self):
        self.app.manager.last_screen = self

    def load_last_screen(self):

        last_screen = self.app.manager.last_screen
        if last_screen:self.app.manager.current = last_screen.name
        return
    def go_home(self):
        self.app.manager.current = 'home_screen'

class CommonComicsScroll(ScrollView):
    pass

class CommonComicsOuterGrid(GridLayout):
    pass

class CommonComicsPagebntlbl(Label):
    pass

class CommonComicsInnerGrid(GridLayout):
    pass

class CommonComicsPageImage(RectangularRippleBehavior,ButtonBehavior,AsyncImage):
    comic = ObjectProperty()
    comics_collection = ObjectProperty()
    def enable_me(self,instance):
        Logger.debug('enabling %s'%self.id)
        self.disabled = False

    def click(self,instance):
        self.disabled = True
        app = App.get_running_app()
        app.root.current = 'comic_book_screen'
        comic_screen = app.root.get_screen('comic_book_screen')
        comic_screen.load_comic_book(self.comic,self.comics_collection)
        Clock.schedule_once(self.enable_me, .05)
from kivy.uix.screenmanager import Screen
from kivy.app import App
from gui.theme_engine.theme import ThemeBehaviour
from gui.navigationdrawer import NavigationDrawer
from kivy.properties import *


class AppNavDrawer(ThemeBehaviour,NavigationDrawer):
    header_img = StringProperty()

    _header_bg = ObjectProperty()
    _bl_items = ObjectProperty()

class AppScreenTemplate(Screen):
    tile_icon_data = ListProperty()
    test_icon_data = ListProperty()
    tile_link_data = ListProperty()
    def toggle_nav(self):

        if self.nav.state != "open":
            return
        self.nav.toggle_state()

    def on_leave(self):
        app = App.get_running_app()
        app.manager.last_screen = self



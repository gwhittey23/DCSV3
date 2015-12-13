# -*- coding: utf-8 -*-
__version__ = '1.0000000135'

DEBUG = True
import kivy
kivy.require('1.9.1')
if DEBUG:
    from kivy.config import Config

from settings.settingsjson import settings_json_server,settings_json_dispaly,settings_json_screen_tap_control
from kivy.uix.screenmanager import ScreenManager
#from csvdb.csvdroid_db import build_db
from gui.theme_engine.dialog import Dialog
#from kivy.core.window import Window
#from kivy.modules import keybinding, webdebugger

from gui.theme_engine.theme import ThemeManager
from gui.screens.comic_book_screen import ComicBookScreen
from gui.screens.home_screen import HomeScreen
from gui.screens.entities_screen import EntitiesScreen
from gui.screens.favorites_screen import FavoritesScreen
from gui.screens.comic_collection_screen import ComicCollectionScreen
from gui.theme_engine.list import MaterialList
from gui.theme_engine.textfields import SingleLineTextField
from gui.theme_engine.toolbar import Toolbar
from kivy.uix.settings import SettingsWithSidebar
# from memory_profiler import profile
from kivy.app import App
from gui.screens.home_screen import HomeScreen
from kivy.properties import ListProperty, ObjectProperty,StringProperty
from gui.theme_engine.theme import ThemeManager
from kivy.metrics import dp
from gui.theme_engine.label import MaterialLabel

# import cProfile
# import pstats

class ErrorLabel(MaterialLabel):
    def __init__(self, **kwargs):
        super(ErrorLabel, self).__init__(**kwargs)


class AppScreenManager(ScreenManager):
    last_screen = ObjectProperty()

    def __init__(self, **kwargs):
        super(AppScreenManager, self).__init__(**kwargs)


class MainApp(App):
    theme_cls = ThemeManager()
    version = __version__
    tile_data = ListProperty([])
    tile_single_data = ListProperty([])
    tile_icon_data = ListProperty()
    tile_avatar_data = ListProperty()
    base_url = StringProperty()
    use_api_key = StringProperty()
    api_key = StringProperty()
    comic_loaded = StringProperty()

    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        ''' ['Pink', 'Blue', 'Indigo', 'BlueGrey', 'Brown', 'LightBlue', 'Purple', 'Grey', 'Yellow',
            'LightGreen', 'DeepOrange', 'Green', 'Red', 'Teal', 'Orange', 'Cyan', 'Amber', 'DeepPurple', 'Lime']
'''
        self.theme_cls.primary_palette = 'Teal'
        self.theme_cls.accent_palette = 'Green'
        self.theme_cls.theme_style = 'Dark'
        self.comic_loaded = 'no'
    def on_start(self):

        # self.profile = cProfile.Profile()
        # self.profile.enable()
        pass
    def on_stop(self):
        # self.profile.disable()
        # self.profile.dump_stats('main.profile')
        # p = pstats.Stats('main.profile')
        # print ';ok dumped'
        # p.strip_dirs().sort_stats(-1).dump_stats('1')
        # p.sort_stats('time').print_stats(100)
        pass

    def test_me(self):
        print 'main app test me'

    def build(self):
        self.icon = 'logo.png'
        self.settings_cls = SettingsWithSidebar
        if DEBUG == False :self.use_kivy_settings = False
        self.manager = AppScreenManager()
        self.manager.get_screen('home_screen').build_nav()
        self.manager.get_screen('entities_screen').build_nav()
        self.manager.get_screen('comic_collection_screen').build_nav()
        self.manager.get_screen('favorites_screen').build_nav()
        # keybinding.start(Window, App)
        # webdebugger.start(Window, App)
        dbl_tap_time = self.config.get('Screen Tap Control','dbl_tap_time')
        Config.set('postproc', 'double_tap_time', dbl_tap_time)
        return self.manager

    # @profile()
    def build_config(self, config):
        config.setdefaults('Server', {
            'url':          'http://',
            'storagedir':       self.user_data_dir,
            'max_height':       0,
            'use_api_key':      0,
            'api_key':          '',
            'max_pages_limit'   :50,
            })

        config.setdefaults('Display', {
            'mag_glass_size':   200,
            'right2left':       0,
            'dblpagesplit':     '0',
            'stretch_image':    '0',

            })

        config.setdefaults('Screen Tap Control', {
            'bottom_right':     'Next Page',
            'bottom_left':      'Prev Page',
            'bottom_center':    'Open Page Nav',
            'top_right':        'Return to Home Screen',
            'top_left':         'Prev Page',
            'top_center':       'Open Collection Browser',
            'middle_right':     'Next Comic',
            'middle_left':      'Prev Comic',
            'middle_center':    'Open Collection Browser',
            'dbl_tap_time':      250,
            })

    def build_settings(self, settings):
        settings.add_json_panel('Server Settings',
                                self.config,
                                data=settings_json_server)
        settings.add_json_panel('Display Settings',
                                self.config,
                                data=settings_json_dispaly)
        settings.add_json_panel('Screen Tap Control',
                                self.config,
                                data=settings_json_screen_tap_control)

    def on_config_change(self, config, section,
                         key, value):
        if key =='dbl_tap_time':
            Config.set('postproc', 'double_tap_time', value)


    def on_pause(self):
      # Here you can save data if needed
         return True

    def on_resume(self):
      # Here you can check if any data needs replacing (usually nothing)
        pass

#        self.manager.get_screen('comic_screen')._abort_download()
    def _dialog(self,error_msg,error_title,s_hint=(.4, .3),font_style='Body1'):
        content = ErrorLabel(font_style=font_style,
                                theme_text_color='Secondary',
                                text="%s"%error_msg,
                                valign='middle',

                                )
        self.error_dialog = Dialog(title=error_title,
                             content=content,
                             size_hint=s_hint,
                             height=dp(250),
                             auto_dismiss=True)
        self.error_dialog.add_action_button("Dismiss", action=lambda *x: self.error_dialog.dismiss())
        self.error_dialog.open()







if __name__ == '__main__':
    MainApp().run()

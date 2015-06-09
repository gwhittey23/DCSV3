__version__ = '1.0000000028'
import sys
sys.path.append( '..' )
DEBUG = True
import kivy
kivy.require('1.9.1')
if DEBUG:
    from kivy.config import Config
    print 'setting windows size'
    Config.set('graphics', 'width', '600')
    Config.set('graphics', 'height', '1024')
from kivy.app import App
from data.settingsjson   import settings_json_server,settings_json_dispaly

from kivy.uix.screenmanager import ScreenManager
#from csvdb.csvdroid_db import build_db

from kivy.core.window import Window
from kivy.modules import keybinding
from gui.theme_engine.theme import ThemeManager
from gui.theme_engine.toolbar import Toolbar
from gui.theme_engine.list import MaterialList
from gui.screens.comic_book_screen import ComicBookScreen
from gui.screens.home_screen import HomeScreen
from kivy.uix.settings import SettingsWithSidebar,SettingsWithTabbedPanel
# from memory_profiler import profile



class AppScreenManager(ScreenManager):
    pass

class MainApp(App):
    theme_cls = ThemeManager()
    version = __version__
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.theme_cls.primary_palette = 'Grey'
        self.theme_cls.accent_palette = 'Teal'
        self.theme_cls.theme_style = 'Dark'
    def build(self):
        self.settings_cls = SettingsWithSidebar

        self.manager = AppScreenManager()
        self.manager.get_screen('home_screen').build_home_screen()

        keybinding.start(Window, App)
        return self.manager

    # @profile()
    def build_config(self, config):
        config.setdefaults('Server', {
            'url': 'http://',
            'storagedir': self.user_data_dir,
            'max_height': 0
            })

        config.setdefaults('Display', {
            'mag_glass_size': 200,
            'right2left':       0,
            'dblpagesplit': self.user_data_dir,

            })


    def build_settings(self, settings):
        settings.add_json_panel('Server Settings',
                                self.config,
                                data=settings_json_server)
        settings.add_json_panel('Display Settings',
                                self.config,
                                data=settings_json_dispaly)

    def on_config_change(self, config, section,
                         key, value):
        print config, section, key, value

    def on_pause(self):
      # Here you can save data if needed
         return True

    def on_resume(self):
      # Here you can check if any data needs replacing (usually nothing)
        pass

    def on_stop(self):
        pass
#        self.manager.get_screen('comic_screen')._abort_download()


if __name__ == '__main__':
    MainApp().run()
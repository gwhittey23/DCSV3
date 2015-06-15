# -*- coding: utf-8 -*-
from urllib import quote,unquote
import inspect

from kivy.properties import ListProperty, ObjectProperty, StringProperty, NumericProperty
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from kivy.uix.gridlayout import GridLayout
#from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from itertools import groupby
from operator import itemgetter
from gui.widgets.custom_widgets import AppNavDrawer, AppScreenTemplate
from comicstream.url_get import CustomUrlRequest
from gui.theme_engine.button import RaisedButton
from gui.theme_engine.ripplebehavior import RectangularRippleBehavior
from gui.theme_engine.list import MaterialList
from gui.theme_engine.theme import ThemeBehaviour
from gui.theme_engine.layouts import BackgroundColorCapableWidget
from kivy.metrics import dp
from kivy.clock import Clock
from functools import partial

import os

class EntitiesScreen(AppScreenTemplate):
    tile_icon_data = ListProperty()
    nav = ObjectProperty()
    series_list = ListProperty()
    entities_data = ListProperty([])
    entities_path = StringProperty()
    number_per_page = NumericProperty()
    current_page_number = NumericProperty()
    up_level = StringProperty()

    def on_enter(self, *args):
        super(EntitiesScreen, self).on_enter(*args)
        self.get_entities_data('', '')

    def __init__(self, **kw):

        self.number_per_page = 400
        super(EntitiesScreen, self).__init__(**kw)

    def got_time_out(self, req, error):
        Logger.critical('ERROR in %s %s' % (inspect.stack()[0][3], error))

    def got_failure(self, req, error):
        Logger.critical('ERROR in %s %s' % (inspect.stack()[0][3], error))

    def got_redirect(self, req, error):

        Logger.critical('ERROR in %s %s > %s' % (inspect.stack()[0][3], req, error))

    def got_error(self, req, error):
        error_title = 'Server Error'
        self.app.dialog_error(error, error_title)
        Logger.critical('ERROR in %s %s' % (req, error))

    def go_comic_collection_screen(self, comic_collection_path,callback):
        comic_collection_screen = self.app.manager.get_screen('comic_collection_screen')
        comic_collection_type = 'entities'
        self.app.manager.current = 'comic_collection_screen'
        comic_collection_screen.get_collection_data(comic_collection_type,comic_collection_path)

    def build_list_display(self, req, results):
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

    def go_to_root(self):
        self.entities_path = ''
        self.get_entities_data('','')

    def go_up_level(self):

        self.get_entities_data('up level','')

    def get_entities_data(self, entities_key, callback):
        base_url = App.get_running_app().config.get('Server', 'url')
        api_key = App.get_running_app().config.get('Server', 'api_key')
        if '/' in entities_key:
            self.app.dialog_error(
                                'Please use search for %s name due to the "/" \nin the name as server is unable to process this ' %
                                (entities_key),'%s Naming Error' % (entities_key), (.9, .3), 'Subhead')
            return



        if entities_key == 'up level':
            r_place = os.path.basename(os.path.normpath(self.entities_path))
            r_place = '/%s'%r_place
            url_path = self.entities_path.replace(r_place,'')
            entities_key = ''
        elif entities_key == '':
            url_path = ''
        else:
            entities_key = quote(entities_key.encode('utf8'))
            url_path = "%s/%s" % (self.entities_path, entities_key)
        self.up_level = self.entities_path
        self.entities_path = url_path
        self.ids.entities_location.text = unquote(url_path)
        entities_list = "%s/entities%s?api_key=%s" % (base_url, url_path, api_key)

        req = CustomUrlRequest(entities_list,
                               self.build_entities_list,
                               on_error=self.got_error,
                               on_failure=self.got_failure,
                               on_redirect=self.got_redirect,
                               timeout=15, debug=True,
                               )

    def build_entities_list(self, req, results):
        bnt_size = dp(65)
        for child in self.walk():
            if child.id == 'entities_scroll':
                child.clear_widgets()
        self.entities_data = []
        for key in results.keys():
            if key == 'entities':
                key_name = 'entities'
            else:
                key_name = key
        data = results[key_name]
        self.letter_bnt_stack.clear_widgets()
        scroll = self.m_scroll
        scroll.clear_widgets()
        grid = GridLayout(cols=1, size_hint=(1, None), spacing=10, padding=10)
        grid.clear_widgets()
        grid.bind(minimum_height=grid.setter('height'))
        if key_name == 'entities':
            for entitie in data:
                if entitie['count'] > 0:
                    if entitie['name'] != 'comics':
                        fixed_entite_name = entitie['name'].replace('/', '%2F')
                        entitie_text = '%s(%s)' % (entitie['name'].title(), str(entitie['count']))
                        page_button = EntitieItemButton(text=entitie_text, height=(bnt_size), size_hint=(.9, None))
                        page_button.bind(on_release=partial(self.get_entities_data, entitie['name']))
                        page_button.bind(on_release=partial(page_button.anti_click))
                        grid.add_widget(page_button)
                    else:
                        entitie_text = 'Click to open %s in Collection Screen(%s)' % (
                        entitie['name'].title(), str(entitie['count']))
                        page_button = EntitieItemButton(text=entitie_text, height=(bnt_size), size_hint=(.9, None))
                        page_button.bind(on_release=partial(self.go_comic_collection_screen, self.entities_path))
                        page_button.bind(on_release=partial(page_button.anti_click))
                        grid.add_widget(page_button)
        elif key_name == 'volumes':
            for item in data:
                if item == None:data.remove(item)
            if len(data) > 1:
                for item in data[0:self.number_per_page]:
                    page_button = EntitieItemButton(text=str(item), height=(bnt_size), size_hint=(.9, None))
                    page_button.bind(on_release=partial(self.get_entities_data, str(item)))
                    page_button.bind(on_release=partial(page_button.anti_click))
                    grid.add_widget(page_button)
            else:
                page_button = EntitieItemButton(text=str(data[0]), height=(bnt_size), size_hint=(.9, None))
                page_button.bind(on_release=partial(self.get_entities_data, str(data[0])))
                page_button.bind(on_release=partial(page_button.anti_click))
                grid.add_widget(page_button)
        else:
            for item in data:
                if item == None:data.remove(item)
            if len(data) > 1:
                for letter, words in groupby(sorted(data[0:self.number_per_page]), key=itemgetter(0)):
                    letter_button = LetterButtons(id=letter,text=letter.title())
                    letter_label = Label(text=str(letter), height=(1), size_hint=(None, None), opacity=1, id=letter)
                    grid.add_widget(letter_label)
                    self.letter_bnt_stack.add_widget(letter_button)
                    letter_button.bind(on_press=letter_button.click)
                    for word in words:
                            word = word.encode('utf8')
                            page_button = EntitieItemButton(text=str(word),height=(bnt_size), size_hint=(.9, None))
                            if not '/' in word:
                                page_button.bind(on_release=partial(self.get_entities_data, word))
                                page_button.bind(on_release=partial(page_button.anti_click))

                            else:
                                page_button.bind(on_release=self.entities_name_error)
                                page_button.bind(on_release=partial(page_button.anti_click))
                            grid.add_widget(page_button)
            else:
                page_button = EntitieItemButton(text=str(data[0]), height=(bnt_size), size_hint=(.9, None))
                page_button.bind(on_release=partial(self.get_entities_data, str(data[0])))
                page_button.bind(on_release=partial(page_button.anti_click))
                grid.add_widget(page_button)
        scroll.add_widget(grid)



        #
        # if key_name == 'entities':
        #     first_entry = { 'text': 'Entities_list','secondary_text': "List of Further Options",'callback': ''}
        #     self.entities_data.append(first_entry)
        #     for item in data:
        #         dict = {}
        #         dict['text'] = item['name'].title()
        #         dict['secondary_text'] = 'Total %s in this entry %s'%( item['name'], item['count'])
        #         self.entities_data.append(dict)
        # else:
        #     first_entry = { 'text': 'Next Page','secondary_text': "List of Further Options",'callback': ''}
        #     self.entities_data.append(first_entry)
        #     for item in  data[1:self.number_per_page]:
        #         dict = {}
        #         dict['text'] = item.title()
        #         dict['secondary_text'] = ''
        #         self.entities_data.append(dict)

    def entities_name_error(self,*args):
        self.app.dialog_error('This has a / in name so browsing disabled','Naming Error', (.5, .3), 'Subhead')
        return

    def on_leave(self):
        app = App.get_running_app()
        app.manager.last_screen = self

class EntitieScreenNavigationDrawer(AppNavDrawer):
    pass

class EntitieItemButton(ThemeBehaviour,RectangularRippleBehavior,Button):
    def __init__(self, **kwargs):
        super(EntitieItemButton, self).__init__(**kwargs)
        self.background_normal= ''
        self.background_color = self._theme_cls.primary_color
        self.background_color_down = self._theme_cls.primary_dark
        self.background_color_disabled = self._theme_cls.disabled_bg_color()

    def enable_me(self,instance):
        Logger.debug('enabling %s'%self.id)
        self.disabled = False

    def anti_click(self,*args):
        self.disabled = True
        Clock.schedule_once(self.enable_me, .5)


class LetterButtons(ThemeBehaviour,RectangularRippleBehavior,Button):
    def __init__(self, **kwargs):
        super(LetterButtons, self).__init__(**kwargs)
        self.background_normal= ''
        self.background_down = ''
        self.background_color = self._theme_cls.primary_color
        self.background_color_down = self._theme_cls.primary_dark

        self.size_hint = None, None
        self.size =dp(20), dp(36)

    def click(self,btn):
        app = App.get_running_app()
        # app.root.current = 'comic_book_screen'
        entities_screen = app.manager.get_screen('entities_screen')
        scroller = entities_screen.m_scroll
        for child in entities_screen.walk():
            if child.id == btn.id:
                scroller.scroll_to(child,padding=10, animate=True)
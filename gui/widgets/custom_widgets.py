# -*- coding: utf-8 -*-
from kivy.uix.togglebutton import ToggleButton
from gui.theme_engine.theme import ThemeBehaviour
from gui.navigationdrawer import NavigationDrawer
from kivy.app import App
from kivy.properties import *
from kivy.uix.image import AsyncImage,Image
from kivy.uix.button import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.bubble import Bubble,BubbleButton
from gui.widgets.custom_effects import RectangularRippleBehavior
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from gui.widgets.circle_menu import ModernMenu
from functools import partial
from data.database import FavItem,DataManager
from data.comic_data import ComicCollection
from data.favorites import add_comic_fav, add_collection
import os.path

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
    toolbar = ObjectProperty()
    def __init__(self, **kw):
        super(AppScreenTemplate, self).__init__(**kw)
        self.app = App.get_running_app()

    def on_enter(self, *args):

        super(AppScreenTemplate, self).on_enter(*args)

    def build_nav(self):
        self.toolbar.nav_button = ["md-keyboard-backspace",self.load_last_screen]
        self.toolbar.add_action_button("md-home", lambda *x:self.go_home())
        self.toolbar.add_action_button("md-my-library-books",lambda *x: self.go_comic_screen() )
        self.toolbar.add_action_button("md-settings",lambda *x: self.app.open_settings())
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

    def go_comic_screen(self):
        if self.app.comic_loaded == 'yes':
            self.app.manager.current = 'comic_book_screen'
        else:
            self.app._dialog('No Comic Loaded','Comic Screen Error')


    def callback1(self, *args):
        print("test 1")
        args[0].parent.open_submenu(
            choices=[
                dict(text='action 1', index=1, callback=self.callback2),
                dict(text='action 2', index=2, callback=self.callback2),
                dict(text='action 3', index=3, callback=self.callback2),
            ])

    def callback2(self, *args):
        print("test 2")
        args[0].parent.dismiss()

    def callback3(self, *args):
        print("test 3")
        args[0].parent.dismiss()

    def callback4(self, *args):
        print("test 4")
        args[0].parent.open_submenu(
            choices=[
                dict(text='hey', index=1, callback=self.callback2),
                dict(text='oh', index=2, callback=self.callback2),
            ])

    def callback5(self, *args):
        print("test 5")
        args[0].parent.dismiss()

class CommonComicsScroll(ScrollView):
    pass

class CommonComicsOuterGrid(GridLayout):
    pass

class CommonComicsCoverLabel(Label):
    pass

class CommonComicsCoverInnerGrid(GridLayout):
    pass

class CommonComicsCoverImage(RectangularRippleBehavior,ButtonBehavior,AsyncImage):
    comic = ObjectProperty()
    comics_collection = ObjectProperty()
    menu_args = DictProperty({})
    menu_cls = ObjectProperty(ModernMenu)
    comic_bubble_menu = ObjectProperty()
    clock_set = StringProperty()
    use_bubble_menu = ObjectProperty()
    def save_cover(self,dt):
        print 'save fired'
        cover_file = 'data/img/%s.png'%str(self.comic.comic_id_number)
        self.export_to_png(cover_file)

    def _proxy_loaded(self,proxyImage):
        if proxyImage.image.texture:
            print 'if proxyImage.image.texture:'
            self.texture = proxyImage.image.texture
            Clock.schedule_once(self.save_cover, 2)

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            if self.use_bubble_menu == False:
                pass
            else:
                self.create_clock(touch)
                if touch.is_double_tap:
                    self.delete_clock(touch)
                    self.open_collection()
        return super(CommonComicsCoverImage, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.use_bubble_menu == False:
            pass
        else:
            if self.collide_point(*touch.pos):
                self.delete_clock(touch)
                self.clock_set = 'no'
        return super(CommonComicsCoverImage, self).on_touch_up(touch)

    def show_bubble(self, touch, dt):
        if dt:self.clock_set = 'no'
        if not self.comic_bubble_menu:
            self.comic_bubble_menu = comic_bubble_menu = CommonComicsBubbleMenu(pos=self.pos)
            self.add_widget(comic_bubble_menu)

    def create_clock(self,touch):
        callback = partial(self.show_bubble, touch)
        Clock.schedule_once(callback, 1)
        self.clock_set = 'yes'
        touch.ud['event'] = callback

    def delete_clock(self,touch):
        if self.clock_set == 'yes':
            Clock.unschedule(touch.ud['event'])
            self.clock_set = 'no'

    def enable_me(self,instance):
        Logger.debug('enabling %s'%self.id)
        self.disabled = False

    def add_fav(self,*args):
       add_comic_fav(self.comic)

    def open_comic(self,*args):
        self.disabled = True
        app = App.get_running_app()
        app.root.current = 'comic_book_screen'
        new_comics_collection = ComicCollection()
        new_comics_collection.add_comic(self.comic)
        comic_screen = app.root.get_screen('comic_book_screen')
        comic_screen.load_comic_book(self.comic,new_comics_collection)
        Clock.schedule_once(self.enable_me, .5)

    def open_collection(self,*args):
        self.disabled = True
        app = App.get_running_app()
        app.root.current = 'comic_book_screen'
        comic_screen = app.root.get_screen('comic_book_screen')
        comic_screen.use_pagination = False
        comic_screen.last_load = 0
        comic_screen.load_comic_book(self.comic,self.comics_collection)
        Clock.schedule_once(self.enable_me, .5)
    def open_next_section(self, *args):
        self.disabled = True
        app = App.get_running_app()
        app.root.current = 'comic_book_screen'
        comic_screen = app.root.get_screen('comic_book_screen')
        comic_screen.load_comic_book(self.comic,self.comics_collection)
        Clock.schedule_once(self.enable_me, .5)

    def open_prev_section(self, *args):
        self.disabled = True
        app = App.get_running_app()
        app.root.current = 'comic_book_screen'
        comic_screen = app.root.get_screen('comic_book_screen')
        comic_screen.last_load = comic_screen.last_section
        comic_screen.load_comic_book(self.comic,self.comics_collection)
        Clock.schedule_once(self.enable_me, .5)


class CommonComicsBubbleMenu(ThemeBehaviour,Bubble):
    def __init__(self, **kwargs):
        super(CommonComicsBubbleMenu, self).__init__(**kwargs)
        self.background_normal= ''
        self.background_down = ''
        self.background_color = self._theme_cls.primary_color
        self.background_color_down = self._theme_cls.primary_dark

    def add_fav(self):
        x = self.parent
        self.parent.comic_bubble_menu = ''
        self.parent.remove_widget(self)
        x.add_fav()

    def open_collection(self,*args):
        self.parent.open_collection()
        self.parent.comic_bubble_menu = ''
        self.parent.remove_widget(self)

    def open_comic(self,*args):
        self.parent.open_comic()
        self.parent.comic_bubble_menu = ''
        self.parent.remove_widget(self)

    def close_me(self,*args):
        self.parent.comic_bubble_menu = ''
        self.parent.remove_widget(self)

class CommonComicsBubbleButton(ThemeBehaviour,ToggleButton):
    def __init__(self, **kwargs):
        super(CommonComicsBubbleButton, self).__init__(**kwargs)
        self.background_normal= ''
        self.background_down = ''
        self.background_color = self._theme_cls.primary_color
        self.background_color_down = self._theme_cls.primary_dark
        self.background_color_disabled = self._theme_cls.primary_dark


class CommonCollectionsBubbleMenu(ThemeBehaviour,Bubble):
    def __init__(self, **kwargs):
        super(CommonCollectionsBubbleMenu, self).__init__(**kwargs)
        self.background_normal= ''
        self.background_down = ''
        self.background_color = self._theme_cls.primary_color
        self.background_color_down = self._theme_cls.primary_dark

    def open_collection(self,*args):
        self.parent.load_collection()
        self.parent.collection_bubble_menu = ''
        self.parent.remove_widget(self)

    def view_items(self,*args):
        x = self.parent
        x.collection_bubble_menu = ''
        x.remove_widget(self)
        x.view_items(self)

    def close_me(self,*args):
        self.parent.collection_bubble_menu = ''
        self.parent.remove_widget(self)



class CollctionAddPopUp(Popup):
    collection = ObjectProperty()
    use_collection = StringProperty()
    def __init__(self, **kwargs):
        super(CollctionAddPopUp, self).__init__(**kwargs)

    def submit_fav(self):

        if self.textfield_name.text:
            if self.use_collection=='True':
                self.collection.name = self.textfield_name.text
                new_collection = self.collection
            else:
                new_collection = ComicCollection(name=self.textfield_name.text)

            x_sort_by = self.collection_sort.text
            new_id = add_collection(new_collection, sort_by=x_sort_by, add_with_items=self.use_collection)
            if self.use_collection =='False':
                app = App.get_running_app()
                favorites_screen = app.root.get_screen('favorites_screen')
                favorites_screen.build_favorites_screen(new_id)
            self.dismiss()

        else:
            self.err_lbl.text = 'You Must Enter a Name'

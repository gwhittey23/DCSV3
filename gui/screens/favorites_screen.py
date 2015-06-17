# -*- coding: utf-8 -*-
import kivy
from kivy.uix.togglebutton import ToggleButton
from gui.theme_engine.theme import ThemeBehaviour

from gui.widgets.custom_widgets import AppScreenTemplate,AppNavDrawer
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from functools import partial
from kivy.properties import StringProperty,ListProperty,ObjectProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage,Image
from kivy.clock import Clock
from kivy.uix.bubble import Bubble,BubbleButton
from gui.widgets.custom_effects import RectangularRippleBehavior
from utils import  iterfy
import gc
from data.database import FavItem,FavCollection,FavFolder,DataManager
from data.favorites import add_comic_fav,add_collection,get_fav_collection,get_loose_fav
import pickle



class FavoritesScreen(AppScreenTemplate):
    fav_folder_list = ListProperty([])

    def on_pre_enter(self, *args):
        super(FavoritesScreen, self).on_pre_enter(*args)
        self.build_favorites_screen()
    def on_enter(self, *args):
        pass
        # Clock.schedule_interval(self.update, 1.0/60)
    def go_comic_screen(self):
        if self.app.comic_loaded == 'yes':
            self.app.manager.current = 'comic_book_screen'
        else:
            self.app._dialog('No Comic Loaded','Comic Screen Error')
    def update(self,dt):
        pass
        # fav_folder = self.fav_folder
        # fav_item =  self.fav_item
        # if fav_item.collide_widget(fav_folder):
        #     print 'collide'
        #     # Clock.schedule_once(self.move_fave_item,.25)


    def move_fav_item(self, dt):

        self.mainbox.remove_widget(self.fav_item)
        Clock.unschedule(self.update)

    def build_favorites_screen(self):
        fav_collection_list = get_fav_collection()
        for s in iterfy(fav_collection_list):
            fav_item_list = s.fav_items


        fav_loose = get_loose_fav()
        for fav  in iterfy(fav_loose):
            print 'fav_item::%s'%fav.name
        f = open('comic_collection.pickle2', 'r')
        self.collection = pickle.load(f)
        f.close()
        scroll = self.scroll
        scroll.clear_widgets()
        gc.collect()
        fav_folder_list = ()
        grid2 = GridLayout(cols=6, size_hint=(1,.5),spacing=(20,20),padding=10, pos_hint = {'x':.01,'y':.4},id='cover_outgrid')

        for s in iterfy(fav_collection_list):
            fav_folder = FavoritesCollection(id='%s'%s.id,_text='%s'%s.name)
            grid2.add_widget(fav_folder)
            self.fav_folder_list.append(fav_folder)
        self.main.add_widget(grid2)
        grid = GridLayout(cols=6, size_hint=(None,None),spacing=(20,20),padding=10, id='cover_outgrid')
        grid.bind(minimum_height=grid.setter('height'))
        base_url = self.app.config.get('Server', 'url')
        for comic in self.collection.do_sort_issue:
            comic_name = '%s #%s'%(comic.series,comic.issue)
            src_thumb = src_thumb = comic.get_cover()
            inner_grid = FavroitesInnerGrid(id='inner_grid'+str(comic.comic_id_number))
            comic_thumb = FavroitesCoverImage(source=src_thumb,id=str(comic.comic_id_number),nocache=True)
            inner_grid.fav_folder_list = self.fav_folder_list

            comic_thumb.comic = comic
            comic_thumb.comics_collection = self.collection
            inner_grid.add_widget(comic_thumb)
            # comic_thumb.bind(on_release=comic_thumb.click)
            smbutton = FavroitesLabel(text=comic_name)
            inner_grid.add_widget(smbutton)
            grid.add_widget(inner_grid)

        scroll.add_widget(grid)



class FavoritesScreenNavigationDrawer(AppNavDrawer):
    pass
#
# class FavoritesFolder(Widget):
#     pass

class FavroitesLabel(Label):
    pass

class FavroitesInnerGrid(DragBehavior,GridLayout):
    fav_folder_list = ListProperty([])
    # def on_touch_down( self, touch ):
    #     if self.collide_point( *touch.pos ):
    #         touch.grab( self )
    #         return True
    #
    # def on_touch_up( self, touch ):
    #     if touch.grab_current is self:
    #         touch.ungrab( self )
    #         Clock.unschedule(self.update)
    #         return True
    # def update(self,dt):
    #     for folder in self.fav_folder_list:
    #
    #             if self.collide_widget(folder):
    #                 print 'colldie with %s '%folder.id
    # def on_touch_move( self, touch ):
    #     if touch.grab_current is self:
    #         self.pos = touch.x-self.width/2, touch.y-self.height/2
    #         Clock.schedule_interval(self.update, 0.25)


class FavroitesCoverImage(RectangularRippleBehavior,Image):
    comic_bubble_menu = ObjectProperty()
    clock_set = StringProperty()
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.create_clock(touch)
            if touch.is_double_tap:
                self.delete_clock(touch)
                self.open_collection()
        return super(FavroitesCoverImage, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.delete_clock(touch)
            self.clock_set = 'no'
        return super(FavroitesCoverImage, self).on_touch_up(touch)

    def show_bubble(self, touch, dt):
        if dt:self.clock_set = 'no'
        if not self.comic_bubble_menu:
            self.comic_bubble_menu = comic_bubble_menu = FavoritesBubbleMenu(pos=self.pos)
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

class FavoritesTrash(Widget):
    pass


class FavoritesFolder(Widget):
    def on_touch_down( self, touch ):
        if self.collide_point( *touch.pos ):
            touch.grab( self )
            return True

    def on_touch_up( self, touch ):
        if touch.grab_current is self:
            touch.ungrab( self )
            # Clock.unschedule(self.update)
            return True
    def update(self,dt):
        for folder in self.fav_folder_list:

            if self.collide_widget(folder):
                print 'colldie with %s '%folder.id
    def on_touch_move( self, touch ):
        if touch.grab_current is self:
            self.pos = touch.x-self.width/2, touch.y-self.height/2
            # Clock.schedule_interval(self.update, 0.25)
class FavoritesBubbleMenu(ThemeBehaviour,Bubble):
    def __init__(self, **kwargs):
        super(FavoritesBubbleMenu, self).__init__(**kwargs)
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

class FavoritesBubbleButton(ThemeBehaviour,ToggleButton):
    def __init__(self, **kwargs):
        super(FavoritesBubbleButton, self).__init__(**kwargs)
        self.background_normal= ''
        self.background_down = ''
        self.background_color = self._theme_cls.primary_color
        self.background_color_down = self._theme_cls.primary_dark
        self.background_color_disabled = self._theme_cls.primary_dark

class FavoritesCollection(Widget):
    _text = StringProperty()
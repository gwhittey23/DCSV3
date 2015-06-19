# -*- coding: utf-8 -*-
import kivy
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from gui.theme_engine.theme import ThemeBehaviour

from gui.widgets.custom_widgets import AppScreenTemplate,AppNavDrawer,CommonCollectionsBubbleMenu
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from functools import partial
from kivy.properties import StringProperty,ListProperty,ObjectProperty,NumericProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage,Image
from kivy.clock import Clock
from kivy.uix.bubble import Bubble,BubbleButton
from gui.widgets.custom_effects import RectangularRippleBehavior
from kivy.logger import Logger
from utils import  iterfy
import gc
import os
from data.database import FavItem,FavCollection,FavFolder,DataManager
from data.favorites import add_comic_fav,add_collection,get_fav_collection,get_loose_fav, get_single_colelction, \
    delete_collection, rename_collection
from kivy.uix.popup import Popup
from kivy.app import App



class FavoritesScreen(AppScreenTemplate):
    fav_folder_list = ListProperty([])
    current_collection = ObjectProperty()
    edit_mode = StringProperty()

    def on_pre_enter(self, *args):
        super(FavoritesScreen, self).on_pre_enter(*args)
        self.build_favorites_screen()
        self.edit_mode = 'Off'

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

    def build_favorites_screen(self,collection_id=None):
        self.edit_switch.bind(active=self.set_edit_mode)
        fav_collection_list = get_fav_collection()
        for s in iterfy(fav_collection_list):
            fav_item_list = s.fav_items
        dm = DataManager()
        dm.create()
        session = dm.Session()
        if collection_id is None:
            collection_name = 'Unsorted Comics'
            query = session.query(FavCollection).filter_by(name=collection_name).one()
            current_collection = query
            self.current_collection = current_collection
        else:
            query = session.query(FavCollection).filter_by(id=collection_id).one()
            current_collection = query
            self.current_collection = current_collection
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

        for fav_item in iterfy(current_collection.fav_items):
            comic_name = (fav_item.name)
            comic_number = fav_item.comic_id_number
            inner_grid = FavroitesInnerGrid(id='inner_grid'+str(comic_number))
            data_folder = self.app.config.get('Server', 'storagedir')
            cover_file = '%s/%s.png'%(data_folder,str(fav_item.comic_id_number))
            try:
                if os.path.isfile(cover_file):
                   src_thumb =  str(cover_file)
            except:
                Logger.critical('Something bad happened in loading cover')
            comic_thumb = FavroitesCoverImage(source=src_thumb,id=str(fav_item.comic_id_number),nocache=True)
            inner_grid.fav_folder_list = self.fav_folder_list
            inner_grid.add_widget(comic_thumb)
            # comic_thumb.bind(on_release=comic_thumb.click)
            smbutton = FavroitesLabel(text=comic_name)
            inner_grid.add_widget(smbutton)
            grid.add_widget(inner_grid)

        scroll.add_widget(grid)
    def set_edit_mode(self,instance, value,*args):
        if value:
            self.edit_mode = 'On'
        else:
            self.edit_mode = 'Off'
class FavoritesScreenNavigationDrawer(AppNavDrawer):
    pass

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
    item_bubble_menu = ObjectProperty()
    clock_set = StringProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.create_clock(touch)
            if touch.is_double_tap:
                self.delete_clock(touch)

        return super(FavroitesCoverImage, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.delete_clock(touch)
            self.clock_set = 'no'
        return super(FavroitesCoverImage, self).on_touch_up(touch)

    def show_bubble(self, touch, dt):
        if dt:self.clock_set = 'no'
        if not self.item_bubble_menu:
            self.item_bubble_menu = item_bubble_menu = FavItemBubbleMenu(pos=self.pos)
            self.add_widget(item_bubble_menu)

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

class FavItemBubbleMenu(ThemeBehaviour,Bubble):
    def __init__(self, **kwargs):
        super(FavItemBubbleMenu, self).__init__(**kwargs)
        self.background_normal= ''
        self.background_down = ''
        self.background_color = self._theme_cls.primary_color
        self.background_color_down = self._theme_cls.primary_dark

    def copy_item(self):
        fav_collection_list = get_fav_collection()
        parent = self.parent
        grid2 = GridLayout(cols=6, size_hint=(1,.5),spacing=(20,20),padding=10, pos_hint = {'x':.01,'y':.4},id='cover_outgrid')
        for s in iterfy(fav_collection_list):
            fav_folder = FavoritesCollection(id='%s'%s.id,_text='%s'%s.name)
            grid2.add_widget(fav_folder)

        parent.copy_move_item_pop = CopyMoveItemPopup(content = grid2 , fav_item=parent)
        parent.copy_move_item_pop.open()
        parent.comic_bubble_menu = ''
        parent.remove_widget(self)

    def move_item(self,*args):
        self.parent.open_collection()
        self.parent.comic_bubble_menu = ''
        self.parent.remove_widget(self)

    def delete_item(self,*args):
        self.parent.open_comic()
        self.parent.comic_bubble_menu = ''
        self.parent.remove_widget(self)

    def close_me(self,*args):
        self.parent.comic_bubble_menu = ''
        self.parent.remove_widget(self)

class CopyMoveItemPopup(Popup):
    fav_item = ObjectProperty()

    def __init__(self,fav_item, **kwargs):
        self.fav_item = fav_item
        super(CopyMoveItemPopup, self).__init__(**kwargs)

    def copy_item(self):
        pass

    def move_item(self):
        pass

class FavoritesCollection(ThemeBehaviour,RectangularRippleBehavior,Button):
    _text = StringProperty()
    collection_bubble_menu = ObjectProperty()
    clock_set = StringProperty()
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.create_clock(touch)
            if touch.is_double_tap:
                self.delete_clock(touch)
                self.load_collection()
        return super(FavoritesCollection, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.delete_clock(touch)
            self.clock_set = 'no'
        return super(FavoritesCollection, self).on_touch_up(touch)

    def show_bubble(self, touch, dt):
        if dt:self.clock_set = 'no'
        if not self.collection_bubble_menu:
            app = App.get_running_app()
            favorites_screen = app.root.get_screen('favorites_screen')
            if favorites_screen.edit_mode == "On":
                self.collection_bubble_menu = collection_bubble_menu = FavCollectionBubleMenu(pos=self.pos)
            else:
                self.collection_bubble_menu = collection_bubble_menu =CommonCollectionsBubbleMenu(pos=self.pos)
            self.add_widget(collection_bubble_menu)

    def create_clock(self,touch):
        callback = partial(self.show_bubble, touch)
        Clock.schedule_once(callback, 1)
        self.clock_set = 'yes'
        touch.ud['event'] = callback

    def delete_clock(self,touch):
        if self.clock_set == 'yes':
            Clock.unschedule(touch.ud['event'])
            self.clock_set = 'no'

    def delete_collection(self, *args):
        app = App.get_running_app()
        favorites_screen = app.root.get_screen('favorites_screen')
        if str(favorites_screen.current_collection.id) == str(self.id):
            Clock.schedule_once(favorites_screen.build_favorites_screen, .25)
        x = self.parent
        x.remove_widget(self)
        delete_collection(collection_id=self.id)

    def rename_collection(self,*args):
        self.collection_pop = CollctionRenamePopUp(collection_id=self.id,fav_collection_widget=self,_text=self._text)

        self.collection_pop.open()


    def load_collection(self,*args):
        app = App.get_running_app()
        favorites_screen = app.manager.get_screen('favorites_screen')
        if favorites_screen.edit_mode == "On":
           favorites_screen.build_favorites_screen(collection_id=self.id)
        else:
            comic_collection_screen = app.manager.get_screen('comic_collection_screen')
            comic_collection_type = 'favorite_collection'
            app.manager.current = 'comic_collection_screen'
            comic_collection_screen.get_collection_data(comic_collection_type,self.id)

class FavCollectionBubleMenu(ThemeBehaviour,Bubble):
    def __init__(self, **kwargs):
        super(FavCollectionBubleMenu, self).__init__(**kwargs)
        self.background_normal= ''
        self.background_down = ''
        self.background_color = self._theme_cls.primary_color
        self.background_color_down = self._theme_cls.primary_dark
    def delete_collection(self):
        x = self.parent
        x.collection_bubble_menu = ''
        x.remove_widget(self)
        x.delete_collection(self)

    def rename_collection(self,*args):
        x = self.parent
        x.collection_bubble_menu = ''
        x.remove_widget(self)
        x.rename_collection(self)

    def close_me(self,*args):
        self.parent.collection_bubble_menu = ''
        self.parent.remove_widget(self)

class FavoritesBubbleButton(ThemeBehaviour,ToggleButton):
    def __init__(self, **kwargs):
        super(FavoritesBubbleButton, self).__init__(**kwargs)
        self.background_normal= ''
        self.background_down = ''
        self.background_color = self._theme_cls.primary_color
        self.background_color_down = self._theme_cls.primary_dark
        self.background_color_disabled = self._theme_cls.primary_dark

class CollctionRenamePopUp(Popup):
    collection_id = NumericProperty()
    fav_collection_widget = ObjectProperty()
    _text = StringProperty()
    def __init__(self,collection_id,fav_collection_widget, **kwargs):
        self.collection_id = int(collection_id)
        self.fav_collection_widget = fav_collection_widget

        super(CollctionRenamePopUp, self).__init__(**kwargs)

    def rename_collection(self):
        if self.textfield_name.text:
            new_name = self.textfield_name.text
            rename_collection(self.collection_id,new_name=new_name)
            x = self.fav_collection_widget
            x._text = new_name
            # x.ids.fav_col_lbl.text = new_name
            self.dismiss()
        else:
            self.err_lbl.text = 'You Must Enter a Name'

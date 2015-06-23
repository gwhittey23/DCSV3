# -*- coding: utf-8 -*-
from functools import partial
import gc
import os

from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty,ListProperty,ObjectProperty,NumericProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.bubble import Bubble
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.metrics import dp
from gui.theme_engine.theme import ThemeBehaviour
from gui.widgets.custom_widgets import AppScreenTemplate,AppNavDrawer,CommonCollectionsBubbleMenu,CommonComicsBubbleMenu,\
    CollctionAddPopUp
from gui.widgets.custom_effects import RectangularRippleBehavior
from gui.theme_engine.material_resources import get_icon_char
from tools.utils import  iterfy
from data.comic_data import ComicCollection, ComicBook
from data.database import FavItem, FavCollection, DataManager
from data.favorites import get_fav_collection, delete_collection, rename_collection, copy_fav_item, move_fav_item


class FavoritesScreen(AppScreenTemplate):
    fav_folder_list = ListProperty([])
    current_collection = ObjectProperty()
    edit_mode = StringProperty()
    fav_collection_id = NumericProperty()
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

    def build_favorites_screen(self,collection_id=1,*args):

        self.edit_switch.bind(active=self.set_edit_mode)
        fav_collection_list = get_fav_collection()
        for s in iterfy(fav_collection_list):
            fav_item_list = s.fav_items
        dm = DataManager()
        dm.create()
        session = dm.Session()

        query = session.query(FavCollection).filter_by(id=collection_id).one()

        current_collection = query
        sort_by = current_collection.sort_by
        new_collection = ComicCollection(name=query.name)
        for fav_item in iterfy(current_collection.fav_items):
            comic_json = fav_item.comic_json
            new_comic = ComicBook(comic_json)
            new_collection.add_comic(new_comic)
        comic_collection_sorted = new_collection.do_sort(sort_by)

        self.current_collection = new_collection
        self.fav_collection_id = current_collection.id
        self.current_collection_label.text = self.current_collection.name
        scroll = self.scroll
        scroll.clear_widgets()
        gc.collect()
        fav_folder_list = ()
        grid2 = GridLayout(cols=6, size_hint=(1,.5),spacing=(20,20),padding=10, pos_hint = {'x':.01,'y':.4},id='cover_outgrid')
        for s in iterfy(fav_collection_list):
            fav_folder = FavoritesCollection(id='%s'%s.id,_text='%s'%s.name,sort_by=s.sort_by)
            grid2.add_widget(fav_folder)
            self.fav_folder_list.append(fav_folder)
        self.main.add_widget(grid2)
        grid = GridLayout(cols=6, size_hint=(None,None),spacing=(20,20),padding=10, id='cover_outgrid')
        grid.bind(minimum_height=grid.setter('height'))
        base_url = self.app.config.get('Server', 'url')

        for comic in iterfy(comic_collection_sorted):
            comic_name = '%s #%s'%(comic.series,comic.issue)
            comic_number = comic.comic_id_number
            inner_grid = FavroitesInnerGrid(id='inner_grid'+str(comic_number))
            data_folder = self.app.config.get('Server', 'storagedir')
            cover_file = '%s/%s.png'%(data_folder,str(comic.comic_id_number))
            try:
                if os.path.isfile(cover_file):
                   src_thumb =  str(cover_file)
            except:
                Logger.critical('Something bad happened in loading cover')
            comic_thumb = FavroitesCoverImage(source=src_thumb,id=str(comic_number),nocache=True)
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

    def open_collection_reader(self, favorite_collection_id,*args):
        dm = DataManager()
        dm.create()
        session = dm.Session()
        if favorite_collection_id is None:
            query = session.query(FavCollection).get(1)
            favorite_collection = query
        else:
            query = session.query(FavCollection).get(favorite_collection_id)
            favorite_collection = query
        new_collection = ComicCollection()
        sort_by =  favorite_collection.sort_by
        for fav_item in iterfy(favorite_collection.fav_items):
            comic_json = fav_item.comic_json
            new_comic = ComicBook(comic_json)
            new_collection.add_comic(new_comic)
        app = App.get_running_app()
        app.root.current = 'comic_book_screen'
        comic_screen = app.root.get_screen('comic_book_screen')
        comic_screen.use_pagination = False
        comic_screen.last_load = 0
        if sort_by == 'Issue':
            comic_collection_sorted = new_collection.do_sort_issue
        elif sort_by == 'Pub Date':
            comic_collection_sorted = new_collection.do_sort_pub_date
        else:
            comic_collection_sorted = new_collection.comics
        comic_screen.load_comic_book(comic_collection_sorted[0],new_collection,sort_by=sort_by)

    def add_collection(self):
        self.collection_pop = CollctionAddPopUp(use_collection='False')
        self.collection_pop.hint_text = 'Enter a name you want this Collection to have'
        self.collection_pop.open()

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
    comic_bubble_menu = ObjectProperty()
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
        if not self.comic_bubble_menu:
            app = App.get_running_app()
            favorites_screen = app.root.get_screen('favorites_screen')
            if favorites_screen.edit_mode == "On":
                self.comic_bubble_menu = comic_bubble_menu = FavItemBubbleMenu(pos=self.pos)
            else:
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

    def get_comic_json(self,*args):
        dm = DataManager()
        dm.create()
        session = dm.Session()
        query = session.query(FavItem).get(self.id)
        return query.comic_json

    def open_comic(self,*args):
        self.disabled = True
        app = App.get_running_app()
        app.root.current = 'comic_book_screen'
        new_comics_collection = ComicCollection()
        new_comic = ComicBook(self.get_comic_json())
        new_comics_collection.add_comic(new_comic)
        comic_screen = app.root.get_screen('comic_book_screen')
        comic_screen.load_comic_book(new_comic,new_comics_collection)
        Clock.schedule_once(self.enable_me, .5)

    def open_collection(self,*args):
        app = App.get_running_app()
        favorites_screen = app.manager.get_screen('favorites_screen')
        favorites_screen.open_collection_reader(favorites_screen.current_collection.id,collection_sort='Pub Data')
        Clock.schedule_once(self.enable_me, .5)

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
        fav_collection = get_fav_collection()
        fav_collection_list = []
        for item in fav_collection:
            print item.name
            fav_collection_list.append(item.name)
        parent = self.parent
        print fav_collection_list
        parent.copy_move_item_pop = CopyMoveItemPopup(fav_item=parent)
        parent.copy_move_item_pop.copy_spinner.values = fav_collection_list
        parent.copy_move_item_pop.copy_spinner.text = fav_collection_list[0]
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

    def copy_fav(self):
        # spinner_text = self.copy_spinner.text
        # dm = DataManager()
        # dm.create()
        # session = dm.Session()
        # fav_collection = session.query(FavCollection).filter_by(name=spinner_text).first()
        # x_item = session.query(FavItem).get(self.fav_item.id)
        # x_item.fav_collection.append(fav_collection)
        # session.commit()
        spinner_text = self.copy_spinner.text
        fav_item = self.fav_item
        copy_fav_item(fav_item, spinner_text)
        self.dismiss()
    def move_fav(self):
        target_name = self.copy_spinner.text
        fav_item = self.fav_item
        app = App.get_running_app()
        favorites_screen = app.root.get_screen('favorites_screen')
        current_collection = favorites_screen.current_collection.name
        current_collection_id = move_fav_item(fav_item,current_collection,target_name)
        favorites_screen.build_favorites_screen(current_collection_id)
        self.dismiss()

class FavoritesCollection(ThemeBehaviour,RectangularRippleBehavior,Button):
    _text = StringProperty()
    collection_bubble_menu = ObjectProperty()
    clock_set = StringProperty()
    sort_by = StringProperty()
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
        fav_collection_id = favorites_screen.fav_collection_id
        if str(favorites_screen.fav_collection_id) == str(self.id):
            Clock.schedule_once(favorites_screen.build_favorites_screen, .25)
        else:
            Clock.schedule_once(partial(favorites_screen.build_favorites_screen, fav_collection_id), .25)
        x = self.parent
        x.remove_widget(self)
        delete_collection(collection_id=self.id)

    def rename_collection(self,*args):
        self.collection_pop = CollctionRenamePopUp(collection_id=self.id,fav_collection_widget=self,
                                                   _text=self._text)
        self.collection_pop.collection_sort.text=self.sort_by

        self.collection_pop.open()

    def view_items(self,*args):
        app = App.get_running_app()
        favorites_screen = app.manager.get_screen('favorites_screen')
        favorites_screen.build_favorites_screen(collection_id=self.id)

    def load_collection(self,*args):
        app = App.get_running_app()
        favorites_screen = app.manager.get_screen('favorites_screen')
        if favorites_screen.edit_mode == "On":
           favorites_screen.build_favorites_screen(collection_id=self.id)
        else:
            favorites_screen.open_collection_reader(self.id)

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
            sort_by = self.collection_sort.text
            rename_collection(self.collection_id,new_name=new_name,sort_by=sort_by)
            x = self.fav_collection_widget
            x._text = new_name
            # x.ids.fav_col_lbl.text = new_name
            self.dismiss()
        else:
            self.err_lbl.text = 'You Must Enter a Name'

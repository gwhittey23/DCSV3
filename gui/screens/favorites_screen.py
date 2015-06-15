# -*- coding: utf-8 -*-
import kivy
from gui.widgets.custom_widgets import AppScreenTemplate,AppNavDrawer
from kivy.uix.widget import Widget
from gui.widgets.custom_widgets import CommonComicsCoverInnerGrid,\
    CommonComicsOuterGrid,CommonComicsCoverLabel,CommonComicsCoverImage,CommonComicsScroll
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.lang import Factory
from kivy.uix.scatterlayout import ScatterLayout,Scatter
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import StringProperty,ListProperty,ObjectProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage,Image
from kivy.clock import Clock
import pickle
class FavoritesScreen(AppScreenTemplate):
    fav_folder_list = ListProperty([])

    def on_pre_enter(self, *args):
        super(FavoritesScreen, self).on_pre_enter(*args)
        self.build_nav()
    def on_enter(self, *args):
        pass
        # Clock.schedule_interval(self.update, 1.0/60)
    def go_comic_screen(self):
        if self.app.comic_loaded == 'yes':
            self.app.manager.current = 'comic_book_screen'
        else:
            self.app.dialog_error('No Comic Loaded','Comic Screen Error')
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
        f = open('comic_collection.pickle', 'r')
        self.collection = pickle.load(f)
        f.close()

        fav_folder_list = ()
        grid2 = GridLayout(cols=6, size_hint=(1,.5),spacing=(20,20),padding=10, pos_hint = {'x':.01,'y':.4},id='cover_outgrid')

        for i in range(1,15):
            fav_folder = FavoritesFolder(id='fav_fodler_%s'%str(i))
            grid2.add_widget(fav_folder)
            self.fav_folder_list.append(fav_folder)
        self.add_widget(grid2)
        grid = GridLayout(cols=6, size_hint=(1,.5),spacing=(20,20),padding=10, pos_hint = {'x':.01,'y':.01},id='cover_outgrid')
        fav_trash=FavoritesTrash()
        grid.add_widget(fav_trash)
        # grid.bind(minimum_height=grid.setter('height'))
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

        self.add_widget(grid)



class FavoritesScreenNavigationDrawer(AppNavDrawer):
    pass
#
# class FavoritesFolder(Widget):
#     pass

class FavroitesLabel(Label):
    pass

class FavroitesInnerGrid(DragBehavior,GridLayout):
    fav_folder_list = ListProperty([])
    def on_touch_down( self, touch ):
        if self.collide_point( *touch.pos ):
            touch.grab( self )
            return True

    def on_touch_up( self, touch ):
        if touch.grab_current is self:
            touch.ungrab( self )
            Clock.unschedule(self.update)
            return True
    def update(self,dt):
        for folder in self.fav_folder_list:

                if self.collide_widget(folder):
                    print 'colldie with %s '%folder.id
    def on_touch_move( self, touch ):
        if touch.grab_current is self:
            self.pos = touch.x-self.width/2, touch.y-self.height/2
            Clock.schedule_interval(self.update, 0.25)



class FavroitesCoverImage(DragBehavior,Image):
    pass

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

DEFAULT_THEME = 'atlas://data/images/defaulttheme/'
FILE_ICON = DEFAULT_THEME + 'filechooser_file'
FOLDER_ICON = DEFAULT_THEME + 'filechooser_folder'

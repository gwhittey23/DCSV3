import gc
from functools import partial
import json

from kivy.logger import Logger
from kivy.properties import ObjectProperty,StringProperty
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import Screen
from kivy.uix.scatterlayout import ScatterLayout
from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.button import ButtonBehavior
from kivy.metrics import dp
from kivy.loader import Loader
from kivy.core.window import Window
from kivy.graphics.transformation import Matrix

from gui.widgets.custom_widgets import  CommonComicsCoverInnerGrid,\
    CommonComicsOuterGrid,CommonComicsCoverLabel,CommonComicsCoverImage,CommonComicsScroll
from gui.widgets.custom_effects import RectangularRippleBehavior
from gui.theme_engine.dialog import Dialog
from settings.settingsjson import settings_json_screen_tap_control


class ComicBookScreen(Screen):
    scroller = ObjectProperty()
    top_pop = ObjectProperty()
    def __init__(self, **kwargs):
        self.just_loaded = False
        self.app = App.get_running_app()
        super(ComicBookScreen, self).__init__(**kwargs)

    def on_leave(self):
        app = App.get_running_app()
        app.manager.last_screen = self

    def load_comic_book(self,comic_obj,comics_collection = ''):
        if self.just_loaded:
            return

        self.just_loaded = True
        self.app.comic_loaded = 'yes'
        Clock.schedule_once(self.set_just_loaded, 4)
        config_app = App.get_running_app()
        data = json.loads(settings_json_screen_tap_control)

        for setting in data:
            if setting['type'] == 'options':

                tap_config = config_app.config.get(setting[u'section'], setting[u'key'])
                if tap_config == 'Disabled':
                      self.ids[setting[u'key']].disabled = True

        Loader.pool.tasks.queue.clear()
        self.comics_collection = comics_collection
        self.comic_obj = comic_obj
        comic_book_carousel = self.ids.comic_book_carousel
        comic_book_carousel.clear_widgets()
        if self.scroller:self.scroller.clear_widgets()
        if self.top_pop:self.top_pop.clear_widgets()

        gc.collect()
        number_pages = comic_obj.page_count
        base_url = App.get_running_app().config.get('Server', 'url')
        api_key = App.get_running_app().config.get('Server', 'api_key')
        strech_image = App.get_running_app().config.get('Display', 'stretch_image')
        if strech_image == '1':
            s_allow_stretch=True
            s_keep_ratio=False
        else:
            s_allow_stretch=False
            s_keep_ratio=True


        max_height = App.get_running_app().config.get('Server', 'max_height')
        scroll = ScrollView( size_hint=(1,1), do_scroll_x=True, do_scroll_y=False,id='page_thumb_scroll')
        self.page_nav_popup = Popup(id='page_nav_popup',title='Pages', content=scroll, pos_hint ={'y': .0001},size_hint = (1,.3))

        self.scroller = scroll
        outer_grid = GridLayout(rows=1, size_hint=(None,None),spacing=5,padding_horizontal=5,id='outtergrd')
        outer_grid.bind(minimum_width=outer_grid.setter('width'))
        for i in range(0, number_pages):
            comic_page_scatter = ComicBookPageScatter(id='comic_scatter'+str(i))
            src_full = "%s/comic/%d/page/%d?api_key=%s&max_height=%d#.jpg" % (base_url, comic_obj.comic_id_number, i,
                                                                              api_key, int(max_height))
            comic_page_image = ComicBookPageImage(source=src_full,id='pi_'+str(i),nocache=True,allow_stretch=s_allow_stretch,keep_ratio=s_keep_ratio)
            comic_page_scatter.add_widget(comic_page_image)
            comic_book_carousel.add_widget(comic_page_scatter)
            #Let's make the thumbs for popup
            inner_grid = ThumbPopPageInnerGrid(id='inner_grid'+str(i))
            src_thumb = "%s/comic/%d/page/%d?api_key=%s&max_height=200#.jpg" % (base_url, comic_obj.comic_id_number, i, api_key)
            page_thumb = ThumbPopPageImage(source=src_thumb,id=comic_page_scatter.id,nocache=True)
            inner_grid.add_widget(page_thumb)
            page_thumb.bind(on_release=page_thumb.click)
            smbutton = ThumbPopPagebntlbl(text='P%s'%str(i+1))
            inner_grid.add_widget(smbutton)
            outer_grid.add_widget(inner_grid)
            proxyImage = Loader.image(src_full,nocache=True)
            proxyImage.bind(on_load=partial(comic_page_image._new_image_downloaded, comic_page_scatter,outer_grid,comic_obj.comic_id_number,i))
        scroll.add_widget(outer_grid)

        if len(self.comics_collection.comics)>1:
            self.build_top_nav()
            self.next_comic = self.get_next_comic()
            self.prev_comic = self.get_prev_comic()
            self.build_next_comic_dialog()
            self.build_prev_comic_dialog()
            # self.ids['btn_collection'].disabled = False
        else:
            pass
            # self.ids['btn_collection'].disabled = True

    def get_prev_comic(self):#TODO Fix when 1 comic is loaded there should not be a next and prev comic.
        comics_collection = self.comics_collection.comics
        comic_obj = self.comic_obj
        index = comics_collection.index(comic_obj) # first index where x appears
        if index < len(comics_collection):
            if index == 0:
                prev_comic = comics_collection[index]
            else:
                prev_comic = comics_collection[index-1]
        return prev_comic

    def get_next_comic(self):
        comics_collection = self.comics_collection.comics
        comic_obj = self.comic_obj
        index = comics_collection.index(comic_obj) # first index where x appears

        if index >= len(comics_collection)-1:
            next_comic = comics_collection[index]
        else:
            next_comic = comics_collection[index+1]
        return next_comic

    def load_next_slide(self):
        comic_book_carousel = self.ids.comic_book_carousel
        if comic_book_carousel.index == len(comic_book_carousel.slides)-1:
            self.open_next_dialog()
            return
        else:
            comic_book_carousel.load_next()

    def load_prev_slide(self):
        comic_book_carousel = self.ids.comic_book_carousel
        if comic_book_carousel.index == 0:
            self.open_prev_dialog()
            return
        else:
            comic_book_carousel.load_previous()

    def page_nav_popup_open(self):

        self.page_nav_popup.open()
        comic_book_carousel = self.ids.comic_book_carousel
        current_slide = comic_book_carousel.current_slide
        for child in self.walk():
            if child.id == current_slide.id:
                Logger.debug('child is %s == slide == %s'%(child.id,current_slide.id ))
                current_page =child

        for child in self.page_nav_popup.walk():
            Logger.debug('%s:%s'% (child,child.id))
            if child.id == 'page_thumb_scroll':
                scroller = child
                for grandchild in scroller.walk():
                    Logger.debug('--------%s:%s'% (grandchild,grandchild.id))
                    if grandchild.id == current_page.id:
                        target_thumb = grandchild
                        Logger.debug('target_thumb: %s'%target_thumb)
                        self.scroller.scroll_to(target_thumb,padding=10, animate=True)

    def comicscreen_open_collection_popup(self):
        self.top_pop.open()

    def build_top_nav(self,collection_sort=''):

        scroll = CommonComicsScroll(id='page_thumb_scroll')
        self.top_pop = Popup(id='page_pop',title='Pages', content=scroll, pos_hint ={'y': .724},size_hint = (1,.379))
        grid = CommonComicsOuterGrid(id='outtergrd')
        grid.bind(minimum_width=grid.setter('width'))
        if collection_sort == 'issue':
            comic_collection_sort = self.comics_collection.do_sort_issue
        else:
            comic_collection_sort = self.comics_collection.comics
        for comic in comic_collection_sort:
            comic_name = '%s #%s'%(str(comic.series),str(comic.issue))
            src_thumb = comic.get_cover()
            inner_grid = CommonComicsCoverInnerGrid(id='inner_grid'+str(comic.comic_id_number))
            comic_thumb = CommonComicsCoverImage(source=src_thumb,id=str(comic.comic_id_number))
            comic_thumb.comic = comic
            comic_thumb.comics_collection = self.comics_collection
            inner_grid.add_widget(comic_thumb)
            comic_thumb.bind(on_release=self.top_pop.dismiss)
            comic_thumb.bind(on_release=comic_thumb.open_collection)
            smbutton = CommonComicsCoverLabel(text=comic_name)
            inner_grid.add_widget(smbutton)
            grid.add_widget(inner_grid)
        scroll.add_widget(grid)






    def build_prev_comic_dialog(self):
        base_url = App.get_running_app().config.get('Server', 'url')
        prev_comic = self.prev_comic
        comic_name = '%s #%s'%(str(prev_comic.series),str(prev_comic.issue))
        src_thumb = self.prev_comic.get_cover()
        inner_grid = CommonComicsCoverInnerGrid(id='inner_grid'+str(prev_comic.comic_id_number))
        comic_thumb = CommonComicsCoverImage(source=src_thumb,id=str(prev_comic.comic_id_number),nocache=True)

        comic_thumb.comic = self.prev_comic
        comic_thumb.comics_collection = self.comics_collection
        inner_grid.add_widget(comic_thumb)

        smbutton = CommonComicsCoverLabel(text=comic_name)
        inner_grid.add_widget(smbutton)
        content = inner_grid


        self.prev_dialog = Dialog(title="Load Prev Comic",
                             content=content,
                             size_hint=(.4, .3),
                             height=dp(250),
                             auto_dismiss=True)
        self.prev_dialog.add_action_button("Dismiss", action=lambda *x: self.prev_dialog.dismiss())

        comic_thumb.bind(on_release=self.prev_dialog.dismiss)
        comics_collection = self.comics_collection.comics
        comic_obj = self.comic_obj
        index = comics_collection.index(comic_obj) # first index where x appears
        if index < len(comics_collection):
            if index == 0:
                return
            else:
                comic_thumb.bind(on_release=comic_thumb.open_collection)

    def build_next_comic_dialog(self):
        ''' Make popup showing cover for next comic'''
        base_url = App.get_running_app().config.get('Server', 'url')
        comic = self.next_comic
        Logger.debug('self.next_comic.comic_id_number: %s'%self.next_comic.comic_id_number)
        Logger.debug('comic_id_number: %s'%comic.comic_id_number)
        comics_collection = self.comics_collection.comics
        comic_obj = self.comic_obj
        index = comics_collection.index(comic_obj) # first index where x appears
        comic_name = '%s #%s'%(str(comic.series),str(comic.issue))
        src_thumb = self.next_comic.get_cover()
        inner_grid = CommonComicsCoverInnerGrid(id='inner_grid'+str(comic.comic_id_number))
        comic_thumb = CommonComicsCoverImage(source=src_thumb,id=str(comic.comic_id_number),nocache=True)

        comic_thumb.comic = self.next_comic
        comic_thumb.comics_collection = self.comics_collection
        inner_grid.add_widget(comic_thumb)

        smbutton = CommonComicsCoverLabel(text=comic_name)
        inner_grid.add_widget(smbutton)
        content = inner_grid
        if index >= len(comics_collection)-1:
            dialog_title = 'On Last Comic'
        else:
            dialog_title = 'Load Next Comic'

        self.next_dialog = Dialog(title=dialog_title,
                             content=content,
                             size_hint=(.3, .3),
                             height=dp(250),
                             auto_dismiss=True)
        comic_thumb.bind(on_release=self.next_dialog.dismiss)

        if index >= len(comics_collection)-1:
            return
        else:
            comic_thumb.bind(on_release=comic_thumb.open_collection)

    def open_next_dialog(self):
         self.next_dialog.open()



    def open_prev_dialog(self):
         self.prev_dialog.open()

    def load_next_comic(self):
        if self.next_dialog: self.next_dialog.dismiss()
        comics_collection = self.comics_collection.comics
        comic_obj = self.comic_obj
        index = comics_collection.index(comic_obj) # first index where x appears
        if index >= len(comics_collection)-1:
            return
        else:
            self.load_comic_book(self.next_comic,self.comics_collection)

    def load_prev_comic(self):
        if self.prev_dialog: self.prev_dialog.dismiss()
        comics_collection = self.comics_collection.comics
        comic_obj = self.comic_obj
        index = comics_collection.index(comic_obj) # first index where x appears
        if index < len(comics_collection):
            if index == 0:
                return
            else:
                self.load_comic_book(self.prev_comic,self.comics_collection)

    def set_just_loaded(self,clock):
        self.just_loaded = False

    #Just here to test

    def load_random_comic(self):
        print Logger.info
        # def got_data(req,results):
        #
        #     data = results
        #     new_collection = ComicCollection()
        #     print data
        #
        #     new_comic = ComicBook(data['comics'][0])
        #     new_collection.add_comic(new_comic)
        #     self.load_comic_book(new_comic,new_collection)
        # comic_id_number = random.randint(2660, 2780)
        # base_url = App.get_running_app().config.get('Server', 'url')
        # recent_list  = "%s/comic/%d" % (base_url,comic_id_number)
        # req = CustomUrlRequest(recent_list,
        #                        got_data,
        #
        #                        timeout = 15,
        #                        )

class ComicBookPageScatter(ScatterLayout):
    zoom_state = StringProperty()
    def __init__(self, **kwargs):
        super(ComicBookPageScatter, self).__init__(**kwargs)
        self.zoom_state = 'normal'
        self.move_state = 'open'
    def on_touch_down(self, touch):
        if touch.is_double_tap:
            if self.zoom_state == 'zoomed':
                self.zoom_state = 'normal'
                mat = self.transform_inv
                self.apply_transform(mat,anchor=(0,0))
            elif self.zoom_state == 'normal':
                self.zoom_state = 'zoomed'
                mat = Matrix().scale(2,2,2)
                self.apply_transform(mat,anchor=touch.pos)
        return super(ComicBookPageScatter, self).on_touch_down(touch)

    def on_transform_with_touch(self,touch):
         self.zoom_state = 'zoomed'
         return super(ComicBookPageScatter, self).on_transform_with_touch(touch)

class ComicBookPageImage(AsyncImage):
    def _new_image_downloaded(self, scatter , outer_grid,comic_number,var_i,proxyImage,):
        '''Fired once the image is downloaded and ready to use'''
        def _remove_widget():
            carousel.remove_widget(scatter)

        def _add_parts():
            strech_image = App.get_running_app().config.get('Display', 'stretch_image')
            if strech_image == '1':
                s_allow_stretch=True
                s_keep_ratio=False
            else:
                s_allow_stretch=False
                s_keep_ratio=True
            part_1 = ComicBookPageImage(_index=var_i,id='pi_'+str(var_i)+'b',allow_stretch=s_allow_stretch,keep_ratio=s_keep_ratio)
            part_2 = ComicBookPageImage(_index=var_i+1,id='pi_'+str(var_i)+'b',allow_stretch=s_allow_stretch,keep_ratio=s_keep_ratio)
            scatter_1 = ComicBookPageScatter(id='comic_scatter'+str(var_i))
            scatter_2 = ComicBookPageScatter(id='comic_scatter'+str(var_i)+'b')
            part_1.texture = proxyImage.image.texture.get_region(0,0,c_width/2,c_height)
            part_2.texture = proxyImage.image.texture.get_region((c_width/2+1),0,c_width/2,c_height)
            scatter_1.add_widget(part_1)
            scatter_2.add_widget(part_2)
            carousel.add_widget(scatter_1,i)
            carousel.add_widget(scatter_2,i+1)



        if proxyImage.image.texture:
            split_dbl_page = App.get_running_app().config.get('Display', 'dblpagesplit')
            if proxyImage.image.texture.width > 2*Window.width and split_dbl_page == '1':

                base_url = App.get_running_app().config.get('Server', 'url')
                src_thumb = "%s/comic/%d/page/%d?max_height=200#.jpg" % (base_url, comic_number, var_i)
                app = App.get_running_app()
                inner_grid_id ='inner_grid' + str(var_i)
                page_image_id = str(var_i)
                carousel = App.get_running_app().root.ids.comic_book_screen.ids.comic_book_carousel
                inner_grid_id = 'inner_grid%s'%str(var_i)
                c_width = self.texture.width
                c_height = self.texture.height
                Logger.debug('<<<New Split it running>>>>')
                i = 0
                for slide in carousel.slides:
                    if slide.id == scatter.id:
                        _remove_widget()
                        _add_parts()
                    i+=1

            else:
                if proxyImage.image.texture.width > 2*Window.width:
                    scatter.size_hint=(2,1)

class ComicCarousel(Carousel):
    pass



#<<<<Following are class for popup at bottom page for pressing and going to page x
class ThumbPopPagePopup(Popup):
    pass

class ThumbPopPageScroll(ScrollView):
    pass

class ThumbPopPageOutterGrid(GridLayout):
    pass

class ThumbPopPageInnerGrid(GridLayout):
    pass

class ThumbPopPagebntlbl(Button):
    pass

class ThumbPopPageSmallButton(Button):
    pass

class ThumbPopPageImage(RectangularRippleBehavior,ButtonBehavior,AsyncImage):

    def click(self,instance):
        app = App.get_running_app()
        # app.root.current = 'comic_book_screen'
        page_nav_popup = app.root.ids.comic_book_screen.page_nav_popup
        page_nav_popup.dismiss()
        carousel = App.get_running_app().root.ids.comic_book_screen.ids.comic_book_carousel
        for slide in carousel.slides:
            if slide.id == self.id:
                use_slide = slide
        carousel.load_slide(use_slide)
#<<<<<<<<<<

#<<<<Following are class for Next list>>>>>>>>>


#Button for screen tapping control

class ControlButton(Button):
    location = StringProperty()
    def enable_me(self,instance):
        Logger.debug('I am enabled')
        self.disabled = False

    def on_touch_down(self, touch):
        if self.disabled:
            if self.collide_point(*touch.pos):
                comic_book_screen =App.get_running_app().root.ids.comic_book_screen
                comic_book_carousel = comic_book_screen.ids.comic_book_carousel
                current_slide = comic_book_carousel.current_slide
                return current_slide.on_touch_down(touch)

        return super(ControlButton, self).on_touch_down(touch)

    def click(btn):
        btn.disabled = True
        Clock.schedule_once(btn.enable_me, .5)
        comic_book_screen =App.get_running_app().root.ids.comic_book_screen
        app = App.get_running_app()
        tap_option =  App.get_running_app().config.get('Screen Tap Control', str(btn.location))
        if tap_option == 'Next Page':
            comic_book_screen.load_next_slide()
        elif tap_option == 'Prev Page':
            comic_book_screen.load_prev_slide()
        elif tap_option == 'Open Page Nav':
            comic_book_screen.page_nav_popup_open()
        elif tap_option == 'Open Collection Browser':
             if len(comic_book_screen.comics_collection.comics)>1:
                comic_book_screen.comicscreen_open_collection_popup()
             else:
                 return
        elif tap_option == 'Prev Comic':
            comic_book_screen.load_prev_comic()
        elif tap_option == 'Next Comic':
            comic_book_screen.load_next_comic()
        elif tap_option == 'Return to Home Screen':
            app.manager.current = 'home_screen'
        else:
            return


#
# class ComicsCollectionInnerGrid(GridLayout):
#     pass
#
# class ComicsCollectionPagebntlbl(Label):
#     pass
#
# class ComicsCollectionImage(RectangularRippleBehavior,ButtonBehavior,AsyncImage):
#
#     comic = ObjectProperty()
#     comics_collection = ObjectProperty()
#
#
#
#     def enable_me(self,instance):
#         self.disabled = False
#
#     def click(self,instance):
#         self.disabled = True
#         app = App.get_running_app()
#         comic_screen = app.root.get_screen('comic_book_screen')
#         print 'comic id = %d'%self.comic.comic_id_number
#         comic_screen.load_comic_book(self.comic,self.comics_collection)
#         Clock.schedule_once(self.enable_me, .5)
# #<<<<<<<<<<


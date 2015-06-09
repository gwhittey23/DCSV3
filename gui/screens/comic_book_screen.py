from kivy.logger import Logger
from kivy.properties import NumericProperty,ObjectProperty,StringProperty

from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import Screen
from kivy.uix.scatterlayout import ScatterLayout
import random
from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.button import Button
from comicstream.url_get import CustomUrlRequest
from comicstream.comic_data import ComicCollection, ComicBook
from kivy.uix.button import ButtonBehavior
from gui.widgets.custom_effects import RectangularRippleBehavior
from gui.theme_engine.dialog import Dialog
import gc
from kivy.metrics import dp
from kivy.loader import Loader
from kivy.core.window import Window
from kivy.graphics.transformation import Matrix
from functools import partial
from kivy.uix.label import Label
class ComicBookScreen(Screen):

    def load_comic_book(self,comic_obj,comics_collection):
        Loader.pool.tasks.queue.clear()
        self.comics_collection = comics_collection
        self.comic_obj = comic_obj
        comic_book_carousel = self.ids['comic_book_carousel']
        comic_book_carousel.clear_widgets()
        gc.collect()
        number_pages = comic_obj.page_count
        base_url = App.get_running_app().config.get('Server', 'url')
        max_height = App.get_running_app().config.get('Server', 'max_height')
        scroll = ScrollView( size_hint=(1,1), do_scroll_x=True, do_scroll_y=False,id='page_thumb_scroll')
        self.page_nav_popup = Popup(id='page_nav_popup',title='Pages', content=scroll, pos_hint ={'y': .0001},size_hint = (1,.33))
        self.scroller = scroll
        outer_grid = GridLayout(rows=1, size_hint=(None,None),spacing=5,padding_horizontal=5,id='outtergrd')
        outer_grid.bind(minimum_width=outer_grid.setter('width'))
        for i in range(0, number_pages):
            comic_page_scatter = ComicBookPageScatter(id='comic_scatter'+str(i))
            src_full = "%s/comic/%d/page/%d?max_height=%d#.jpg" % (base_url, comic_obj.comic_id_number, i,int(max_height))
            print src_full
            comic_page_image = ComicBookPageImage(source=src_full,id='pi_'+str(i),nocache=True)
            comic_page_scatter.add_widget(comic_page_image)
            comic_book_carousel.add_widget(comic_page_scatter)
            #Let's make the thumbs for popup
            inner_grid = ThumbPopPageInnerGrid(id='inner_grid'+str(i))
            src_thumb = "%s/comic/%d/page/%d?max_height=200#.jpg" % (base_url, comic_obj.comic_id_number, i)
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
            self.build_top_list()
            self.next_comic = self.get_next_comic()
            self.prev_comic = self.get_prev_comic()
            self.build_next_comic_dialog()
            self.build_prev_comic_dialog()
            self.ids['btn_collection'].disabled = False
        else:
            self.ids['btn_collection'].disabled = True

    def get_prev_comic(self):
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

    def load_next_slide(self,btn):
        comic_book_carousel = self.ids['comic_book_carousel']
        if comic_book_carousel.index == len(comic_book_carousel.slides)-1:
            self.open_next_dialog()
            return
        else:
            comic_book_carousel.load_next()
        btn.disabled = True
        Clock.schedule_once(btn.enable_me, .5)

    def load_prev_slide(self,btn):
        comic_book_carousel = self.ids['comic_book_carousel']
        if comic_book_carousel.index == 0:
            self.open_prev_dialog()
            return
        else:
            comic_book_carousel.load_previous()
        btn.disabled = True
        Clock.schedule_once(btn.enable_me, .5)

    def page_nav_popup_open(self):

        self.page_nav_popup.open()
        carousel = self.ids['comic_book_carousel']
        current_slide = carousel.current_slide
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

    def build_top_list(self):
        scroll = ScrollView( size_hint=(1,1), do_scroll_x=True, do_scroll_y=False,id='page_thumb_scroll')
        self.top_pop = Popup(id='page_pop',title='Pages', content=scroll, pos_hint ={'y': .7},size_hint = (1,.33))
        grid = GridLayout(rows=1, size_hint=(None,None),spacing=5,padding_horizontal=5,id='outtergrd')
        grid.bind(minimum_width=grid.setter('width'))
        for comic in self.comics_collection.comics:
            comic_name = '%s #%s'%(str(comic.series),str(comic.issue))
            src_thumb = comic.thumb_url
            inner_grid = ComicsCollectionInnerGrid(id='inner_grid'+str(comic.comic_id_number))
            comic_thumb = ComicsCollectionImage(source=src_thumb,id=str(comic.comic_id_number),nocache=True)
            comic_thumb.comic = comic
            comic_thumb.comics_collection = self.comics_collection
            inner_grid.add_widget(comic_thumb)
            comic_thumb.bind(on_release=self.top_pop.dismiss)
            comic_thumb.bind(on_release=comic_thumb.click)

            smbutton = ComicsCollectionPagebntlbl(text=comic_name)
            inner_grid.add_widget(smbutton)
            grid.add_widget(inner_grid)
        scroll.add_widget(grid)

    def build_next_comic_dialog(self):
        ''' Make popup showing cover for next comic'''
        base_url = App.get_running_app().config.get('Server', 'url')
        comic = self.next_comic
        Logger.debug('self.next_comic.comic_id_number: %s'%self.next_comic.comic_id_number)
        Logger.debug('comic_id_number: %s'%comic.comic_id_number)

        comic_name = '%s #%s'%(str(comic.series),str(comic.issue))
        src_thumb = comic.thumb_url
        inner_grid = ComicsCollectionInnerGrid(id='inner_grid'+str(comic.comic_id_number))
        comic_thumb = ComicsCollectionImage(source=self.next_comic.thumb_url,id=str(comic.comic_id_number),nocache=True)

        comic_thumb.comic = self.next_comic
        comic_thumb.comics_collection = self.comics_collection
        inner_grid.add_widget(comic_thumb)

        smbutton = ComicsCollectionPagebntlbl(text=comic_name)
        inner_grid.add_widget(smbutton)
        content = inner_grid
        self.next_dialog = Dialog(title="Load Next",
                             content=content,
                             size_hint=(.3, .3),
                             height=dp(250),
                             auto_dismiss=True)
        comic_thumb.bind(on_release=self.next_dialog.dismiss)
        comic_thumb.bind(on_release=comic_thumb.click)

    def open_next_dialog(self):
         self.next_dialog.open()

    def build_prev_comic_dialog(self):
        base_url = App.get_running_app().config.get('Server', 'url')
        prev_comic = self.prev_comic
        comic_name = '%s #%s'%(str(prev_comic.series),str(prev_comic.issue))
        src_thumb = prev_comic.thumb_url
        inner_grid = ComicsCollectionInnerGrid(id='inner_grid'+str(prev_comic.comic_id_number))
        comic_thumb = ComicsCollectionImage(source=self.prev_comic.thumb_url,id=str(prev_comic.comic_id_number),nocache=True)

        comic_thumb.comic = self.prev_comic
        comic_thumb.comics_collection = self.comics_collection
        inner_grid.add_widget(comic_thumb)

        smbutton = ComicsCollectionPagebntlbl(text=comic_name)
        inner_grid.add_widget(smbutton)
        content = inner_grid


        self.prev_dialog = Dialog(title="Load Next",
                             content=content,
                             size_hint=(.3, .3),
                             height=dp(250),
                             auto_dismiss=True)
        comic_thumb.bind(on_release=self.prev_dialog.dismiss)
        comic_thumb.bind(on_release=comic_thumb.click)

    def open_prev_dialog(self):
         self.prev_dialog.open()

    def load_next_comic(self):
        self.dialog.dismiss()
        self.load_comic_book(self.next_comic,self.comics_collection)

    def load_prev_comic(self):
        self.dialog.dismiss()
        self.load_comic_book(self.prev_comic,self.comics_collection)


    #Just here to test

    def load_random_comic(self):
        def got_data(req,results):

            data = results
            new_collection = ComicCollection()
            print data

            new_comic = ComicBook(data['comics'][0])
            new_collection.add_comic(new_comic)
            self.load_comic_book(new_comic,new_collection)
        comic_id_number = random.randint(2660, 2780)
        base_url = App.get_running_app().config.get('Server', 'url')
        recent_list  = "%s/comic/%d" % (base_url,comic_id_number)
        req = CustomUrlRequest(recent_list,
                               got_data,

                               timeout = 15,
                               )

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
            part_1 = ComicBookPageImage(_index=var_i,id='pi_'+str(var_i)+'b')
            part_2 = ComicBookPageImage(_index=var_i+1,id='pi_'+str(var_i)+'b')
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
                carousel = App.get_running_app().root.ids['comic_book_screen'].ids['comic_book_carousel']
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

class ControlButton(Button):
    def enable_me(self,instance):
        Logger.debug('I am enabled')
        self.disabled = False

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
        page_nav_popup = app.root.ids['comic_book_screen'].page_nav_popup
        page_nav_popup.dismiss()
        carousel = App.get_running_app().root.ids['comic_book_screen'].ids['comic_book_carousel']
        for slide in carousel.slides:
            if slide.id == self.id:
                use_slide = slide
        carousel.load_slide(use_slide)
#<<<<<<<<<<

#<<<<Following are class for Next list>>>>>>>>>
class ComicsCollectionScroll(ScrollView):
    pass

class ComicsCollectionOuterGrid(GridLayout):
    pass

class ComicsCollectionInnerGrid(GridLayout):
    pass

class ComicsCollectionPagebntlbl(Label):
    pass

class ComicsCollectionImage(RectangularRippleBehavior,ButtonBehavior,AsyncImage):

    comic = ObjectProperty()
    comics_collection = ObjectProperty()



    def enable_me(self,instance):
        self.disabled = False

    def click(self,instance):
        self.disabled = True
        app = App.get_running_app()
        comic_screen = app.root.get_screen('comic_book_screen')
        print 'comic id = %d'%self.comic.comic_id_number
        comic_screen.load_comic_book(self.comic,self.comics_collection)
        Clock.schedule_once(self.enable_me, .5)
#<<<<<<<<<<
from kivy.logger import Logger
from kivy.properties import NumericProperty,ObjectProperty

from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import Screen
from kivy.uix.scatterlayout import ScatterLayout
import random
from kivy.app import App
from kivy.uix.carousel import Carousel
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup


class ComicBookScreen(Screen):
    def load_comic_book(self,comic_book_number=1755):

        comic_book_carousel = self.ids['comic_book_carousel']
        comic_book_carousel.clear_widgets()
        number_pages = 20
        base_url = App.get_running_app().config.get('Server', 'url')
        max_height = App.get_running_app().config.get('Server', 'max_height')
        scroll = ScrollView( size_hint=(1,1), do_scroll_x=True, do_scroll_y=False,id='page_thumb_scroll')
        self.thumb_pop = Popup(id='page_pop',title='Pages', content=scroll, pos_hint ={'y': .0001},size_hint = (1,.33))
        self.scroller = scroll
        outer_grid = GridLayout(rows=1, size_hint=(None,None),spacing=5,padding_horizontal=5,id='outtergrd')
        outer_grid.bind(minimum_width=outer_grid.setter('width'))
        for i in range(0, number_pages):
            comic_book_scatter = ComicBookPageScatter(id='comic_scatter'+str(i))
            src_full = "%s/comic/%d/page/%d?max_height=%d#.jpg" % (base_url, comic_book_number, i,int(max_height))
            comic_book_image = ComicBookPageImage(source=src_full,id='pi_'+str(i),nocache=True)
            comic_book_scatter.add_widget(comic_book_image)
            comic_book_carousel.add_widget(comic_book_scatter)
    #Just here to test
    def load_random_comic(self):
        comic_number = random.randint(2660, 2780)
        self.load_comic_book(comic_number)
class ComicBookPageScatter(ScatterLayout):
    pass


class ComicBookPageImage(AsyncImage):
    pass

class ComicCarousel(Carousel):
    pass
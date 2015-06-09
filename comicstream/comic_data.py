from kivy.properties import ListProperty,ObjectProperty,DictProperty,StringProperty
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import AsyncImage



class ComicCollection(object):

    # ids = DictProperty({})
    # name = StringProperty()
    def __init__(self):
        self.size = 65
        self.comics = []
        self.mynumber = 32
    '''Group of Comics in bundlded together'''
    def add_comic(self, comic, index=0):

        '''
            Add Single comic book to this colection
        '''
        if index == 0 or len(self.comics) == 0:
            self.comics.insert(0, comic)
        else:
            comics = self.comics
            if index >= len(comics):
                index = len(comics)
            comics.insert(index, comic)
    def remove_comic(self, comic):
        '''
            Remove a comic from the comics of this collection.
        '''

        if comic not in self.comics:
            return
        self.comics.remove(comic)
        comic.collection = None

    def clear_comics(self, comics=None):
        '''
            Remove all Comics added to this Collection.
        '''

        if not comics:
            comics = self.comics
        remove_comic = self.remove_comic
        for comic in comics[:]:
            remove_comic(comic)

    def get_comic_by_number(self,comic_number):
        '''
            Will return the comic that matches id number x this number is ATM comicstreaer server id number.
        '''
        for comic in self.comics:
            if comic.comic_id_number == comic_number:
                return comic
class ComicsCoverImage(ButtonBehavior,AsyncImage):
    comic = ObjectProperty()
    comics_collection = ObjectProperty()

    def click(self,instance):
        app = App.get_running_app()
        app.root.current = 'comic_screen'
        comic_screen = app.root.get_screen('comic_screen')
        comic_screen.load_comic(self.comic,self.comics_collection)

class ComicBook(object):
    cover = ObjectProperty()
    '''
    class representing a single comic
    '''
    def __init__(self, data,*args, **kwargs):
        print 'Start Comic Class'
        comic_data = data
        self.comic_id_number = comic_data['id']#this is the id number used for comicstream switched to this because of id of widget
        self.added_ts = comic_data['added_ts']
        self.month = comic_data['month']
        self.year = comic_data['year']
        self.comments = comic_data['comments']
        self.pubdate = comic_data['date']
        self.issue = comic_data['issue']
        self.page_count = comic_data['page_count']
        self.publisher = comic_data['publisher']
        self.series = comic_data['series']
        self.storyarcs = comic_data['storyarcs']
        self.title = comic_data['title']
        self.volume = comic_data['volume']
        self.weblink = comic_data['weblink']
        self.mod_ts = comic_data['mod_ts']
        self.page_count = comic_data['page_count']
        self.credits = comic_data['credits']
        self.characters =  comic_data['characters']
        self.characters =  comic_data['characters']

        #TODO:Add in implement better into the comic
        #self.credits = comic_data['credits']
        #self.characters =  comic_data['characters']
        #self.characters =  comic_data['characters']

        base_url = App.get_running_app().config.get('Server', 'url')
        src_thumb = "%s/comic/%s/thumbnail#.jpg" % (base_url, self.comic_id_number)
        self.thumb_url  = src_thumb

    def json_data(self):
        pass

        # comic_data = data
        # self.comic_id_number = comic_data['id']
        # self.added_ts = comic_data['added_ts']
        # self.month = comic_data['month']
        # self.year = comic_data['year']
        # self.comments = comic_data['comments']
        # self.pubdate = comic_data['date']
        # self.issue = comic_data['issue']
        # self.page_count = comic_data['page_count']
        # self.publisher = comic_data['publisher']
        # self.series = comic_data['series']
        # self.storyarcs = comic_data['storyarcs']
        # self.title = comic_data['title']
        # self.volume = comic_data['volume']
        # self.weblink = comic_data['weblink']
        # self.mod_ts = comic_data['mod_ts']
        # self.page_count = comic_data['page_count']
        #self.credits = comic_data['credits']
        #self.characters =  comic_data['characters']
        #self.teams = comic_data['teams']



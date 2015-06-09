from kivy.network.urlrequest import UrlRequest
from kivy.app import App
from comic_data import ComicCollection,ComicBook
from kivy.logger import Logger
from comicstream.url_get import CustomUrlRequest
from kivy.network.urlrequest import UrlRequest
import inspect

class Bob(object):
    pass
class ComicStreamerConnect(App):

    def __init__(self):

        self.data = ''

     # def get_server_data(self):
     #     get_series_url = "%s/comiclist?order=added&per_page=10" % (self.base_url, , i)

    # def get_recent_comics(self):
    #     print 'ok'
    #     def got_error(req, results):
    #         print 'got_error'
    #         Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    #     def got_time_out(req, results):
    #         Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    #     def got_failure(req, results):
    #         Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    #     def got_redirect(req, results):
    #         Logger.critical('ERROR in %s %s'%(inspect.stack()[0][3],results))
    #     def got_data(req, results):
    #         self.data = results
    #         print 'Fired got_data'
    #         print results
    #     # self.base_url = App.get_running_app().config.get('Server', 'url')
    #     self.base_url = 'http://192.168.0.3:32500'
    #     recent_list  = "%s/comiclist?order=-added&per_page=10" % (self.base_url)
    #     print recent_list
    #     self.req = UrlRequest(recent_list,
    #                            on_success=got_data,
    #                            on_error=got_error,
    #                            on_failure=got_failure,
    #                            on_redirect=got_redirect,
    #                            timeout = 5,
    #                             debug=True
    #                            )


if __name__ == '__main__':
    c = ComicStreamerConnect()
    c.get_recent_comics()
import os
import tornado.web
import mopidy_redbox
import library

class MainHandler(tornado.web.RequestHandler):
    def initialize(self):
        pass

    def get(self):
        self.render("site/index.html", active_page="index")
        

class BrowseHandler(tornado.web.RequestHandler):
    def initialize(self, core):
        self.core = core

    def get(self):
        self.render("site/browse.html", active_page="browse")


class RadioHandler(tornado.web.RequestHandler):
    def initialize(self, config):
        self.lib = library.Library(os.path.join(mopidy_redbox.Extension.get_data_dir(config), b'library.json.gz'), podcast_timeout=config['redbox']['podcasts_timeout'])

    def get(self, radio_bank=None):
        radios = self.lib.data['radio_banks']

        if radio_bank is None:
            if len(radios) > 0:
                radio_bank = radios.keys()[0]

        if radio_bank not in radios:
            radio_bank = None

        self.render("site/radios.html", active_page="radios", radios=radios, radio_bank=radio_bank)

    def post(self, *args, **kwargs):
        print args, kwargs
import logging
import os
import random

import mopidy
from mopidy import backend, exceptions, models

from mopidy import local
from mopidy.internal import storage as internal_storage

import pykka

import urllib
import podcastparser

import mopidy_redbox
import library

logger = logging.getLogger(__name__)


class RedBoxBackend(pykka.ThreadingActor, backend.Backend):
    uri_schemes = [
        'redbox'
    ]

    def __init__(self, config, audio):
        super(RedBoxBackend, self).__init__()

        lib = library.Library(os.path.join(mopidy_redbox.Extension.get_data_dir(config), b'library.json.gz'), podcast_timeout=config['redbox']['podcasts_timeout'])
        lib.update_podcasts()
        
        self.library = RedBoxLibraryProvider(self, lib)
        self.playback = RedBoxPlaybackProvider(audio, self, lib, config['redbox']['noise_folder'])




class RedBoxLibraryProvider(backend.LibraryProvider):
    def __init__(self, backend, lib):
        super(RedBoxLibraryProvider, self).__init__(backend)
        self.lib = lib

    @property
    def root_directory(self):
        return models.Ref.directory(name='RedBox', uri="redbox:")

    def refresh(self, uri=None):
        self.lib.load()


    def lookup(self, uri):
        if not uri.startswith("redbox:"):
            return []

        if uri == "redbox:noise":
            return [models.Track(name="Random Noise", uri=uri)]

        split_uri = uri.split(":")

        if len(split_uri) == 4:
            if split_uri[1] == "radios":
                bank_radios = self.lib.data['radio_banks'][split_uri[2]]
                for rad in bank_radios:
                    if rad['position'] == int(split_uri[3]):
                        return [models.Track(name=rad['name'], uri=uri, artists=[models.Artist(name=rad['name'])], album=models.Album(name=split_uri[2]))]


            if split_uri[1] == "podcasts":
                for podcast in self.lib.data['podcasts']:
                    if podcast['position'] == int(split_uri[2]):
                        for ep in podcast['episodes']:
                            if split_uri[3] == ep['title']:
                                return [models.Track(name=ep['title'], uri=uri, artists=[models.Artist(name=podcast['name'])], album=models.Album(name=""))]



        return []

    def browse(self, uri):
        if not uri.startswith("redbox:"):
            return []

        if uri == "redbox:noise":
            return [models.Ref.track(name="Random Noise", uri="redbox:noise")]

        split_uri = uri.split(":")

        # root
        if len(split_uri) == 2:
            if split_uri[1] == "":
                return [
                    models.Ref.directory(name="Radios", uri="redbox:radios"),
                    models.Ref.directory(name="Podcast", uri="redbox:podcasts"),
                    models.Ref.directory(name="Noise", uri="redbox:noise")
                ]

            if split_uri[1] == "radios":
                return [
                    models.Ref.album(name=bank, uri="redbox:radios:{}".format(bank)) for bank in self.lib.data["radio_banks"]
                ]

            if split_uri[1] == "podcasts":
                return [
                    models.Ref.album(name=podcast['name'], uri="redbox:podcasts:{}".format(podcast['position'])) for podcast in self.lib.data["podcasts"]
                ]

        if len(split_uri) == 3:
            if split_uri[1] == "radios":
                return [
                    models.Ref.track(name=radio['name'], uri="redbox:radios:{}:{}".format(split_uri[2], radio['position'])) for radio in self.lib.data['radio_banks'][split_uri[2]]
                ]
            if split_uri[1] == "podcasts":
                for podcast in self.lib.data['podcasts']:
                    if podcast['position'] == int(split_uri[2]):
                        return [
                            models.Ref.track(name=episode['title'], uri="redbox:podcasts:{}:{}".format(split_uri[2], episode['title'])) 
                                for episode in podcast['episodes']
                        ]
        return []


class RedBoxPlaybackProvider(backend.PlaybackProvider):
    def __init__(self, audio, backend, lib, noise_folder):
        super(RedBoxPlaybackProvider,  self).__init__(audio, backend)
        self.lib = lib
        self.noises = self.find_noise_files(noise_folder)

    def translate_uri(self, uri):
        if not uri.startswith("redbox:"):
            return None

        if uri == "redbox:noise":
            fn = self.noises[random.randint(0, len(self.noises)-1)]
            return "file://"+fn

        split_uri = uri.split(":")

        if len(split_uri) == 4:
            if split_uri[1] == "radios":
                bank_radios = self.lib.data['radio_banks'][split_uri[2]]
                for rad in bank_radios:
                    if rad['position'] == int(split_uri[3]):
                        return rad['stream_url']

            if split_uri[1] == "podcasts":
                for podcast in self.lib.data['podcasts']:
                    if int(split_uri[2]) == podcast['position']:
                        for ep in podcast['episodes']:
                            if split_uri[3] == ep['title']:
                                return ep['url']

        return None


    def find_noise_files(self, path):
        folder = path
        if not os.path.isdir(folder):
            logger.warning("Bad Noise folder: {}".format(folder))
            return []

        # get random file in this directory
        onlyfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and os.path.splitext(f)[-1].lower() in [".wav", ".mp3"]]
        if len(onlyfiles) == 0:
            logger.warning("No files found in FM Noise folder: {}.".format(folder))
            return []

        return [os.path.join(folder, fn) for fn in onlyfiles]



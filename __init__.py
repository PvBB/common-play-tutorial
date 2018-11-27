import re
from mycroft.skills.core import intent_handler, intent_file_handler
from mycroft.util.parse import match_one, fuzzy_match
from mycroft.util.log import LOG
from mycroft.api import DeviceApi
from padatious import IntentContainer
from requests import HTTPError
from adapt.intent import IntentBuilder

import time
from subprocess import Popen, DEVNULL
import signal
from socket import gethostname
import random
from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel

track_dict = {
    'sky radio': 'http://playerservices.streamtheworld.com/api/livestream-redirect/SKYRADIO.mp3',
    'radio veronica':  'http://playerservices.streamtheworld.com/api/livestream-redirect/VERONICA.mp3',
    'sublime FM': 'http://stream.sublimefm.nl/SublimeFM_aac'
}


class InternetRadioSkill(CommonPlaySkill):
    def CPS_match_query_phrase(self, phrase):
        """ This method responds wether the skill can play the input phrase.

            The method is invoked by the PlayBackControlSkill.

            Returns: tuple (matched phrase(str),
                            match level(CPSMatchLevel),
                            optional data(dict))
                     or None if no match was found.
        """
        # Get match and confidence
        match, confidence = match_one(phrase, track_dict)
        # If the confidence is high enough return a match
        if confidence > 0.9:
            return (match, CPSMatchLevel.EXACT, {"track": match})
        elif confidence > 0.7:
            return (match, CPSMatchLevel.MULTI_KEY, {"track": match})
        elif confidence > 0.5:
            return (match, CPSMatchLevel.TITLE, {"track": match})
        # Otherwise return None
        else:
            return None

    def CPS_start(self, phrase, data):
        """ Starts playback.

            Called by the playback control skill to start playback if the
            skill is selected (has the best match level)
        """
        url = data['track']
        self.audioservice.play(url)
        
    #### implement audio ducking
    def handle_listener_started(self, message):
        """ Handle auto ducking when listener is started.
        The ducking is enabled/disabled using the skill settings on home.
        TODO: Evaluate the Idle check logic
        """
        if self.audioservice.is_playing():
            self.__pause()
            self.ducking = True

            # Start idle check
            self.idle_count = 0
            self.cancel_scheduled_event('IdleCheck')
            self.schedule_repeating_event(self.check_for_idle, None,
                                          1, name='IdleCheck')

    def check_for_idle(self):
        """ Repeating event checking for end of auto ducking. """
        if not self.ducking:
            self.cancel_scheduled_event('IdleCheck')
            return

        active = self.enclosure.display_manager.get_active()
        if not active == '' or active == 'InternetRadioSkill':
            # No activity, start to fall asleep
            self.idle_count += 1

            if self.idle_count >= 5:
                # Resume playback after 5 seconds of being idle
                self.cancel_scheduled_event('IdleCheck')
                self.ducking = False
                self.resume()
        else:
            self.idle_count = 0


def create_skill():
    return InternetRadioSkill()

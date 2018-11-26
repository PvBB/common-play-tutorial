from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel

from mycroft.util.parse import match_one


track_dict = {
    'sky radio': 'http://playerservices.streamtheworld.com/api/livestream-redirect/SKYRADIO.mp3',
    'radio veronica':  'http://playerservices.streamtheworld.com/api/livestream-redirect/VERONICA.mp3'
}


class TutorialSkill(CommonPlaySkill):
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
        if confidence > 0.5:
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


def create_skill():
    return TutorialSkill()

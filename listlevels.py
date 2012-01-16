#!/usr/bin/python
from __future__ import division

# This script takes a username and spits out a list of links to all
# works drawn by that user.
import cgi
import cgitb
import math

from database_tables import Level, LevelObject, Score
from webserver_utils import render_template_file, verify_id, make_lang_settings
from sqlobject import OR

def formatTime(ms):
    s = math.floor(ms / 1000)
    ms = ms % 1000
    m = math.floor(s / 60)
    s = s % 60
    
    return "%d:%02d.%02d" % (m, s, ms)


def printList(player):
    print "Content-type: text/html"
    print

    # Show levels that are published and/or created by the current player.
    matches = Level.select(OR(Level.q.published == True, 
                              Level.q.creator == player), orderBy = "-modified")
    published_list = ""
    your_list = ""
    for level in matches:
        title = level.name
        date = level.modified
        edit_link = ""
        if level.creator != None:
            if level.creator == player:
                creator = "You"            # TODO l10n
            else:
                creator = level.creator.name
        else:
            creator = "Nobody"            # TODO l10n
            
        scores = Score.selectBy(level = level)
        best = ""
        if (scores.count() > 0):
            # TODO l10n
            best = "%s by %s with %d trinkets" % (formatTime(scores[0].completionTime),
                                                 scores[0].player.name,
                                                 scores[0].trinkets)
        else:
            best = "Nobody Yet!"            # TODO l10n
        scores = Score.selectBy(player = player, level = level)
        your_time = ""
        if (scores.count() > 0):
            # TODO l10n
            your_time = "%s with %d trinkets" % (formatTime(scores[0].completionTime), 
                                                 scores[0].trinkets)
        if level.creator == player:
            if level.published:
              published = "Yes"            # TODO l10n
            else:
              published = "No"
            your_list += render_template_file( "list-my-level-row.html",
                                               {"moddate": date,
                                                "title": title,
                                                "published": published,
                                                "best": best,
                                                "yourtime": your_time} )
        else:
            published_list += render_template_file( "list-level-row.html",
                                           {"moddate": date,
                                            "title": title,
                                            "creator": creator,
                                            "best": best,
                                            "yourtime": your_time} )

    sub_words = {"published_list": published_list,
                 "your_list": your_list,
                 "player": player.name,
                 "avatarURL": player.avatarURL,
                 "lang_radio_buttons": make_lang_settings(player.langPref)}
    
    print render_template_file( "list-levels.html", sub_words)

if __name__ == "__main__":
    cgitb.enable()
    q = cgi.FieldStorage()

    player = verify_id()
    # action = q.getfirst("action", "")
    # title = q.getfirst("title", "")

    printList(player)



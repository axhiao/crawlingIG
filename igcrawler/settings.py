# coding: utf-8

defaults = {
    "fetch_likes_plays": False,
    "fetch_likers": False,
    "fetch_comments": False,
    "fetch_mentions": False,
    "fetch_hashtags": False,
    "fetch_details": False
}

HEAD = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36',
    'Origin': 'https://www.instagram.com/',
    'Sec-Fetch-Dest' : 'script'
}

from enum import Enum
class Relation(Enum):
    DEFAULT = 0 # default: meaningless
    FLER_FLIG = 1 # follower -> following, 
    FLER_TAG = 2 # follower -> tag_id, user table also stores the following hashtag name.
    PST_TAG = 3 # post -> tag
    CMT_PST = 4 # comment -> post
    CMT_CMT = 5 # comment -> comment

class DrugTypeNew(Enum):
    UNRELATED = 0
    BOTTLE = 1
    LEAVES = 2
    LSDART = 3
    PILL = 4
    WPOWDER = 5
    LSDSHEET = 6
    MUSHROOM = 7
# 0,not drug-related image
# 1,bottle
# 2,leaves
# 3,lsd art
# 4, pills
# 5, white powder
# 6,lsd sheet
# 7,magic mushroom

class DrugType(Enum):
    BOTTLE = 0
    POWDER = 1
    WEED = 2
    LSD = 3
    PILLS = 4
    NODRUG = 5
    
def apply_defaults(cls):
    for name, value in defaults.items():
        setattr(cls, name, value)
    return cls


@apply_defaults
class settings(object):
    pass


def override_settings(args):
    for name in defaults.keys():
        setattr(settings, name, getattr(args, name))


def prepare_override_settings(parser):
    for name in defaults.keys():
        parser.add_argument("--" + name, action="store_true")

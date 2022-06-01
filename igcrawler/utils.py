# coding: utf-8

import os
import random
import hashlib
from functools import wraps
from time import sleep
import requests

from igcrawler.settings import HEAD
from igcrawler.exceptions import RetryException


def instagram_int(string):
    return int(string.replace(",", ""))

def retry(attempt=10, wait=0.3):
    def wrap(func):
        @wraps(func)
        def wrapped_f(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RetryException:
                if attempt > 1:
                    sleep(wait)
                    return retry(attempt - 1, wait)(func)(*args, **kwargs)
                else:
                    exc = RetryException()
                    exc.__cause__ = None
                    raise exc

        return wrapped_f

    return wrap


def randmized_sleep(average=1):
    """
        range = [0.5*param, 1.5*param]
    """
    _min, _max = average * 1 / 2, average * 3 / 2
    sleep(random.uniform(_min, _max))


def validate_posts(dict_posts):
    """
        The validator is to verify if the posts are fetched wrong.
        Ex. the content got messed up or duplicated.
    """
    posts = dict_posts.values()
    contents = [post["datetime"] for post in posts]
    # assert len(set(contents)) == len(contents)
    if len(set(contents)) == len(contents):
        print("These post data should be correct.")


# class Singleton(object):
#     def __init__(self, cls, *args, **kwargs):
#         self._cls = cls
#         self._instance = {}
    
#     def __call__(self, *args, **kwargs):
#         if self._cls not in self._instance:
#             self._instance[self._cls] = self._cls(args, kwargs)
#         return self._instance[self._cls]

# class Singleton(type):
#     _instances = {}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]

def Singleton(cls):
    instance = {}
    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instance:
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]
    return wrapper

def const_gis(authtokens, query):
    t = authtokens[0] + ':' + query
    x_instagram_gis = hashlib.md5(t.encode("utf-8")).hexdigest()
    return x_instagram_gis

@Singleton
class Gcnt():
    gcnt = 0
    lcnt = 0

# class AAA(object):
#     def __init__(self):
#         super().__init__()
#     pass


# if __name__ == '__main__':
#     f = os.path.dirname(os.path.dirname(os.path.realpath(__file__))).strip(os.sep) +\
#         os.sep + 'pic_store'
#     s = store_pic(f, "https://instagram.fagc1-1.fna.fbcdn.net/v/t51.2885-15/e35/s1080x1080/87395006_509125863121146_8281358186061852041_n.jpg?_nc_ht=instagram.fagc1-1.fna.fbcdn.net&_nc_cat=106&_nc_ohc=ArA21yhZ6EMAX9XvPJ8&oh=f78243c44a1be436f97c2b5b0934e183&oe=5E883A81")
#     print(s)

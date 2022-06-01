# coding: utf-8
import logging as log
import pymysql

from .utils import Singleton

import sys 
sys.path.append("..")
from db.model import Model

@Singleton
class Tagset(object):
    def __init__(self, csvsrc="", dbsrc=False):
        self.csvsrc = csvsrc
        self.dbsrc = dbsrc
        self.tag_list = list()
        self.tag_dict = dict()
        self.model = Model()
    
    def tag_from_text(self, text_list):
        for tag in text_list:
            if tag not in self.tag_dict:
                self.tag_list.insert(0, tag)
                self.tag_dict[tag] = 0 # default to access



    def tagload(self):
        # if self.dbsrc:
        #     self._load_from_db()
        if len(self.csvsrc) > 0:
            self._load_from_csv(self.csvsrc)

    def _load_from_csv(self, csv):
        try:
            with open(csv, 'rt') as f:
                for line in f:
                    lst = line.rstrip().split(' ')
                    for l in lst:
                        if l not in self.tag_dict: #or self.tag_dict[l] == 0:
                            self.tag_list.insert(0, l)
                            self.tag_dict[l] = 0 # default to access
        except FileNotFoundError:
            log.info('csv file load failed. No file found')

    def _load_from_db(self):
        for i in self.model.get_tagname():
            self.tag_list.append(i['name'])
            self.tag_dict[i['name']] = i['is_broken']
    
    def is_contain(self, s):
        return s in self.tag_dict
    
    def get_taglist(self):
        return self.tag_list

    def get_size(self):
        return len(self.tag_list)

    def print(self):
        print(self.tag_list)

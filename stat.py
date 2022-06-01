# coding:utf-8
import requests
import json
import sys, os, time
import pandas as pd
import random

from db.model import Model

oper = Model()

fpath = r'/home/lab321/weixiao/data/ig_links/negatives.json'
users = set()
with open(fpath, 'r') as fp:
    posts = json.load(fp)
    for p in posts:
        users.add(p['owner_name'])
        for c in oper.get_comments(p['id']):
            users.add(c['user_name'])


with open('/home/lab321/weixiao/data/ig_links/negative_name.csv', 'w') as fp:
    for name in users:
        fp.write(name + '\n')

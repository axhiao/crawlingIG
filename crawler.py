# coding: utf-8
from __future__ import unicode_literals

import argparse
import json
import sys
import os
import time
from io import open
import logging as log
import logging.config

from db.db import config as DBCONFIG
from igcrawler.crawler import InsCrawler
from igcrawler.settings import override_settings
from igcrawler.settings import prepare_override_settings
from igcrawler.tagset import Tagset

def init_log(level, filename = 'crawler.log', filepath = './log/'):
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    fullpath = filepath + filename
    level_coll = {
        "CRITICAL": log.CRITICAL,
        "FATAL": log.FATAL,
        "ERROR": log.ERROR,
        "WARNING": log.WARNING,
        "WARN": log.WARN,
        "INFO": log.INFO,
        "DEBUG": log.DEBUG,
        "NOTSET": log.NOTSET,
    }
    logging.basicConfig(
        filename = fullpath,
        level = level_coll[level],
        format = '%(asctime)s [%(threadName)s] [%(name)s] [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S'
    )

def usage():
    return """
        python crawler.py posts -u cal_foodie -n 100 -o ./output
        python crawler.py posts_full -u cal_foodie -n 100 -o ./output
        python crawler.py profile -u cal_foodie -o ./output
        python crawler.py profile_script -u cal_foodie -o ./output
        python crawler.py hashtag -t taiwan -o ./output
        The default number for fetching posts via hashtag is 100.
    """


def crawl_hashtag(tag_coll, debug, user_name, user_pwd):
    '''
        crawl every hashtag in the set.
    '''
    log.info('Start to crawl each hashtag...')

    
    ins_crawler = InsCrawler(get_pkl(), user_name, user_pwd, has_screen=debug)
    for tag in tag_coll.get_taglist():
        # ins_crawler.crawl_hashtag(tag)
        ins_crawler.crawl_hashtag_233(tag)
        
    # ins_crawler.crawl_hashtag('mdmatherapy')


def get_posts_by_user(username, number, detail, debug):
    ins_crawler = InsCrawler(weight_path=get_pkl(), has_screen=debug)
    return ins_crawler.get_user_posts(username, number, detail)


def get_profile(username):
    ins_crawler = InsCrawler(weight_path=get_pkl(), )
    return ins_crawler.get_user_profile(username)


def get_profile_from_script(username):
    ins_cralwer = InsCrawler(weight_path=get_pkl(), )
    return ins_cralwer.get_user_profile_from_script_shared_data(username)


def get_posts_by_hashtag(tag, number, debug):
    ins_crawler = InsCrawler(weight_path=get_pkl(), has_screen=debug)
    return ins_crawler.get_latest_posts_by_tag(tag, number)


def arg_required(args, fields=[]):
    for field in fields:
        if not getattr(args, field):
            parser.print_help()
            sys.exit()

def output(data, filepath):
    out = json.dumps(data, ensure_ascii=False)
    if filepath:
        with open(filepath, "w", encoding="utf8") as f:
            f.write(out)
    else:
        print(out)

def get_pkl():
    path = os.path.dirname(os.path.realpath(__file__)) + \
    os.sep + "nnmodel" + os.sep + "weights"
    file_name = ""
    for i in os.listdir(path):
        if i.endswith('.pkl') or i.endswith(".pth"):
            file_name = path + os.sep + i
    if file_name == "":    
        raise BaseException("No weight file found")
    return file_name



# ////////////////////////////////////////////////////////////////////
# //                          _ooOoo_                               //
# //                         o8888888o                              //
# //                         88" . "88                              //
# //                         (| ^_^ |)                              //
# //                         O\  =  /O                              //
# //                      ____/`---'\____                           //
# //                    .'  \\|     |//  `.                         //
# //                   /  \\|||  :  |||//  \                        //
# //                  /  _||||| -:- |||||-  \                       //
# //                  |   | \\\  -  /// |   |                       //
# //                  | \_|  ''\---/''  |   |                       //
# //                  \  .-\__  `-`  ___/-. /                       //
# //                ___`. .'  /--.--\  `. . ___                     //
# //              ."" '<  `.___\_<|>_/___.'  >'"".                  //
# //            | | :  `- \`.;`\ _ /`;.`/ - ` : | |                 //
# //            \  \ `-.   \_ __\ /__ _/   .-` /  /                 //
# //      ========`-.____`-.___\_____/___.-`____.-'========         //
# //                           `=---='                              //
# //      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        //
# //            佛祖保佑       永不宕机     永无BUG                   //
# ////////////////////////////////////////////////////////////////////

if __name__ == "__main23__":
    parser = argparse.ArgumentParser(description="Instagram Crawler", usage=usage())
    # parser.add_argument("mode", help="options: [posts, posts_full, profile, profile_script, hashtag]" )
    parser.add_argument("-l", "--level", default='INFO', type=str, help="set the level of log")
    parser.add_argument("-n", "--number", type=int, help="number of returned posts")
    parser.add_argument("-u", "--username", help="instagram's username")
    parser.add_argument("-t", "--tag", help="instagram's tag name")
    parser.add_argument("-o", "--output", help="output file name(json format)")
    parser.add_argument("--debug", default=True, action="store_true")
    parser.add_argument("ip", type=str, help="Ip address of database")

    # prepare_override_settings(parser)
    args = parser.parse_args()
    DBCONFIG['host'] = args.ip
    init_log(level = args.level,\
            filename = "crawler-%s.log"%(time.strftime("%Y%m%d-%H-%M-%S", time.localtime())),\
            filepath="./log/")
    
    log.info('Start to load hashtag from csv file and database')
    tag_coll = Tagset('./keywords/drug_cihui.csv', dbsrc=True)
    tag_coll.tagload()
    print(tag_coll)
    print(type(tag_coll))
    log.info('The size of data we\'re gonna visit is %d', tag_coll.get_size())
    crawl_hashtag(tag_coll, args.debug)

def run_run(user_name, user_pwd, hashtags):
    DBCONFIG['host'] = "157.182.212.97"
    init_log(level = "INFO",\
            filename = "crawler-%s.log"%(time.strftime("%Y%m%d-%H-%M-%S", time.localtime())),\
            filepath="./log/")
    
    log.info('Start to load hashtag from csv file and database')
    tag_coll = Tagset('./keywords/drug_cihui.csv', dbsrc=True)
    # tag_coll.tagload()
    tag_coll.tag_from_text(hashtags)
    log.info('The size of data we\'re gonna visit is %d', tag_coll.get_size())
    crawl_hashtag(tag_coll, True, user_name, user_pwd)
    

if __name__ == "__main__":
    run_run('1233', '432', 'fda')


    # override_settings(args)
    # if args.mode in ["posts", "posts_full"]:
    #     arg_required("username")
    #     output(
    #         get_posts_by_user(
    #             args.username, args.number, args.mode == "posts_full", args.debug
    #         ),
    #         args.output,
    #     )
    # elif args.mode == "profile":
    #     arg_required("username")
    #     output(get_profile(args.username), args.output)
    # elif args.mode == "profile_script":
    #     arg_required("username")
    #     output(get_profile_from_script(args.username), args.output)
    # elif args.mode == "hashtag":
    #     arg_required("tag")
    #     output(
    #         get_posts_by_hashtag(args.tag, args.number or 100, args.debug), args.output
    #     )
    # else:
    #     usage()
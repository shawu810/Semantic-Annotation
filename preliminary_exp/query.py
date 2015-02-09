import MySQLdb
import os
import cPickle as pickle
from credential import *


class Point:
    def __init__(self, lat, lon, timestamp, content):
        self.lat = lat
        self.lon = lon
        self.timestamp = timestamp
        self.content   = content

def parse_one_query_result(all_tweets):
    point_list  = list()
    for one_result in all_tweets:
        tweet_id   = one_result[0]
        timestamp  = one_result[1]
        user_id    = one_result[2]
        pl         = one_result[3]
        lon        = one_result[4]
        lat        = one_result[5]
        content    = one_result[6]
        PP         = Point(lat, lon, timestamp, content)
        point_list.append(PP)
    return point_list

def parse_one_query_result_by_check_in(all_tweets):
    check_in_point_list      = list()
    none_check_in_point_list = list()
    for one_result in all_tweets:
        tweet_id   = one_result[0]
        timestamp  = one_result[1]
        user_id    = one_result[2]
        pl         = one_result[3]
        lon        = one_result[4]
        lat        = one_result[5]
        content    = one_result[6]
        PP         = Point(lat, lon, timestamp, content)
        if 'I m at' in content and 'http://' in content:
            check_in_point_list.append(PP)
        else:
            none_check_in_point_list.append(PP)
    return check_in_point_list, none_check_in_point_list


def query_user(user_id, cursor):
    query  = "SELECT * FROM raw_tweets WHERE user_id = " + str(user_id)
    try:
        cursor.execute(query)
    except Exception as e:
        print "ERROR: " + query
    return cursor.fetchall()

def query_location_entropy(user_id, cursor):
    query  = "SELECT location_entropy FROM TweetUser WHERE user_id ={}".format(user_id)
    try:
        cursor.execute(query)
    except Exception as e:
        print "ERROR: "+ query
    return cursor.fetchall()[0][0]


class DB:
    def __init__(self, usermap=dict(), gendermap = {'male':[],'female':[]}, racemap = {'black':[],'white':[],'asian':[],'hispanic':[]}):
        self.usermap   = usermap
        self.gendermap = gendermap        
        self.racemap   = racemap


def parsing_label_file(filename):
    infor = DB()
    for oneline in open(filename):
        line_set = oneline.rstrip('\n').split(';')
        if 'user' in oneline:
            continue
        userid   = line_set[0].replace(" ","").replace("\t","")
        race     = line_set[1]
        gender   = line_set[2]
        if userid not in infor.usermap:
            infor.usermap[userid] = (race, gender)
        if gender in infor.gendermap:
            infor.gendermap[gender].append(userid)
        if race in infor.racemap:
            infor.racemap[race].append(userid)
    return infor



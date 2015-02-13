import MySQLdb
import os
import cPickle as pickle 
from query import *
from crawling_4sq import * 
from DB_credential import *
######################################################################
# This program does the following:
# 1. get raw mobility records given user id from databases
# 2. get raw foursqaure respone from 4sq api given user mobility records
######################################################################

def split_user_tweets(infor, cursor):
    user_checkins   = dict()
    user_locations  = dict()
    for one_user in infor.usermap:
        if infor.usermap[one_user][0] == '' and infor.usermap[one_user][1]=='':
            continue
        print one_user
        raw_tweets    = query_user(one_user,cursor)
        checkin_list, point_list = parse_one_query_result_by_check_in(raw_tweets)
        user_checkins[one_user]  = checkin_list
        user_locations[one_user] = point_list
    return user_checkins, user_locations
##################################################################################################################################
#Plot density map

def plot_density_map(point_list, path):
    header = "visual/header.html"
    footer = "visual/footer.html"
    output_file = open(header,'r').read()
    points = ""
    for point in point_list:
        new_p = "new google.maps.LatLng({},{}),".format(str(point.lat), str(point.lon))
        points += new_p
    points.rstrip(',')
    output_file += points + open(footer,'r').read()
    f = open(path,'w')
    f.write(output_file)
    f.close()

def plot_density_map_for_all(user_c, user_l, path):
    user_list = user_c.keys()
    for one_user in user_list:
        path2c = path+one_user+"_c.html"
        path2l = path+one_user+"_l.html"
        plot_density_map(user_c[one_user], path2c)
        plot_density_map(user_l[one_user], path2l)

######################################################################
# Annotate by category 
#  Functions in this section needs to be deleted
#####################################################################
def parse_content_for_venue(content):
    index  = content.find('(')
    content= content[0:index-1].replace('I m at ',"")    
    return content

def get_responses_of_a_user(point_list):
    responeses  = list()
    for point in point_list:
        r = fetch_4sqPOI(point)
        responeses.append(r)
    return responeses

def dump_list(users, path, appending=''):
    for one_user in users.keys():
        print one_user
        if one_user in finished_list:
            print "already finished skip"
            continue
        r = get_responses_of_a_user(users[one_user])
        print len(r),len(users[one_user])
        with open(path+one_user+'_json_{}.pickle'.format(appending),'w') as f:
            pickle.dump(r,f)



def annotate_checkins_all_dump(users, path):
    for one_user in users.keys():
        print one_user
        if one_user in finished_list:
            print "already finished skip"
            continue
        result,r = annotate_checkins_by_cat(users[one_user],catmap)
        freq_map[one_user] = result 
        with open(path+one_user+'_json.pickle','w') as f:
            pickle.dump(r,f)
    return freq_map

def annotate_locations_all_dump(users, catmap, path):
    freq_map     = dict()
    for one_user in users.keys():
        print one_user
        #if one_user in finished_list:
        #    print "already finished skip, l"
        #    continue
        freq_map, ann_list, r = annotate_locations_by_cat(users[one_user],catmap)
        freq_map[one_user] = freq_map 
        with open(path+one_user+'_freqmap_l.pickle','w') as f:
            pickle.dump([freq_map, ann_list], f)
        with open(path+one_user+'_json_l.pickle','w') as f:
            pickle.dump(r,f)
    return freq_map



#path2labels = '/home/feiwu/Dropbox/Research/POI/preliminary_experiment/user_labels'
path2labels  = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/user_label_NYC'
path2densityfigures = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/density_figures/'
path2data   = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/data/'
path2records   = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/NYCdata/finished'
path2data   = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/NYCdata/'

global cursor
global finished_list
finished_list = [x.rstrip('\n') for x in open(path2records,'r').readlines()]
#finished_list = []
PROCESS_RAW_LABELS = False
PLOT_DENSITY       = False  
STORE_RAW          = True
db_connection = MySQLdb.connect(hostname,user,passwd,db)
cursor        = db_connection.cursor()
infor         = parsing_label_file(path2labels)
if PROCESS_RAW_LABELS:
    user_c,user_l = split_user_tweets(infor, cursor)
    with open(path2data+'labeled_user_data.pickle','w') as f:
        pickle.dump([user_c,user_l], f)
else:
    with open(path2data+'labeled_user_data.pickle','r') as f:
        user_c, user_l = pickle.load(f)

dump_list(user_c,path2data,'')
dump_list(user_l,path2data,'l')


sys.exit()

if PLOT_DENSITY:
    plot_density_map_for_all(user_c, user_l, path2densityfigures)

#if GET_CAT_MAP_4SQ:
#    r       = fetch_categories_tree()
#    cat_map = parse_rCat(r)
#    with open(path2catmap,'w') as f:
#        pickle.dump(cat_map,f)
#else:
#    with open(path2catmap,'r') as f:
#        cat_map = pickle.load(f)

#with open(path2data+'checkin_freqmap.pickle','w') as f:
#    pickle.dump(all_checkin_freqmap, f)

#all_location_freqmap = annotate_locations_all_dump(user_l, cat_map, path2data)



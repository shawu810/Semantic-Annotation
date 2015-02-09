import MySQLdb
import cPickle as pickle
import os
from query import *
from crawling_4sq import *
import numpy as np

#### number of checkins ###########
def dump_by_vector(users_freq_map,userlist ):    
    matrix = list()
    for one_user in userlist:
        vec   = [0]*10
        ff    = False
        freq_map = users_freq_map[one_user]
        for onecat in major_cats:
            if onecat in freq_map:
                vec[major_cats[onecat]] = freq_map[onecat]
                ff = True
        if ff:
            matrix.append(vec)
    return matrix

path2labels = '/home/feiwu/Dropbox/Research/POI/preliminary_experiment/user_labels'
path2densityfigures = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/density_figures/'
path2data_c   = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/annotated_cat_data/'
path2catmap = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/data/4sq_cat.pickle'

global finished_list, major_cats
infor       = parsing_label_file(path2labels)
finished_list = [x.split('_')[0] for x in open(path2data_c+'finished_file','r').readlines()]
finished_list = [x for x in finished_list if x != 'finished']
major_cats   = {'Food':0,
                'Travel':1,
                'Arts & Entertainment':2,
                'Outdoors & Recreation':3,
                'College & Education':4,
                'Nightlife':5,
                'Professional':6,
                'Shops':7,
                'Residence':8}
c_appending  = '_freqmap_c.pickle'
l_appending  = '_freqmap_l.pickle'
db_connection = MySQLdb.connect(hostname,user,passwd,db)
cursor        = db_connection.cursor()

RE_WRT_CAT_MATRIX = False

users_freq_map = dict()
for one_user in finished_list:
    with open(path2data_c+one_user+'_freqmap_c.pickle') as f:
        users_freq_map[one_user] =  pickle.load(f)
#sys.exit()
if RE_WRT_CAT_MATRIX:
    matrix =  dump_by_vector(users_freq_map, infor.gendermap['female'])
    np.savetxt('female_wrt_cat', matrix)
    matrix =  dump_by_vector(users_freq_map, infor.gendermap['male'])
    np.savetxt('male_wrt_cat', matrix)

    matrix =  dump_by_vector(users_freq_map, infor.racemap['black'])
    np.savetxt('black_wrt_cat', matrix)
    matrix =  dump_by_vector(users_freq_map, infor.racemap['white'])
    np.savetxt('white_wrt_cat', matrix)

location_entropy_map = dict()
for user in finished_list:
    try:
        re = query_location_entropy(user,cursor)
    except Exception as e:
        print e
        continue
    location_entropy_map[user] = re
    print user + "  " + str(re) 

def dump_entropy(location_entropy_map, user_list):
    vec  = list()
    for u in user_list:
        if u in location_entropy_map:
            vec.append(float(location_entropy_map[u]))
    return vec

male_vec  = dump_entropy(location_entropy_map, infor.gendermap['male'])
female_vec= dump_entropy(location_entropy_map, infor.gendermap['female'])

black_vec  = dump_entropy(location_entropy_map, infor.racemap['black'])
white_vec= dump_entropy(location_entropy_map, infor.racemap['white'])


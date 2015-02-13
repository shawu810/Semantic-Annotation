import cPickle as pickle
from query import *
from crawling_4sq import *
import numpy as np

#####################################################
# This program is supposed to do the following:
#   - read r respone for trajectory point of a user and parse into data-label matrix
####################################################


def get_annotation_list_all(finished_list, user_c, catmap):   
    all_list =  dict()
    for one_user in finished_list:
        print one_user
        with open(path2data+one_user+raw_response) as f:
            user_r = pickle.load(f)
        user_cc    = user_c[one_user]
        annotation_list = annotate_checkins_by_catmap(user_r,user_cc, catmap)
        all_list[one_user] = annotation_list
    return all_list

def hist_cats(one_list):
    hist = dict()
    for one in one_list:
        if one not in hist:
            hist[one] = 0
        hist[one] +=    1
    return hist

def get_all_hists(all_list):
    freq_map_dict = dict()
    all_cats_index= dict()
    count  = 0
    for one in all_list:
        freq_map_dict[one] = hist_cats(all_list[one])
        for onekey in freq_map_dict[one].keys():
            if onekey not in all_cats_index:
                all_cats_index[onekey] = count
                count                 += 1
    return freq_map_dict, all_cats_index

def dump_by_vector(users_freq_map, userlist , major_cats ):    
    matrix = list()
    for one_user in userlist:
        vec   = [0]* ( len(major_cats.keys()) + 1)
        ff    = False
        freq_map = users_freq_map[one_user]
        for onecat in major_cats:
            if onecat in freq_map:
                vec[major_cats[onecat]] = freq_map[onecat]
                ff = True
        if ff:
            matrix.append(vec)
    return matrix

def dump_by_vector_with_labels(users_freq_map, userlist, major_cats, infor):
    matrix = list()
    number_of_labels = 2  ## gender and race
    result_u_list = list()
    index_map = ['']*(len(major_cats.keys())+ number_of_labels)
    ff = False
    index_map[len(index_map)-1] = 'gender'
    index_map[len(index_map)-2] = 'race'
    for onekey in major_cats:
        index_map[major_cats[onekey]] = onekey
    for one_user in userlist:
        vec = [0]*(len(major_cats.keys())+ number_of_labels)
        freq_map = users_freq_map[one_user]
        for onecat in major_cats:
            if onecat in freq_map:
                vec[major_cats[onecat]] = freq_map[onecat]
                ff = True
        if  one_user in infor.gendermap['male']: 
            vec[len(vec)-1] = 1
        elif one_user in infor.gendermap['female']:
            vec[len(vec)-1] = -1
        if one_user in infor.racemap['white']:
            vec[len(vec)-2] = 1
        elif one_user in infor.racemap['black']:
            vec[len(vec)-2] = -1
        if ff:
            matrix.append(vec)
            result_u_list.append(one_user)
    return matrix, index_map, result_u_list


path2data = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/data/'
path2labels = '/home/feiwu/Dropbox/Research/POI/preliminary_experiment/user_labels'

#finished_list = [x.split('_')[0] for x in open(path2data+'finished_file','r').readlines()]
#finished_list = [x for x in finished_list if x != 'finished']

raw_response = '_json.pickle'
with open(path2data+'labeled_user_data.pickle','r') as f:
    user_c, user_l = pickle.load(f)

CAT_MAP_FLAG = 1 # 1 for sub  cat, 2 cat

finished_list = user_c.keys()
r       = fetch_categories_tree()
if CAT_MAP_FLAG == 1:
    cat_map = parse_r_subCat(r)
    out = 'matrix_checkins.pickle'
elif CAT_MAP_FLAG == 2:
    cat_map = parse_rCat(r)
    out = 'matrix_checkins_cat.pickle'
infor   = parsing_label_file(path2labels)

VI_FLAG  = False
ANNOTATE = True
if ANNOTATE:
    all_list = get_annotation_list_all(finished_list, user_c, cat_map)
    users_freq_map, cat_index = get_all_hists(all_list)
    with open(path2data+'annotated_checkins_result.pickle','w') as f:
        pickle.dump([users_freq_map, cat_index], f)
else:
    with open(path2data+'annotated_checkins_result.pickle') as f:
        users_freq_map, cat_index = pickle.load(f)

if VI_FLAG:
    matrix =  dump_by_vector(users_freq_map, infor.gendermap['female'], cat_index)
    np.savetxt('female_wrt_sub_cat', matrix)
    matrix =  dump_by_vector(users_freq_map, infor.gendermap['male'], cat_index)
    np.savetxt('male_wrt_sub_cat', matrix)
    matrix =  dump_by_vector(users_freq_map, infor.racemap['black'], cat_index)
    np.savetxt('black_wrt_sub_cat', matrix)
    matrix =  dump_by_vector(users_freq_map, infor.racemap['white'], cat_index)
    np.savetxt('white_wrt_sub_cat', matrix)

matrix, index_map, result_u_list = dump_by_vector_with_labels(users_freq_map, users_freq_map.keys(), cat_index, infor)
with open(path2data+out,'w') as f:
    pickle.dump([matrix, index_map, result_u_list],f) 

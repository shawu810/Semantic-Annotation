import cPickle as pickle
from query import *
from crawling_4sq import *
import numpy as np

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
        #try:
        freq_map = users_freq_map[one_user]
        #except Exception as e:
        #    print e
        #    continue
        for onecat in major_cats:
            if onecat in freq_map:
                vec[major_cats[onecat]] = freq_map[onecat]
                ff = True
        if ff:
            matrix.append(vec)
    return matrix


path2data = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/data/'
path2labels = '/home/feiwu/Dropbox/Research/POI/preliminary_experiment/user_labels'

#finished_list = [x.split('_')[0] for x in open(path2data+'finished_file','r').readlines()]
#finished_list = [x for x in finished_list if x != 'finished']

c_appending  = '_freqmap_c.pickle'
raw_response = '_json.pickle'
with open(path2data+'labeled_user_data.pickle','r') as f:
    user_c, user_l = pickle.load(f)

finished_list = user_c.keys()
r       = fetch_categories_tree()
cat_map = parse_r_subCat(r)
infor   = parsing_label_file(path2labels)



all_list = get_annotation_list_all(finished_list, user_c, cat_map)
users_freq_map, cat_index = get_all_hists(all_list)

matrix =  dump_by_vector(users_freq_map, infor.gendermap['female'], cat_index)
np.savetxt('female_wrt_sub_cat', matrix)
matrix =  dump_by_vector(users_freq_map, infor.gendermap['male'], cat_index)
np.savetxt('male_wrt_sub_cat', matrix)

matrix =  dump_by_vector(users_freq_map, infor.racemap['black'], cat_index)
np.savetxt('black_wrt_sub_cat', matrix)
matrix =  dump_by_vector(users_freq_map, infor.racemap['white'], cat_index)
np.savetxt('white_wrt_sub_cat', matrix)



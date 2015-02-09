import MySQLdb
import os
import cPickle as pickle 
from query import *
from crawling_4sq import * 



def split_user_tweets(infor, cursor):
    user_checkins   = dict()
    user_locations  = dict()
    for one_user in infor.usermap:
        if infor.usermap[one_user][0] == 'na' and infor.usermap[one_user][1]=='na':
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

def parse_content_for_venue(content):
    index  = content.find('(')
    content= content[0:index-1].replace('I m at ',"")    
    return content
        
    

def annotate_locations_by_cat(point_list, catmap):
    cat_freq_map = {'others':0}
    key_counter  = 1
    counter_max  = 4
    list_of_annotation = list()
    responeses   = list()
    for point in point_list:
        try:
            r = fetch_4sqPOI(point, key_counter)
            if r == -1:
                print "switch new key"
                key_counter = (key_counter+1)%counter_max
                if key_counter == 0:
                    time.sleep(600)
                r = fetch_4sqPOI(point, key_counter)
        except Exception as e:
            print e
        try:
            name_list,id_list,lat_list,lon_list, cat_list= parse_rPOI(r)
        except Exception as e:
            print "ERROR-annotate_l_by_cat: " 
            print e
            print r
            continue
        number_of_query_result = len(name_list)
        if len(cat_list) == 0:
            continue
        cat = cat_list[0]
        if cat in catmap:
            cat = catmap[cat]
            if cat not in cat_freq_map:
                cat_freq_map[cat] = 0
            cat_freq_map[cat] += 1
        else:
            cat_freq_map['others'] +=1
            print "T:" + point.content
            print "Matched: " + uni2str(name_list[0])+"| Cat: " + cat
        list_of_annotation.append([cat, point.content, point.lat, point.lon, point.timestamp])
        responeses.append(r)
    return cat_freq_map, list_of_annotation, responeses
import time
def annotate_checkins_by_cat(point_list, catmap):
    cat_freq_map = {'others':0}
    key_counter  = 0
    counter_max  = 4
    responeses   = list()
    for point in point_list:
        try:
            r = fetch_4sqPOI(point, key_counter)
            if r == -1:
                print "switch new key"
                key_counter = (key_counter+1)%counter_max
                if key_counter%counter_max == 0 and key_counter != 0:
                    time.sleep(600)
                r = fetch_4sqPOI(point, key_counter)
        except Exception as e:
            print e
            continue
        try:
            name_list,id_list,lat_list,lon_list, cat_list= parse_rPOI(r)
        except Exception as e:
            print "ERROR-annotate_c_by_cat: " 
            print e
            continue
        number_of_query_result = len(name_list)
        for i in range(number_of_query_result):
            if normLCSS(uni2str(name_list[i]), parse_content_for_venue(point.content)) > 0.7:
                cat = cat_list[i]
                if cat in catmap:
                    cat = catmap[cat]
                    if cat not in cat_freq_map:
                        cat_freq_map[cat] = 0
                    cat_freq_map[cat] += 1
                    break
                else:
                    cat_freq_map['others'] +=1
                    break
            else:
                if i == number_of_query_result-1:
                    cat_freq_map['others'] += 1
        responeses.append(r)
    return cat_freq_map, responeses

def annotate_checkins_all_dump(users, catmap, path):
    freq_map     = dict()
    for one_user in users.keys():
        print one_user
        if one_user in finished_list:
            print "already finished skip"
            continue
        result,r = annotate_checkins_by_cat(users[one_user],catmap)
        freq_map[one_user] = result 
        with open(path+one_user+'_freqmap_c.pickle','w') as f:
            pickle.dump(result, f)
        with open(path+one_user+'_json.pickle','w') as f:
            pickle.dump(r,f)
    return freq_map

def annotate_locations_all_dump(users, catmap, path):
    freq_map     = dict()
    for one_user in users.keys():
        print one_user
        if one_user in finished_list:
            print "already finished skip, l"
            continue
        freq_map, ann_list, r = annotate_locations_by_cat(users[one_user],catmap)
        freq_map[one_user] = freq_map 
        with open(path+one_user+'_freqmap_l.pickle','w') as f:
            pickle.dump([freq_map, ann_list], f)
        with open(path+one_user+'_json_l.pickle','w') as f:
            pickle.dump(r,f)
    return freq_map



path2labels = '/home/feiwu/Dropbox/Research/POI/preliminary_experiment/user_labels'
path2densityfigures = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/density_figures/'
path2data   = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/data/'
path2catmap = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/data/4sq_cat.pickle'
path2records   = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/data/finished_file'

finished_list = [x.split('_')[0] for x in open(path2records,'r').readlines()]
print finished_list


global finished_list
#finished_list= ['7166062','8241232','14441659','15440426','23857378','33859210','180449593','583060976','355203','10163682',
#                '34469882', '544781217','28723928','36530562','22553672','17749590','16020567','17947596','233779408','80044220','39377605','18547608','66090606','166544789','40851186','15391338','14170486','49879270','77803198','623260867','16712144','14433924','19321576','36544865','67212491','41042519']
global cursor
finished_list = [x.split('_')[0] for x in open(path2records,'r').readlines()]
print finished_list


PROCESS_RAW_LABELS = False
PLOT_DENSITY       = False  
GET_CAT_MAP_4SQ    = False 
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

if PLOT_DENSITY:
    plot_density_map_for_all(user_c, user_l, path2densityfigures)

if GET_CAT_MAP_4SQ:
    r       = fetch_categories_tree()
    cat_map = parse_rCat(r)
    with open(path2catmap,'w') as f:
        pickle.dump(cat_map,f)
else:
    with open(path2catmap,'r') as f:
        cat_map = pickle.load(f)

#all_checkin_freqmap = annotate_checkins_all_dump(user_c,cat_map, path2data)
#with open(path2data+'checkin_freqmap.pickle','w') as f:
#    pickle.dump(all_checkin_freqmap, f)

#all_location_freqmap = annotate_locations_all_dump(user_l, cat_map, path2data)



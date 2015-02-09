import MySQLdb
import os
import cPickle as pickle
from query import *
####################################################
# plot pin points on google map with infor window
#####################################################
def construct_google_map_point(lat, lon):
    return "new google.maps.LatLng({0},{1})".format(str(lat), str(lon))

def read_in_active_user(filename):
    user_list = list()
    for oneline in open(filename, 'r'):
        line_set = oneline.split('\t')
        user_list.append(int(line_set[0]))
    return user_list

def construct_point_var(point_list):
    point = point_list[0]
    lat   = point.lat
    lon   = point.lon
    var_out= """var point   = {0}; """.format(construct_google_map_point(lat, lon))
    return var_out
def construct_location_variable(point_list):
    center_string = ""
    for site in point_list:     
        lat      = site.lat
        lon      = site.lon
        content  = site.content
        timestamp= site.timestamp
        center_string += """["time: {}<br> {} ",{},{}],""".format(timestamp,content,str(lat),str(lon))
    center_string = center_string.rstrip(',')
    return "var locations = [{}];".format(center_string)

def load_template(path):
    return ''.join(open(path,'r').readlines())

def plot_sites(list_of_sites, path = 'test'):
    html        = load_template(path2template).replace('####', construct_point_var(list_of_sites)+ construct_location_variable(list_of_sites))
    f           = open(path+'.html','w')
    f.write(html)
    f.close()

   
active_user_list = 'active_user'

global cursor,path2template
path2template = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/visual/template.html'
db_connection  = MySQLdb.connect(hostname, user, passwd, db)
cursor         = db_connection.cursor()


user_list        = read_in_active_user(active_user_list)
for one_user in user_list:
    all_tweets = query_user(one_user, cursor)
    point_list = parse_one_query_result(all_tweets)
    plot_sites(point_list, path = 'user_visual/{}'.format(str(one_user)))

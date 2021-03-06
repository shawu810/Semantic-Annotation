import requests
import time
import json
import unicodedata
import cPickle as pickle
from fsq_credential import key_counter,fsq_ClientID_set,fsq_ClientSercet_set
##############################################################################
# Utility
#############################################################################
def normLCSS(a,b):
    a = a.replace(" ", "")
    b = b.replace(" ", "")
    m = len(a)
    n = len(b)
    ll= max([m,n])
    matrix = [[0 for x in range(n+1)] for x in range(m+1)]
    for i in range(1,m+1):
        for j in range(1,n+1):
            ii = i-1
            jj = j-1
            if a[ii].lower() == b[jj].lower():
                matrix[i][j] = matrix[i-1][j-1] + 1
            else:
                matrix[i][j] = max([matrix[i-1][j], matrix[i][j-1]])
    return float (matrix[m][n])/ll



def uni2str(uni):
    return unicodedata.normalize('NFKD', uni).encode('ascii','replace')
###############################################################################


def fetch_4sqPOI(point):
    lat = point.lat
    lon = point.lon
    status_code = 0
    global key_counter
    error_count  = 0
    while status_code != 200:
        fsq_ClientID     = fsq_ClientID_set[key_counter]     #"AQIGCLQOQLSFWS2C24WSKBTUDCRIAYZ1C5VBGFUJ3CTJQICG"
        fsq_ClientSercet = fsq_ClientSercet_set[key_counter] #"JEBHXVQ1YYADIC3IRCKDNJFZX4AM24NAVZTCQ2IVT0U3RT2A"
        fsq_rest         = "https://api.foursquare.com/v2/venues/search?ll="+str(lat)+","+str(lon)+"&limit=20&intent=checkin&radius=50&client_id="+fsq_ClientID+"&client_secret="+fsq_ClientSercet+"&v=20150203"
        try:
            r = requests.get(fsq_rest)
        except Exception as e:
            error_count += 1
            print error_count
            print e
            return []
        status_code = r.status_code
        if status_code == 403:
            print "switching keys "
            key_counter = (key_counter+1)%len(fsq_ClientID_set)
            time.sleep(60)
            continue
        if status_code != 200:
            print r.status_code
        if status_code == 500:
            print "sever problem"
            time.sleep(60)
        if status_code == 404:
            print "not found"
            return r
    return r

def fetch_categories_tree():
    fsq_ClientID     = "AQIGCLQOQLSFWS2C24WSKBTUDCRIAYZ1C5VBGFUJ3CTJQICG"
    fsq_ClientSercet = "JEBHXVQ1YYADIC3IRCKDNJFZX4AM24NAVZTCQ2IVT0U3RT2A"
    fsq_rest         = "https://api.foursquare.com/v2/venues/categories?client_id="+fsq_ClientID+"&client_secret="+fsq_ClientSercet+"&v=20150203"
    r = requests.get(fsq_rest)
    while r.status_code == 403:
        print 'limit reached'
        time.sleep(3600)
        r = requests.get(fsq_rest)
    return r

   
def parse_rPOI(r):
    rjson = r.json()['response']['venues']
    name_list = [x['name'] for x in rjson]
    id_list   = [x['id']   for x in rjson]
    lat_list  = [x['location']['lat'] for x in rjson]
    lon_list  = [x['location']['lng'] for x in rjson]
    cat_list  = [','.join([uni2str(y['shortName']) for y in x['categories']]) for x in rjson]
    return name_list,id_list,lat_list,lon_list,cat_list

def parse_rCat(r):
    rjson   = r.json()['response']['categories'] # all categoriesa
    cat_map = dict()
    for one_cat in rjson:
        cat_name = uni2str(one_cat['shortName'])
        if cat_name not in cat_map:
            print cat_name
            cat_map[cat_name] = cat_name
        for one_sub_cat in one_cat['categories']:
            sub_cat_name = uni2str(one_sub_cat['shortName'])
            if sub_cat_name not in cat_map:
                cat_map[sub_cat_name] = cat_name
            for one_sub_sub_cat in one_sub_cat['categories']:
                sub_sub_cat_name = uni2str(one_sub_sub_cat['shortName'])
                if sub_sub_cat_name not in cat_map:
                    cat_map[sub_sub_cat_name] = cat_name
    return cat_map

def parse_r_subCat(r):   
    rjson   = r.json()['response']['categories'] # all categoriesa
    cat_map = dict()
    for one_cat in rjson:
        cat_name = uni2str(one_cat['shortName'])
        if cat_name not in cat_map:
            print cat_name
            cat_map[cat_name] = cat_name
        for one_sub_cat in one_cat['categories']:
            sub_cat_name = uni2str(one_sub_cat['shortName'])
            if sub_cat_name not in cat_map:
                cat_map[sub_cat_name] = sub_cat_name
            for one_sub_sub_cat in one_sub_cat['categories']:
                sub_sub_cat_name = uni2str(one_sub_sub_cat['shortName'])
                if sub_sub_cat_name not in cat_map:
                    cat_map[sub_sub_cat_name] = sub_cat_name
    return cat_map

def annotate_checkins_by_catmap(r_list, point_list, catmap):
    catmap['']     = 'unknown'
    n_points       = len(r_list)
    if len(r_list) != len(point_list):
        print "length of the lists mis-matched! "
        return []
    annotated_list = list()
    for i in range(len(r_list)):
        point = point_list[i]
        r     = r_list[i]
        try:
            name_list, id_list, lat_list, lon_list, cat_list = parse_rPOI(r)
        except Exception as e:
            print e
            #annotated_list.append('unknown')   
            continue
        number_of_query_result = len(name_list)
        for i in range(number_of_query_result):
            if normLCSS(uni2str(name_list[i]), parse_content_for_venue(point.content)) > 0.6:
                if cat_list[i] == '':
                    continue
                cat = catmap[cat_list[i]]  # translate categories
                annotated_list.append(cat)
                break
            if i == number_of_query_result-1:
                pass
                #annotated_list.append('unknown')
                #print name_list
                #print parse_content_for_venue(point.content)
                #print normLCSS(uni2str(name_list[i]), parse_content_for_venue(point.content))
    return annotated_list
 

def parse_content_for_venue(content):
    index  = content.find('(')
    content= content[0:index-1].replace('I m at ',"")    
    return content
        
               

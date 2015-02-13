import twitter
import cPickle as pickle
import sys
import time
consumer_key1        = 'xwEkbpI0kswT7WvhizwzoqHPV'                 #'cbjHS21OkO7GY11S2kPwlvOHU'
consumer_secret1     = 'fvCcg9Wz201GnEuOfYC3TyY5yc914bdRBfzi07NzP6pLmVPLqX'                 #'JBDEO5EouelnZ7TecDFmIlbqqXca53U3VGV85lw9zrYKsTo'
access_token1        = '282126262-0QHPibt4grj4RSoBPXFr1sGdBCMTBIykqWg6WXny'
access_token_secret1 = 'LMs0xDZHuEZEBVYK8hAY2zfP9HR4wLDC9HxdhTzzjuQ5X'
api = twitter.Api(consumer_key=consumer_key1,
                  consumer_secret=consumer_secret1,
                  access_token_key=access_token1,
                  access_token_secret=access_token_secret1)

def get_user_object_from_twitter(user_list):
    user_object_dict = dict()
    while len(user_list)>0:
        one_user = user_list[0]
        print one_user
        try:
            user = api.GetUser(user_id = one_user)
        except Exception as e:
            print e
            if e[0][0]['code'] == 88:
                time.sleep(900)  
                continue
        d    = user.AsDict()
        user_object_dict[one_user] = d
        user_list.pop(0)
    return user_object_dict

def dump_select_attributes(object_dict, name_list, filename):
    f = open(filename, 'w')
    header = ','.join(name_list)
    f.write(header+'<br>\n')
    for one_user in object_dict.keys():
        u_object = object_dict[one_user]
        aline    = ''
        for one in name_list:
            if one not in u_object:
                aline+= ','
                continue
            if one == 'url':
                aline+= '<a href={}> {}</a>,'.format(u_object[one],format(u_object[one]))
                continue
            aline+= str(u_object[one]) +','
        if 'screen_name' in name_list:
            aline+= '<a href=https://twitter.com/{}> {}</a>'.format(u_object['screen_name'], u_object['screen_name'])
        f.write(aline+'<br>\n')
    f.close()

path2_userlist  = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/active_user'
path2_userobject= '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/user_raw_data/NYC_users_raw.pickle'

FROM_TWITTER = False

user_list      = [x.split('\t')[0] for x in open(path2_userlist,'r').readlines()]


if FROM_TWITTER:
    user_object_dict = get_user_object_from_twitter(user_list)   
    with open(path2_userobject, 'w') as f:
        pickle.dump(user_object_dict, f)
else:
    with open(path2_userobject, 'r') as f:
        user_object_dict = pickle.load(f)

dump_select_attributes(user_object_dict, ['id','screen_name','url'], 'user_label_NYC.html')


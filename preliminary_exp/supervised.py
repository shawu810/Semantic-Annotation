import sklearn
import numpy as np
import cPickle as pickle
import os
import pydot

from sklearn.datasets import load_iris
from sklearn import tree

def remove_non_label(target, matrix):
    index = np.logical_and(target!=0, np.sum(matrix, axis=1)!=0)
    return np.array(matrix[index,:], dtype='float'), (target[index] +1 )/2



path2data = '/home/feiwu/Desktop/MobilityProfile/preliminary_exp/data/'
data_file = 'matrix_checkins.pickle'
#data_file = 'matrix_checkins_cat.pickle'
with open(path2data+data_file) as f:
    matrix,index_map, result_u_list = pickle.load(f)
num_m = np.array(matrix)
np.random.shuffle(num_m)
data        = num_m[:,0:-2]
race_target = num_m[:,-2] 
gender_target = num_m[:,-1]

gender_data, gender_label   = remove_non_label(gender_target, data)

clf = tree.DecisionTreeClassifier()
clf = clf.fit(gender_data, gender_label)
from sklearn.externals.six import StringIO
dot_data = StringIO()
tree.export_graphviz(clf, out_file=dot_data)
graph = pydot.graph_from_dot_data(dot_data.getvalue())
graph.write_pdf('gender.pdf')


### SVM stuff start here ##########

from sklearn import svm
from sklearn.cross_validation import KFold, ShuffleSplit
from numpy import array, mean
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV
from sklearn.preprocessing import normalize
from sklearn.metrics import classification_report
from sklearn.decomposition import PCA
pca = PCA(n_components = 5)

kf = KFold(len(gender_label),5)
#kf  = ShuffleSplit(n= len(gender_data), n_iter= 5, test_size = 0.2, train_size= 0.8)
for train_idx, test_idx in kf:
    X_train = gender_data[train_idx,:]
    X_test  = gender_data[test_idx,:]
    y_train = gender_label[train_idx]
    y_test  = gender_label[test_idx]
    tunned_parameters = [{'kernel':['rbf'], 'gamma':[1e-2,1e-3,1e-4,1,1e-5],
                         'C': [1e-1,1e-2,1,10,100,1000]}]
    clf = GridSearchCV(svm.SVC(C=1), tunned_parameters, cv = 5, scoring = 'accuracy')
    clf.fit(normalize(X_train), y_train)
    #for params, mean_score, scores in clf.grid_scores_:
    #    print "%0.3f (+/-%0.03f) for % r" % (mean_score, scores.std()/2, params)
    y_true_train, y_pred_train = y_train, clf.predict(normalize(X_train))
    y_true, y_pred = y_test, clf.predict(normalize(X_test))
    print "Train error: "
    print classification_report(y_true_train, y_pred_train)
    print "Test error: "
    print classification_report(y_true, y_pred)
    print "###########################################################################################################"
print "PCAAAA starts here"
kf = KFold(len(gender_label),5)
#kf  = ShuffleSplit(n= len(gender_data), n_iter= 5, test_size = 0.2, train_size= 0.8)
for train_idx, test_idx in kf:
    X_train = gender_data[train_idx,:]
    X_test  = gender_data[test_idx,:]
    y_train = gender_label[train_idx]
    y_test  = gender_label[test_idx]
    #X_train, X_test, y_train, y_test = cross_validation.train_test_split(gender_data,gender_label, test_size = 0.3)
    tunned_parameters = [{'kernel':['rbf'], 'gamma':[1e-2,1e-3,1e-4,1,1e-5],
                         'C': [1e-1,1e-2,1,10,100,1000]}]
    clf = GridSearchCV(svm.SVC(C=1), tunned_parameters, cv = 5, scoring = 'accuracy')
    pca.fit(normalize(X_train))
    clf.fit(pca.transform(normalize(X_train)), y_train)
    #for params, mean_score, scores in clf.grid_scores_:
    #    print "%0.3f (+/-%0.03f) for % r" % (mean_score, scores.std()/2, params)
    y_true_train, y_pred_train = y_train, clf.predict(pca.transform(normalize(X_train)))
    y_true, y_pred = y_test, clf.predict(pca.transform(normalize(X_test)))
    print "Train error: "
    print classification_report(y_true_train, y_pred_train)
    print "Test error: "
    report = classification_report(y_true, y_pred)
    print classification_report(y_true, y_pred)
    print "###########################################################################################################"

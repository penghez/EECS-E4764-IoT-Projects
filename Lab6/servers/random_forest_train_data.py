from sklearn.ensemble import RandomForestClassifier
import letter_lists
from sklearn.externals import joblib

train = letter_lists.train
letters = ['C', 'O', 'L', 'U', 'M', 'B', 'I', 'A']
# test = data1.test
label = []
for i in range(len(train)):
	label.append(letters[i // 20])

# clf = RandomForestClassifier(n_estimators = 100, max_depth = 20, random_state =2)
clf = RandomForestClassifier(n_estimators = 100)

clf.fit(train,label)
joblib.dump(clf,"train_model_forest_new.m")
import pandas as pd
from sklearn import svm, datasets
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report

cv_result_path = r'E:\clinics\cv.csv'

iris = datasets.load_iris()
parameters = {'kernel': ('linear', 'rbf'), 'C': [1, 2, 4], 'gamma': [0.125, 0.25, 0.5, 1, 2, 4]}
svr = svm.SVC()
clf = GridSearchCV(svr, parameters)
clf.fit(iris.data, iris.target)
cv_result = pd.DataFrame.from_dict(clf.cv_results_)
with open(cv_result_path, 'w') as f:
    cv_result.to_csv(f)

print('The parameters of the best model are: ')
print(clf.best_params_)

y_pred = clf.predict(iris.data)
print(classification_report(y_true=iris.target, y_pred=y_pred))
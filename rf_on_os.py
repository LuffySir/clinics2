# -*-coding:utf-8 -*-
import pandas as pd
import numpy as np
import random

from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import roc_curve, auc

from scipy import interp
import matplotlib.pyplot as plt

target_path = r'src\temp.xlsx'

# 所有属性
rf_train_path = r'src\rf_train.csv'
rf_validate_path = r'src\rf_validate.csv'
rf_test_path = r'src\rf_test.csv'

# 选择属性后的
rf_select_train_path = r'src\rf_select_train.csv'
rf_select_validate_path = r'src\rf_select_validate.csv'
rf_select_test_path = r'src\rf_select_test.csv'

# 利用网格法得出结果
cv_result_path = r'src\cv.csv'


def get_train_test(target_path, sheet_name, train_percent,
                   validate_percent, train_path, validate_path, test_path, is_random=False):
    # 是否需要重新随机选取训练集和测试集
    if is_random:
        xls_file = pd.ExcelFile(target_path)
        all_info = xls_file.parse(sheet_name)
        all_info = all_info.fillna(1)

        label_0 = all_info[all_info['OS'] == 0]
        label_1 = all_info[all_info['OS'] == 1]
        label_2 = all_info[all_info['OS'] == 2]
        label_0_num, label_1_num = len(label_0), len(label_1)
        label_2_num = len(label_2)

        # 生成随机序列，前70%作训练集
        random_0 = random.sample([i for i in range(label_0_num)], label_0_num)
        # 训练集
        train_0_lines = random_0[:int(label_0_num*train_percent)+1]
        # 验证集
        validate_0_lines = random_0[int(label_0_num*train_percent)+1:int(label_0_num*(train_percent+validate_percent))+1]
        print('验证集标签为0的数量', len(validate_0_lines))
        # 测试集
        test_0_lines = random_0[int(label_0_num*(train_percent+validate_percent))+1:]
        print('测试集标签为0的数量', len(test_0_lines))

        random_1 = random.sample([i for i in range(label_0_num, label_0_num+label_1_num)], label_1_num)
        train_1_lines = random_1[:int(label_1_num*train_percent)+1]
        validate_1_lines = random_1[int(label_1_num*train_percent)+1:int(label_1_num*(train_percent+validate_percent))+1]
        print('验证集标签为1的数量', len(validate_1_lines))
        test_1_lines = random_1[int(label_1_num*(train_percent+validate_percent))+1:]
        print('测试集标签为1的数量', len(test_1_lines))

        random_2 = random.sample([i for i in range(label_0_num+label_1_num, label_0_num+label_1_num+label_2_num)], label_2_num)
        train_2_lines = random_2[:int(label_2_num*train_percent)+1]
        validate_2_lines = random_2[int(label_2_num*train_percent)+1:int(label_2_num*(train_percent+validate_percent))+1]
        print('验证集标签为2的数量', len(validate_2_lines))
        test_2_lines = random_2[int(label_2_num*(train_percent+validate_percent))+1:]
        print('测试集标签为2的数量', len(test_2_lines))

        # 构造训练集、测试集
        train = all_info[0:0]
        validate = all_info[:0]
        test = all_info[0:0]
        for i in train_0_lines:
            # oversampling
            for j in range(3):
                # loc[i]获取all_info的第i行
                train = train.append(all_info.loc[i])
        for i in train_1_lines:
            train = train.append(all_info.loc[i])
        for i in train_2_lines:
            train = train.append(all_info.loc[i])
        for i in validate_0_lines:
            validate = validate.append(all_info.loc[i])
        for i in validate_1_lines:
            validate = validate.append(all_info.loc[i])
        for i in validate_2_lines:
            validate = validate.append(all_info.loc[i])
        for i in test_0_lines:
            test = test.append(all_info.loc[i])
        for i in test_1_lines:
            test = test.append(all_info.loc[i])
        for i in test_2_lines:
            test = test.append(all_info.loc[i])

        train.to_csv(train_path, encoding='utf-8', index=False)
        validate.to_csv(validate_path, encoding='utf-8', index=False)
        test.to_csv(test_path, encoding='utf-8', index=False)
    else:
        train = pd.read_csv(train_path)
        validate = pd.read_csv(validate_path)
        test = pd.read_csv(test_path)
    return train, validate, test

# train, validate, test = get_train_test(target_path, 'Sheet6', 0.7, 0.1, rf_train_path, rf_validate_path, rf_test_path, True)
train, validate, test = get_train_test(target_path,'Sheet13',0.7,0.1,rf_select_train_path,rf_select_validate_path,rf_select_test_path,True)

target = 'OS'
predictors = [x for x in train.columns if x not in [target]]
# 验证集
real_on_validate = validate[target]
# 测试集
real_on_test = test[target]

important_list = []

# # 网格法调参
# parameters = {'n_estimators':(100, 150), 'criterion':('gini', 'entropy'),
#               'max_features':(3, 4, 5, 6), 'max_depth':(3, 4, 5, 6)}
# rf = RandomForestClassifier()
# clf = GridSearchCV(rf, parameters)
# clf.fit(train[predictors], train[target])
# cv_result = pd.DataFrame.from_dict(clf.cv_results_)
# with open(cv_result_path, 'w') as f:
#     cv_result.to_csv(f)
# print('The parameters of the best model are: ')
# print(clf.best_params_)

# model
# clf = GradientBoostingClassifier(n_estimators=60)
clf = RandomForestClassifier(n_estimators=100, criterion='gini')
clf.fit(train[predictors], train[target])

# 验证集预测结果
predicts_on_validate = clf.predict(validate[predictors])
# 验证集准确率
score_on_validate = clf.score(validate[predictors], real_on_validate)

# 测试集预测结果
predicts_on_test = clf.predict(test[predictors])
# 预测可能性
predicts_on_test_proba = clf.predict_proba(test[predictors])
# print('可能性', predicts_on_test_proba)
# 测试集准确率
score_on_test = clf.score(test[predictors], real_on_test)

# save result
test_res = pd.DataFrame(columns=['is_os_five'])
test_res.is_recur = predicts_on_test
# 真实值与预测值连接
real_predicts = pd.concat([real_on_test, test_res], axis=1)
# 特征重要性
feature_importances = clf.feature_importances_
print('验证集准确率', score_on_validate)
print('测试集准确率', score_on_test)
print('验证集数量', len(validate))
print('测试集数量', len(test))
# print('3年分类错误的数量', predicts_on_test[:25].sum())
# print('5年分类错误的数量', len(test)-25-predicts_on_test[25:].sum())
# print('敏感性', (25-predicts_on_test[:25].sum())/25)
# print('特异性', predicts_on_test[25:].sum()/(len(test)-25))
print(feature_importances)

fpr, tpr, thresholds = roc_curve(real_on_test, predicts_on_test_proba[:,2])
roc_auc = auc(fpr, tpr)
print('roc_auc', roc_auc)
# print(fpr)
# print(tpr)
print(thresholds)
plt.plot(fpr, tpr, lw=1, label='ROC (area= %0.2f)' % (roc_auc))
plt.show()

important_feas = []
while feature_importances.max() >= 0.01:
    important_feas.append(feature_importances.argmax())
    # print(feature_importances.argmax(), end=',')
    feature_importances[feature_importances.argmax()] = 0
important_list.append(important_feas)
print(important_list)




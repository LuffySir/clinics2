# -*-coding:utf-8 -*-
import sys
import pandas as pd
import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier


target_path = r'E:\clinics\temp.xlsx'
rf_train_path = r'E:\clinics\rf_train.csv'
rf_test_path = r'E:\clinics\rf_test.csv'
rf_select_train_path = r'E:\clinics\rf_select_train.csv'
rf_select_test_path = r'E:\clinics\rf_select_test.csv'


def get_train_test(target_path, sheet_name, percent, train_path, test_path, is_random=False):
    # 是否需要重新随机选取训练集和测试集
    if is_random:
        xls_file = pd.ExcelFile(target_path)
        all_info = xls_file.parse(sheet_name)
        all_info = all_info.fillna(1)

        label_0 = all_info[all_info['是否复发'] == 0]
        label_1 = all_info[all_info['是否复发'] == 1]
        label_0_num, label_1_num = len(label_0), len(label_1)

        # 生成随机序列，前70%作训练集
        random_0 = random.sample([i for i in range(label_0_num)], label_0_num)
        train_0_lines = random_0[:int(label_0_num*percent)+1]
        test_0_lines = random_0[int(label_0_num*percent)+1:]

        random_1 = random.sample([i for i in range(label_0_num, label_0_num+label_1_num)], label_1_num)
        train_1_lines = random_1[:int(label_1_num*percent)+1]
        test_1_lines = random_1[int(label_1_num*percent)+1:]

        # 构造训练集、测试集
        train = all_info[0:0]
        test = all_info[0:0]
        for i in train_0_lines:
            # oversampling
            for j in range(3):
                # loc[i]获取all_info的第i行
                train = train.append(all_info.loc[i])
        for i in train_1_lines:
            train = train.append(all_info.loc[i])
        for i in test_0_lines:
            test = test.append(all_info.loc[i])
        for i in test_1_lines:
            test = test.append(all_info.loc[i])

        train.to_csv(train_path, encoding='utf-8', index=False)
        test.to_csv(test_path, encoding='utf-8', index=False)
    else:
        train = pd.read_csv(train_path)
        test = pd.read_csv(test_path)
    return train, test

train, test = get_train_test(target_path,'Sheet6',0.7,rf_train_path,rf_test_path,True)
# train, test = get_train_test(target_path,'Sheet8',0.7,rf_select_train_path,rf_select_test_path,False)

target = '是否复发'
predictors = [x for x in train.columns if x not in [target]]
real = test[target]

important_list = []
for i in range(20):
    # model
    # clf = GradientBoostingClassifier(n_estimators=60)
    clf = RandomForestClassifier(n_estimators=100)
    clf.fit(train[predictors], train[target])
    # 预测结果
    predicts = clf.predict(test[predictors])
    # 准确率
    score = clf.score(test[predictors], real)

    # save result
    test_res = pd.DataFrame(columns=['is_recur'])
    test_res.is_recur = predicts
    # 真实值与预测值连接
    real_predicts = pd.concat([real, test_res], axis=1)
    # 特征重要性
    feature_importances = clf.feature_importances_
    print(predicts[:60].sum())
    print(predicts[60:].sum())
    print(score)
    print(feature_importances)

    important_feas = []
    while feature_importances.max() >= 0.01:
        important_feas.append(feature_importances.argmax())
        # print(feature_importances.argmax(), end=',')
        feature_importances[feature_importances.argmax()] = 0
    important_list.append(important_feas)

# 重要特征出现的次数
feas = {}
for important_feas in important_list:
    print(important_feas)
    for fea in important_feas:
        feas[fea] = feas.get(fea, 0) + 1

feas_order = sorted(feas.items(), key=lambda item:item[1],reverse=True)
print(feas_order)
for key, val in feas_order:
    if val >= 8:
        print(key, end=',')


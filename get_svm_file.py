import xlrd
import linecache
import random
from svmutil import *

target_path = r'E:\clinics\temp.xlsx'

svm_path = r'E:\clinics\svm_form1'
random_svm_path = r'E:\clinics\random_svm_form'


def get_svm_form(r_path, w_path, sheet_num, feas_col, label_col, label_times=1):
    gc_data = xlrd.open_workbook(r_path)
    gc_table = gc_data.sheets()[sheet_num]
    # 标题信息，用来判断特征列是否选择正确
    title_info = gc_table.row_values(0)
    label_nums = {}
    # for t in feas_col:
    #     print(title_info[t])
    with open(w_path,'w') as svm_file:
        for i in range(2, gc_table.nrows):
            fea_num = 1
            row_data = gc_table.row_values(i)
            label = str(row_data[label_col])
            label_nums[label] = label_nums.get(label,0) + 1
            if label == '0':
                for k in range(label_times):
                    fea_num = 1
                    svm_file.write('0' + ' ')
                    for j in feas_col:
                        if row_data[j] == '':
                            row_data[j] = 1
                        svm_file.write(str(fea_num)+':'+str(row_data[j])+' ')
                        fea_num += 1
                    svm_file.write('\n')
            else:
                svm_file.write('1' + ' ')
                for j in feas_col:
                    if row_data[j] == '':
                        row_data[j] = 1
                    svm_file.write(str(fea_num) + ':' + str(row_data[j]) + ' ')
                    fea_num += 1
                svm_file.write('\n')
    # print(label_nums)
    return label_nums


def get_random_samples(r_path, w_path, percent=0.7):
    # 获取类别数量
    with open(r_path, 'r') as svm_file:
        label_nums = {}
        for line in svm_file:
            label = line[:1]
            label_nums[label] = label_nums.get(label, 0) + 1
    label_0_num, label_1_num = label_nums['0'], label_nums['1']
    # 获取随机序列random.sample(序列，数量)
    random_0 = random.sample([i for i in range(label_0_num)], label_0_num)
    # 随机序列中前百分之六十为训练集
    random_train_0 = random_0[:int(label_0_num * percent)]
    # print(len(set(random_train_0)), len(random_train_0), random_train_0)
    # 随机序列中百分之六十以后为测试集
    random_test_0 = random_0[int(label_0_num * percent):]
    # print(len(set(random_test_0)), len(random_test_0), random_test_0)
    random_1 = random.sample([i for i in range(label_1_num)], label_1_num)
    random_train_1 = random_1[:int(label_1_num * percent)]
    # print(len(set(random_train_1)), len(random_train_1), random_train_1)
    random_test_1 = random_1[int(label_1_num * percent):]
    # print(len(set(random_test_1)), len(random_test_1), random_test_1)

    with open(w_path, 'w') as svm_random_file:
        for line in random_train_0:
            train_0_info = linecache.getlines(r_path)[line]
            svm_random_file.write(train_0_info)
        for line in random_train_1:
            train_1_info = linecache.getlines(r_path)[line + label_0_num]
            svm_random_file.write(train_1_info)
        for line in random_test_0:
            test_0_info = linecache.getlines(r_path)[line]
            svm_random_file.write(test_0_info)
        for line in random_test_1:
            test_1_info = linecache.getlines(r_path)[line + label_0_num]
            svm_random_file.write(test_1_info)

    return random_train_0, random_test_0, random_train_1, random_test_1


# def get_svm_model(path, train_num)
# 特征
feas = [i for i in range(49)]
# rmv = [2,3,4,5,9,10,27,28,41,45,47]
# for j in rmv:
#     feas.remove(j)
# svm可读格式
label_nums = get_svm_form(target_path, svm_path, 3, feas, 51, 3)
# 不同标签的训练和测试集
random_train_0, random_test_0, random_train_1, random_test_1 = get_random_samples(svm_path, random_svm_path)

train_num = len(random_train_0) + len(random_train_1)
test_num = len(random_test_0) + len(random_test_1)
print(train_num, test_num)
y, x = svm_read_problem(random_svm_path)
# m = svm_train(y[:train_num], x[:train_num], '-t 2 -h 0 -c 20 -w1 0.5 -w2 0.5')
m = svm_train(y[:train_num], x[:train_num], '-t 1 -h 0 -c 20 -w1 0.5 -w0 0.5')
p_label, p_acc, p_val = svm_predict(y[train_num:], x[train_num:], m)
print(p_acc)
print(len(p_label[:len(random_test_0)]))
print(p_label[:len(random_test_0)].count(0.0))
print(p_label[:len(random_test_0)])
print(len(p_label[len(random_test_0):]))
print(p_label[len(random_test_0):].count(1.0))
print(p_label[len(random_test_0):])

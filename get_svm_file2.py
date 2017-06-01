import xlrd
import linecache
import random
from svmutil import *

target_path = r'src\temp.xlsx'

svm_path = r'src\svm_form1'
svm_path2 = r'src\svm_form2'
random_svm_path = r'src\random_svm_form'
random_svm_path2 = r'src\random_svm_form2'


def get_svm_form_test_no_copy(r_path, w_path, sheet_num, feas_col, label_col, label_times=1):
    gc_data = xlrd.open_workbook(r_path)
    gc_table = gc_data.sheets()[sheet_num]
    # 标题信息，用来判断特征列是否选择正确
    title_info = gc_table.row_values(0)
    label_nums = {}
    # for t in feas_col:
    #     print(title_info[t])
    with open(w_path,'w') as svm_file:
        for i in range(2, gc_table.nrows):
            row_data = gc_table.row_values(i)
            label = str(row_data[label_col])
            label_nums[label] = label_nums.get(label,0) + 1
        label_0_num, label_1_num = label_nums['0'], label_nums['1']
        random_0 = random.sample([i for i in range(2, label_0_num+2)], label_0_num)
        # print(random_0)
        test_0 = random_0[:int(label_0_num*0.3)]
        # print(test_0)
        train_0 = random_0[int(label_0_num*0.3):]
        # 写标签为0的训练集
        for i in range(2, gc_table.nrows):
            fea_num = 1
            row_data = gc_table.row_values(i)
            label = str(row_data[label_col])
            # 训练集标签为0的采样label_times倍
            if label == '0' and i not in test_0:
                for k in range(label_times):
                    fea_num = 1
                    svm_file.write('0' + ' ')
                    for j in feas_col:
                        if row_data[j] == '':
                            row_data[j] = 1
                        svm_file.write(str(fea_num)+':'+str(row_data[j])+' ')
                        fea_num += 1
                    svm_file.write('\n')
        # 写标签为1的数据
        for i in range(2, gc_table.nrows):
            fea_num = 1
            row_data = gc_table.row_values(i)
            label = str(row_data[label_col])
            if label == '1':
                svm_file.write('1' + ' ')
                for j in feas_col:
                    if row_data[j] == '':
                        row_data[j] = 1
                    svm_file.write(str(fea_num) + ':' + str(row_data[j]) + ' ')
                    fea_num += 1
                svm_file.write('\n')
        # 写标签为0的测试集
        for i in range(2, gc_table.nrows):
            fea_num = 1
            row_data = gc_table.row_values(i)
            label = str(row_data[label_col])
            # 测试集不重采样
            if label == '0' and i in test_0:
                svm_file.write('0' + ' ')
                for j in feas_col:
                    if row_data[j] == '':
                        row_data[j] = 1
                    svm_file.write(str(fea_num) + ':' + str(row_data[j]) + ' ')
                    fea_num += 1
                svm_file.write('\n')
    # print(label_nums)
    return label_nums, len(train_0)*label_times, len(test_0)


def get_random_samples(r_path, w_path, train_0_num, test_0_num, percent=0.7):
    # 获取类别数量
    with open(r_path, 'r') as svm_file:
        label_nums = {}
        for line in svm_file:
            label = line[:1]
            label_nums[label] = label_nums.get(label, 0) + 1
    label_0_num, label_1_num = label_nums['0'], label_nums['1']
    # 获取随机序列random.sample(序列，数量)
    random_1 = random.sample([i for i in range(label_1_num)], label_1_num)
    random_train_1 = random_1[:int(label_1_num * percent)]
    # print(len(set(random_train_1)), len(random_train_1), random_train_1)
    random_test_1 = random_1[int(label_1_num * percent):]
    # print(len(set(random_test_1)), len(random_test_1), random_test_1)

    with open(w_path, 'w') as svm_random_file:
        # 写标签为0的训练集
        for line in range(train_0_num):
            train_0_info = linecache.getlines(r_path)[line]
            svm_random_file.write(train_0_info)
        # 写标签为1的训练集
        for line in random_train_1:
            train_1_info = linecache.getlines(r_path)[line + train_0_num]
            svm_random_file.write(train_1_info)
        for line in random_test_1:
            test_1_info = linecache.getlines(r_path)[line + train_0_num]
            svm_random_file.write(test_1_info)
        for line in range(train_0_num+label_1_num, train_0_num+label_1_num+test_0_num):
            test_0_info = linecache.getlines(r_path)[line]
            svm_random_file.write(test_0_info)
    return len(random_train_1), len(random_test_1)


def get_svm_model(path, train_num, test_1_num):
    y, x = svm_read_problem(path)
    m = svm_train(y[:train_num], x[:train_num], '-t 1 -h 1 -c 10')
    # m = svm_train(y[:train_num], x[:train_num], '-t 1 -h 0 -c 20 -w1 0.5 -w0 0.5')
    p_label, p_acc, p_val = svm_predict(y[train_num:], x[train_num:], m)
    print(p_acc)
    print(len(p_label[:test_1_num]))
    print(p_label[:test_1_num].count(1.0))
    print(p_label[:test_1_num])
    print(len(p_label[test_1_num:]))
    print(p_label[test_1_num:].count(0.0))
    print(p_label[test_1_num:])


# is_rand = False
is_rand = True

if is_rand:
    # # 特征
    # feas = [i for i in range(70)]
    # # feas = [i for i in range(31)]
    # rmv = [2,3,4,5,9,10,27,28,41,45,47]
    # # rmv = [27,28,41,45]
    # for j in rmv:
    #     feas.remove(j)

    feas = [1, 15, 19, 20, 21, 23, 25, 26, 42]

    # svm可读格式
    label_nums, train_0_num, test_0_num = get_svm_form_test_no_copy(target_path, svm_path, 6, feas, 70, 3)
    # label_nums, train_0_num, test_0_num = get_svm_form_test_no_copy(target_path, svm_path2, 6, feas, 31, 3)
    print('train_0_num', train_0_num)
    print('test_0_num', test_0_num)
    # 不同标签的训练和测试集
    train_1_num, test_1_num = get_random_samples(svm_path, random_svm_path, train_0_num, test_0_num)
    # train_1_num, test_1_num = get_random_samples(svm_path2, random_svm_path2, train_0_num, test_0_num)
    print('test_1_num', test_1_num)
    train_num = train_0_num + train_1_num
    test_num = test_1_num + test_0_num
    print(train_num, test_num)
    # 训练svm模型
    get_svm_model(random_svm_path, train_num, test_1_num)
else:
    # 训练svm模型
    get_svm_model(random_svm_path, 850, 184)

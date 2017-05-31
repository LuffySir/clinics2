from svmutil import *

random_svm_path = r'E:\clinics\random_svm_form'

def get_svm_model(path, train_num, test_1_num):
    y, x = svm_read_problem(path)
    # m = svm_train(y[:train_num], x[:train_num], '-t 2 -h 0 -c 20 -w1 0.5 -w2 0.5')
    m = svm_train(y[:train_num], x[:train_num], '-t 2 -h 0 -c 120 -w0 2 -w1 0.2')
    p_label, p_acc, p_val = svm_predict(y[train_num:], x[train_num:], m)
    print(p_acc)
    print(len(p_label[:test_1_num]))
    print(p_label[:test_1_num].count(1.0))
    print(p_label[:test_1_num])
    print(len(p_label[test_1_num:]))
    print(p_label[test_1_num:].count(0.0))
    print(p_label[test_1_num:])


get_svm_model(random_svm_path, 850, 184)

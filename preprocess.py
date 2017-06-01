import xlrd
import xlsxwriter
import re
import numpy as np

origin_path = r'E:\clinics\gc_new2.xlsx'
col_nums_path = r'E:\clinics\col_nums.xlsx'
LN_path = r'E:\clinics\LN.xlsx'
comorbidities_path = r'E:\clinics\comorbidities.xlsx'
temp_path = r'E:\clinics\temp.xlsx'
scale_path = r'E:\clinics\scale.xlsx'
temp_path2 = r'E:\clinics\temp2.xlsx'


# 添加列号
def add_col_num(r_path, w_path):
    gc_data = xlrd.open_workbook(r_path)
    gc_table = gc_data.sheets()[2]
    gc_file = xlsxwriter.Workbook(w_path)
    gc_sheet = gc_file.add_worksheet()
    for i in range(gc_table.ncols):
        gc_sheet.write(1, i, i)


# 将LN转移比率转化为数值
def change_LN_into_num(r_path, w_path):
    gc_data = xlrd.open_workbook(r_path)
    gc_table = gc_data.sheets()[3]
    pathology_file = xlsxwriter.Workbook(w_path)
    pathology_sheet = pathology_file.add_worksheet()
    try:
        for i in range(2, gc_table.nrows):
            row_data = gc_table.row_values(i)
            LN_data = str(row_data[17])
            # print(LN_data,type(LN_data))
            LN_data = LN_data.replace('。', '').replace('，', '').replace(',', '').replace('.', '').split('/')

            pathology_sheet.write(i, 0, LN_data[0])
            pathology_sheet.write(i, 1, LN_data[1])
            res = int(LN_data[0]) / int(LN_data[1])
            res = round(res, 4)
            pathology_sheet.write(i, 2, res)
    except FloatingPointError as e:
        print('error:', e)
    pathology_file.close()


# 并存疾病、原发部位拆分
def get_comorbidities(r_path, w_path):
    gc_data = xlrd.open_workbook(r_path)
    gc_table = gc_data.sheets()[3]
    pathology_file = xlsxwriter.Workbook(w_path)
    pathology_sheet = pathology_file.add_worksheet()
    pathology_sheet1 = pathology_file.add_worksheet()
    ill_cols = [k for k in range(7)]
    tumr_pos = [t for t in range(4)]
    for i in range(2, gc_table.nrows):
        row_data = gc_table.row_values(i)
        # 并发疾病（0-6分别作为一列特征）
        comorbidities_data = str(row_data[25]).replace('，', ',').split(',')
        # 原发肿瘤部位
        prim_tumr_pos = str(row_data[12]).replace('，', ',').split(',')
        # 解决读入并发疾病\肿瘤部位为float类型值
        comorbidities_data = [ill[:1] for ill in comorbidities_data if ill != '']
        prim_tumr_pos = [pos[:1] for pos in prim_tumr_pos if pos != '']
        # print(comorbidities_data)
        print(prim_tumr_pos)
        # 若存在该种并发疾病，写1，否则写0
        for col in ill_cols:
            if str(col) not in comorbidities_data:
                pathology_sheet.write(i, col, 0)
            else:
                pathology_sheet.write(i, col, 1)
        for t_col in tumr_pos:
            if str(t_col) not in prim_tumr_pos:
                pathology_sheet1.write(i, t_col, 0)
            else:
                pathology_sheet1.write(i, t_col, 1)
    pathology_file.close()


# 填充缺失项、转换成数值
def fill_and_trans(r_path, w_path):
    gc_data = xlrd.open_workbook(r_path)
    gc_table = gc_data.sheets()[4]
    pathology_file = xlsxwriter.Workbook(w_path)
    pathology_sheet = pathology_file.add_worksheet()
    for i in range(1, gc_table.nrows):
        row_data = gc_table.row_values(i)
        sex = str(int(row_data[0]))
        age = str(row_data[1]).strip()
        height = str(row_data[7])
        weight = str(row_data[8])
        sal = str(row_data[9])
        # 病人来源
        local = str(int(row_data[10]))
        # 手术时间
        oper_time = int(row_data[11])
        # 癌结节数量
        tumor_num = str(row_data[19])
        # 脉管癌栓
        embolus = str(row_data[20])
        # 神经浸润
        neural_invasion = str(row_data[21])
        # 肿瘤直径
        tumor_dia = str(row_data[22])
        # her-2
        her_2 = str(row_data[23])
        # E-cadher
        e_cadher = str(row_data[24])
        # 术后是否专科医生就诊
        is_specialist = str(row_data[31])
        # 是否行术后辅助化疗
        is_post_chemotherapy = str(row_data[32])[:1]
        # 术后至化疗开始时间
        from_oper_to_chemo = str(row_data[33])
        # 化疗方案
        chemo_plan = str(row_data[34])
        # 选择方案原因
        select_reason = str(row_data[35])
        # 完成化疗周期数
        periods = str(row_data[36])
        # 未完成原因
        unfinish_reason = str(row_data[37])
        # 未化疗原因
        no_chemo_reason = str(row_data[38])
        # 是否术后放疗
        is_radiotherapy = str(row_data[39])
        # 是否复发(0复发，1未复发)
        is_recur = str(row_data[44])
        # 随访截止日期
        follow_up_day = str(row_data[46])[:5]
        # 生存时间
        os = str(row_data[47])

        # 不为空则复制
        for j in range(gc_table.ncols):
            if row_data[j] != '':
                pathology_sheet.write(i, j, row_data[j])
            if 54 <= j <= 73:
                if str(row_data[j]) == 'x' or str(row_data[j]) == 'X' or str(row_data[j]) == '':
                    pathology_sheet.write(i, j, -1)

        # 去除部分年龄存在的‘岁’字
        if len(age) > 2:
            age = int(age[:2])
            pathology_sheet.write(i, 1, age)

        # 填充男性基本信息
        if sex == '0':
            # 身高、体重按照男性均值填充
            if height == '':
                pathology_sheet.write(i, 7, 163)
            # else:
            #     pathology_sheet.write(i, 7, int(height))
            if weight == '':
                pathology_sheet.write(i, 8, 63)
            # else:
            #     pathology_sheet.write(i, 8, int(weight))
            # 薪水按照城乡区域的均值分别填充
            if sal == '':
                if local == '0':
                    pathology_sheet.write(i, 9, 1)
                elif local == '1':
                    pathology_sheet.write(i, 9, 2)
                elif local == '2':
                    pathology_sheet.write(i, 9, 1)
            # else:
            #     pathology_sheet.write(i, 9, int(sal))
        # 填充女性基本信息
        elif sex == '1':
            if height == '':
                pathology_sheet.write(i, 7, 153)
            # else:
            #     pathology_sheet.write(i, 7, int(height))
            if weight == '':
                pathology_sheet.write(i, 8, 55)
            # else:
            #     pathology_sheet.write(i, 8, int(weight))
            if sal == '':
                if local == '0':
                    pathology_sheet.write(i, 9, 1)
                elif local == '1':
                    pathology_sheet.write(i, 9, 3)
                elif local == '2':
                    pathology_sheet.write(i, 9, 2)
            # else:
            #     pathology_sheet.write(i, 9, int(sal))

        # 填充癌结节数量
        if tumor_num == '':
            pathology_sheet.write(i, 19, 0)
        # else:
        #     pathology_sheet.write(i, 19, int(tumor_num))

        # 填充有无癌栓
        if embolus == '':
            pathology_sheet.write(i, 20, 1)
        # else:
        #     pathology_sheet.write(i, 20, int(embolus))

        # 填充是否神经浸润
        if neural_invasion == '':
            pathology_sheet.write(i, 21, 1)
        # else:
        #     pathology_sheet.write(i, 21, int(neural_invasion))

        # 填充肿瘤直径（均值）
        if tumor_dia == '':
            pathology_sheet.write(i, 22, 5)
        # else:
        #     pathology_sheet.write(i, 22, float(tumor_dia))

        # 填充her2（没做该项检查和阴性）
        if her_2 == '':
            pathology_sheet.write(i, 23, -1)

        # 填充e_cadher（没做该项检查和阴性）
        if e_cadher == '':
            pathology_sheet.write(i, 24, -1)
        elif e_cadher == '阳性':
            pathology_sheet.write(i, 24, 1)

        # 填充是否于专科医生就诊
        if is_specialist == '是':
            pathology_sheet.write(i, 31, 1)
        elif is_specialist == '否':
            pathology_sheet.write(i, 31, 0)
        elif is_specialist == '':
            pathology_sheet.write(i, 31, -1)

        # 填充是否术后辅助化疗
        if is_post_chemotherapy == '' or is_post_chemotherapy == '0':
            pathology_sheet.write(i, 32, 0)
            # 术后至化疗开始时间
            pathology_sheet.write(i, 33, -1)
            # 化疗方案
            pathology_sheet.write(i, 34, -1)
            # 选择原因
            pathology_sheet.write(i, 35, -1)
            # 完成化疗周期数
            pathology_sheet.write(i, 36, -1)
            # 未完成化疗周期的原因
            pathology_sheet.write(i, 37, -1)

        # 填充是否辅助放疗
        if is_radiotherapy == '' or is_radiotherapy == '否':
            pathology_sheet.write(i, 39, 0)
        elif is_radiotherapy == '是':
            pathology_sheet.write(i, 39, 1)

        # 填充随访截止日期(按照2014/3/1填充)
        if follow_up_day == '':
            follow_up_day = 41699
            pathology_sheet.write(i, 46, 41699)

        # 填充并离散化os
        if os != '':
            fill_os = str(int(float(os)))
            if int(fill_os) < 36:
                pathology_sheet.write(i, 47, 0)
            elif int(fill_os) < 60:
                pathology_sheet.write(i, 47, 1)
            else:
                pathology_sheet.write(i, 47, 2)

        elif os == '':
            fill_os = str(int((int(follow_up_day) - int(oper_time)) / 30))
            if int(fill_os) < 36:
                pathology_sheet.write(i, 47, 0)
            elif int(fill_os) < 60:
                pathology_sheet.write(i, 47, 1)
            else:
                pathology_sheet.write(i, 47, 2)


# 特征缩放
def get_feature_scaling(r_path, w_path):
    gc_data = xlrd.open_workbook(r_path)
    gc_table = gc_data.sheets()[2]
    pathology_file = xlsxwriter.Workbook(w_path)
    pathology_sheet = pathology_file.add_worksheet()
    # 年龄
    ages = []
    # 身高
    heights = []
    # 体重
    weights = []
    # LN分子
    LN1 = []
    # LN分母
    LN2 = []
    # 肿瘤直径
    tumor_size = []
    # 症状出现至诊断时间
    cure_time = []
    # 确诊至手术时间
    oper_time = []
    # 完成化疗周期数
    chemo_period = []
    # os生存时间
    os = []
    for i in range(2, gc_table.nrows):
        row_data = gc_table.row_values(i)
        ages.append(row_data[1])
        heights.append(row_data[7])
        weights.append(row_data[8])
        LN1.append(float(row_data[19]))
        LN2.append(float(row_data[20]))
        tumor_size.append(row_data[26])
        cure_time.append(row_data[37])
        oper_time.append(row_data[38])
        chemo_period.append(row_data[46])
        os.append(float(row_data[51]))

    # print(transformed, np.array(transformed))
    # print(gc_table.row_values(0)[6],gc_table.row_values(0)[7],gc_table.row_values(0)[12],gc_table.row_values(0)[29])
    # 各指标的平均值，标准差
    ages_mean, ages_std = np.mean(ages), np.std(ages, ddof=1)
    heights_mean, heights_std = np.mean(heights), np.std(heights, ddof=1)
    weights_mean, weights_std = np.mean(weights), np.std(weights, ddof=1)
    LN1_mean, LN1_std = np.mean(LN1), np.std(LN1, ddof=1)
    LN2_mean, LN2_std = np.mean(LN2), np.std(LN2, ddof=1)
    tumor_size_mean, tumor_size_std = np.mean(tumor_size), np.std(tumor_size, ddof=1)
    cure_time_mean, cure_time_std = np.mean(cure_time), np.std(cure_time, ddof=1)
    oper_time_mean, oper_time_std = np.mean(oper_time), np.std(oper_time, ddof=1)
    chemo_period_mean, chemo_period_std = np.mean(chemo_period), np.std(chemo_period, ddof=1)
    os_mean, os_std = np.mean(os), np.std(os, ddof=1)
    # 特征缩放（归一化）
    for j in range(2, gc_table.nrows):
        row_data = gc_table.row_values(j)
        ages_fea_scl = (row_data[1] - ages_mean) / ages_std
        pathology_sheet.write(j, 0, round(ages_fea_scl, 4))
        heights_fea_scl = (row_data[7] - heights_mean) / heights_std
        pathology_sheet.write(j, 1, round(heights_fea_scl, 4))
        weights_fea_scl = (row_data[8] - weights_mean) / weights_std
        pathology_sheet.write(j, 2, round(weights_fea_scl, 4))
        LN1_fea_scl = (float(row_data[19]) - LN1_mean) / LN1_std
        pathology_sheet.write(j, 3, round(LN1_fea_scl, 4))
        LN2_fea_scl = (float(row_data[20]) - LN2_mean) / LN2_std
        pathology_sheet.write(j, 4, round(LN2_fea_scl, 4))
        tumor_size_fea_scl = (row_data[26] - tumor_size_mean) / tumor_size_std
        pathology_sheet.write(j, 5, round(tumor_size_fea_scl, 4))
        cure_time_fea_scl = (row_data[37] - cure_time_mean) / cure_time_std
        pathology_sheet.write(j, 6, round(cure_time_fea_scl, 4))
        oper_time_fea_scl = (row_data[38] - oper_time_mean) / oper_time_std
        pathology_sheet.write(j, 7, round(oper_time_fea_scl, 4))
        chemo_period_fea_scl = (row_data[46] - chemo_period_mean) / chemo_period_std
        pathology_sheet.write(j, 8, round(chemo_period_fea_scl, 4))
        os_fea_scl = (float(row_data[51]) - os_mean) / os_std
        pathology_sheet.write(j, 9, round(os_fea_scl, 4))
    pathology_file.close()


# add_col_num(temp_path, col_nums_path)
# change_LN_into_num(origin_path, LN_path)
# get_comorbidities(origin_path, comorbidities_path)
fill_and_trans(origin_path, temp_path2)
# get_feature_scaling(temp_path, scale_path)


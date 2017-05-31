import xlrd
import pandas as pd
import numpy as np

path=r'E:\clinics\gc_new2.xlsx'
xls = pd.ExcelFile(path)
table = xls.parse('Sheet2')

man = table[table['性别']==0]
# 男性平均身高 # 163.4819944598338
man_hei_mean = np.rint(man['身高'].mean())
# 男性平均体重 # 62.670520231213871
man_wei_mean = np.rint(man['体重'].mean())

# 农村男性月收入平均值 # 0.97826086956521741
man_sal_mean_0 = np.rint(man[man['病人\n来源']==0]['月\n收入'].mean())

# 城市男性月收入平均值 # 1.948051948051948
man_sal_mean_1 = np.rint(man[man['病人\n来源']==1]['月\n收入'].mean())

# 城镇男性月收入平均值 # 1.3157894736842106
man_sal_mean_2 = np.rint(man[man['病人\n来源']==2]['月\n收入'].mean())

man[man['病人\n来源']==0]['月\n收入'].fillna(man_sal_mean_0)
man[man['病人\n来源']==1]['月\n收入'].fillna(man_sal_mean_1)
man[man['病人\n来源']==2]['月\n收入'].fillna(man_sal_mean_2)


woman = table[table['性别']==1]
# 女性平均身高
woman['身高'].mean()
# 152.94573643410854
woman['体重'].mean()
# 55.182038834951456
woman[woman['病人\n来源']==0]['月\n收入'].mean()
# 1.0
woman[woman['病人\n来源']==1]['月\n收入'].mean()
# 2.5128205128205128
woman[woman['病人\n来源']==2]['月\n收入'].mean()
# 2.2777777777777777
woman[woman['病人\n来源']==0]['月\n收入'].fillna(np.rint(woman[woman['病人\n来源']==0]['月\n收入'].mean()))
woman[woman['病人\n来源']==1]['月\n收入'].fillna(np.rint(woman[woman['病人\n来源']==1]['月\n收入'].mean()))
woman[woman['病人\n来源']==2]['月\n收入'].fillna(np.rint(woman[woman['病人\n来源']==2]['月\n收入'].mean()))
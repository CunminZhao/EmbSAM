import pandas as pd


csv_path=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\Submission\Public Data\ITK-SNAP-CVE Data\Emb3\Emb3_Stat_old.csv'

origianl_stat=pd.read_csv(csv_path, index_col=[0, 1],header=0)

new_stat_value=origianl_stat.values/2

new_stat=pd.DataFrame(index=origianl_stat.index,columns=origianl_stat.columns,data=new_stat_value)

new_stat.to_csv('Emb3_Stat.csv')
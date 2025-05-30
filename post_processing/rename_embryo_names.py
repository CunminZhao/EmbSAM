import glob
import os

# ======================OBJ DATA (SINGLE DATA FORLDER RENAMING)======================================================

# naming_dict={'190311plc1mp1':'Emb1','190311plc1mp3':'Emb2','190311plc1mp2':'Emb3','Membrane':'Emb4','190315plc1mp1':'Emb5',
#              'emb1':'Emb1','emb2':'Emb2','emb3':'Emb3','emb4':'Emb4','emb5':'Emb5'}
naming_dict={
               'compress1':'Emb6',
'Compressed2':'Emb7',
'Uncompressed1':'Emb8',
'Uncompressed2':'Emb9'}

# data_source=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\seg_result\seg_cell'

data_source=r'H:\EmbSAM\revision\4data\tif\combined_obj'

for folder_name in os.listdir(data_source):
    files=glob.glob(os.path.join(data_source,folder_name,'*'))
    embryo_name_this_orin=os.path.basename(files[0]).split('.')[0].split('_')[0]
    for file_name in files:
        target_name=os.path.basename(file_name).replace(embryo_name_this_orin,naming_dict[embryo_name_this_orin])
        os.rename(file_name,os.path.join(os.path.dirname(file_name),target_name))

for dir_this in os.listdir(data_source):
    if dir_this in naming_dict:
        os.rename(os.path.join(data_source, dir_this),os.path.join(data_source,naming_dict[dir_this]))
# ================================================================================================================

# ==================GUI DATA RENAMING==========================================================

# root_dir=r'H:\EmbSAM\revision\4data\GUIData'
#
# rename_dict = {
#     # '241007plc1KOp1':'Abla_MSpp_1',
#                'compress1':'Emb6',
# 'Compressed2':'Emb7',
# 'Uncompressed1':'Emb8',
# 'Uncompressed2':'Emb9'}
#
#
#
# for dir_this in os.listdir(root_dir):
#     if os.path.isfile(os.path.join(root_dir,dir_this)):
#         continue
#     embryo_original_name=dir_this
#     # for file_name_this in os.listdir(os.path.join(root_dir,dir_this)):
#     #     # embryo_original_name,tp_this=file_name_this.split('_')[:2]
#     #     if embryo_original_name in rename_dict.keys():
#     this_gui_emb_path=os.path.join(root_dir,embryo_original_name)
#     for this_one_dir in os.listdir(this_gui_emb_path):
#         if os.path.isdir(os.path.join(this_gui_emb_path,this_one_dir)):
#             files = os.listdir(os.path.join(this_gui_emb_path, this_one_dir))
#             for original_file_name in files:
#                 target_name = original_file_name.replace(embryo_original_name, rename_dict[embryo_original_name])
#
#                 os.rename(os.path.join(this_gui_emb_path, this_one_dir,original_file_name),
#                           os.path.join(this_gui_emb_path, this_one_dir,target_name))
#         else:
#             os.rename(os.path.join(this_gui_emb_path,this_one_dir),
#                       os.path.join(this_gui_emb_path,this_one_dir.replace(embryo_original_name, rename_dict[embryo_original_name])))
#
# for dir_this in os.listdir(root_dir):
#     if dir_this in rename_dict:
#         os.rename(os.path.join(root_dir, dir_this),os.path.join(root_dir,rename_dict[dir_this]))
# ============================================================================
import glob
import os

import numpy as np
# import pandas
import pandas as pd
import json

from utils.data_io import nib_load,nib_save

# def merge_dictionary_based_on_1():
#     base_dictionary_path=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\segmentation results\10s_data_from_guoye\name_dictionary_fast.csv'
#     merging_dictionary_path=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\segmentation results\name_dictionary_fast2.csv'
#
#     base_dictionary=pd.read_csv(base_dictionary_path, index_col=0).to_dict()['0']
#     merging_dictionary=pd.read_csv(merging_dictionary_path, index_col=0).to_dict()['0']
#     max_in_base_dict=max(base_dictionary.keys())
#     for index,key in enumerate(merging_dictionary.keys()):
#         if
#         base_dictionary[max_in_base_dict+index+1]=merging_dictionary[key]
#
#
#
#
#     name_dictionary = pd.DataFrame.from_dict(base_dictionary, orient="index")
#     name_dictionary.to_csv(r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\segmentation results\name_dictionary_fast.csv')

def merge_single_cells():
    base_dictionary_path=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\seg_result\name_dictionary_base.csv'
    updated_dictionary_path= r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\seg_result\name_dictionary.csv'

    label_2_cell_dict=pd.read_csv(base_dictionary_path, index_col=0).to_dict()['0']
    name_2_label_dict = {value: key for key, value in label_2_cell_dict.items()}


    # label_2_cell_dict = base_dictionary.co

    root_embryo_data = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\seg_result\emb3\emb3_seg_result'
    saving_embryo_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\seg_result\seg_cell\Emb3'
    embryo_frames = [f.path for f in os.scandir(root_embryo_data) if f.is_dir()]
    size_3d = [256, 356, 160] # NEED TO BE NOTIFIED
    loss_cells = []
    for embryo_frame in embryo_frames:
        print(os.path.basename(embryo_frame))
        cell_niigzs = glob.glob(os.path.join(embryo_frame, '*.nii.gz'))
        to_save_segmentation = np.zeros(size_3d)
        for cell_niigz in cell_niigzs:
            # print(os.path.basename(cell_niigz))
            file_formfix = os.path.basename(cell_niigz).split('.')[0].split('_')
            if len(file_formfix)<3:
                continue
            cell_name_this=file_formfix[-1]
            this_niigz = nib_load(cell_niigz)
            cell_label_this = np.unique(this_niigz)

            if len(cell_label_this) < 2:
                loss_cells.append([os.path.basename(embryo_frame), cell_name_this])
            else:
                if cell_name_this not in name_2_label_dict.keys():
                    this_in_base_dict = max(label_2_cell_dict.keys())+1
                    print('updating; label, cell name',this_in_base_dict,cell_name_this)
                    label_2_cell_dict[this_in_base_dict] = cell_name_this
                    name_2_label_dict[cell_name_this]=this_in_base_dict
                    to_save_segmentation[this_niigz == cell_label_this[1]] = this_in_base_dict
                else:
                    to_save_segmentation[this_niigz == cell_label_this[1]] = name_2_label_dict[cell_name_this]

        nib_save(to_save_segmentation, os.path.join(saving_embryo_path, os.path.basename(embryo_frame) + '.nii.gz'))
    name_dictionary = pd.DataFrame.from_dict(label_2_cell_dict, orient="index")
    name_dictionary.to_csv(updated_dictionary_path)
    with open('convert.txt', 'w') as convert_file:
        convert_file.write(json.dumps(loss_cells))


if __name__ == '__main__':
    merge_single_cells()




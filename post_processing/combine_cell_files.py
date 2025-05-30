import glob
import pandas as pd
import json
import os
from tqdm import tqdm
import pickle
from treelib import Tree
import numpy as np

from utils.cell_tree import construct_celltree, read_cd_file
from utils.data_io import check_folder

from utils.data_io import nib_load, nib_save


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
    base_dictionary_path = r'D:\BaiduSyncdisk\EmbSAM\revision\4data\name_dictionary_base.csv'
    updated_dictionary_path = r'D:\BaiduSyncdisk\EmbSAM\revision\4data\name_dictionary.csv'

    label_2_cell_dict = pd.read_csv(base_dictionary_path, index_col=0).to_dict()['0']
    name_2_label_dict = {value: key for key, value in label_2_cell_dict.items()}

    # label_2_cell_dict = base_dictionary.co

    root_embryo_data = r'D:\BaiduSyncdisk\EmbSAM\revision\4data\emb9_segcell'
    saving_embryo_path = r'D:\BaiduSyncdisk\EmbSAM\revision\4data\merged_segcell\Emb9'
    embryo_frames = [f.path for f in os.scandir(root_embryo_data) if f.is_dir()]
    # size_3d = [256, 356, 160] # NEED TO BE NOTIFIED
    size_3d = [256, 356, 210]  # NEED TO BE NOTIFIED

    loss_cells = []
    for embryo_frame in embryo_frames:
        print(os.path.basename(embryo_frame))
        cell_niigzs = glob.glob(os.path.join(embryo_frame, '*.nii.gz'))
        to_save_segmentation = np.zeros(size_3d)
        for cell_niigz in cell_niigzs:
            # print(os.path.basename(cell_niigz))
            file_formfix = os.path.basename(cell_niigz).split('.')[0].split('_')
            if len(file_formfix) < 3:
                continue
            cell_name_this = file_formfix[-1]
            this_niigz = nib_load(cell_niigz)
            cell_label_this = np.unique(this_niigz)

            if len(cell_label_this) < 2:
                loss_cells.append([os.path.basename(embryo_frame), cell_name_this])
            else:
                if cell_name_this not in name_2_label_dict.keys():
                    this_in_base_dict = max(label_2_cell_dict.keys()) + 1
                    print('updating; label, cell name', this_in_base_dict, cell_name_this)
                    label_2_cell_dict[this_in_base_dict] = cell_name_this
                    name_2_label_dict[cell_name_this] = this_in_base_dict
                    to_save_segmentation[this_niigz == cell_label_this[1]] = this_in_base_dict
                else:
                    to_save_segmentation[this_niigz == cell_label_this[1]] = name_2_label_dict[cell_name_this]

        nib_save(to_save_segmentation, os.path.join(saving_embryo_path, os.path.basename(embryo_frame) + '.nii.gz'))
    name_dictionary = pd.DataFrame.from_dict(label_2_cell_dict, orient="index")
    name_dictionary.to_csv(updated_dictionary_path)
    with open('convert.txt', 'w') as convert_file:
        convert_file.write(json.dumps(loss_cells))


def process_dividing_cells():
    raw_z_resolution = 68
    z_resolution = 160

    segmented_cells_path = r'H:\EmbSAM\revision\4data\merged_segcell'
    saving_new_volume_root_path=r'H:\EmbSAM\revision\4data\dividing_segcell'

    # embryo_names_list = ['compress1', 'Compressed2', 'Uncompressed1']
    embryo_names_list = ['Uncompressed2']  # uncompressed2 bias - 117 !!!!!!!!!!!!!!!
    # running_max_time_list = [475, 464, 499]
    running_max_time_list = [382]
    segmented_volume_cd_file_bias=117

    name_dictionary_path = r'H:\EmbSAM\revision\4data\name_dictionary.csv'
    label_name_dict = pd.read_csv(name_dictionary_path, index_col=0).to_dict()['0']
    name_label_dict = {value: key for key, value in label_name_dict.items()}

    for idx, embryo_name in enumerate(embryo_names_list):
        # ------------------------------------------------------
        annotated_root_path = r'H:\EmbSAM\revision\4data\cdfiles'
        cd_file_path = os.path.join(annotated_root_path, 'CD{}.csv'.format(embryo_name))
        # cd_file_all_dict = {}
        cd_file_dataframe = read_cd_file(cd_file_path)
        # print('constructing cell tree for ', embryo_name)
        cell_tree = construct_celltree(cd_file_path, running_max_time_list[idx]+segmented_volume_cd_file_bias, name_dictionary_path)
        for tp in tqdm(range(1, running_max_time_list[idx] + 1),
                       desc='generating {} nucloc file per time point'.format(embryo_name)):

            segmented_volume_path = os.path.join(segmented_cells_path, embryo_name,
                                                 '{}_{}.nii.gz'.format(embryo_name, str(tp).zfill(3)))

            segmented_volume=nib_load(segmented_volume_path)
            cell_labels_in_volume=np.unique(segmented_volume)[1:]

            segmented_volume_new=segmented_volume.copy()

            this_tp_cd_file_dataframe = cd_file_dataframe.loc[cd_file_dataframe['time'] == (tp+segmented_volume_cd_file_bias)]

            no_repeat_record_list=[]

            for index_tmp in this_tp_cd_file_dataframe.index:
                cell_name_ = this_tp_cd_file_dataframe.loc[index_tmp]['cell']
                cell_label_ = name_label_dict[cell_name_]
                if cell_label_ not in cell_labels_in_volume:
                    # print(cell_name_)
                    cell_mother_node = cell_tree.parent(cell_name_)
                    cell_mother_name=cell_mother_node.tag
                    cell_mother_label = name_label_dict.get(cell_mother_name, None)

                    children_list = cell_tree.children(cell_mother_name)
                    daughter_cell1 = children_list[0].tag
                    daughter_cell2 = children_list[1].tag
                    another_one_name = daughter_cell2 if daughter_cell1 == cell_name_ else daughter_cell1
                    another_one_label=name_label_dict[another_one_name]
                    if another_one_label in cell_labels_in_volume:
                        no_repeat_record_list.append(cell_mother_label)


                        zxy_pos1 = this_tp_cd_file_dataframe.loc[this_tp_cd_file_dataframe['cell'] == daughter_cell1]
                        zxy_pos2 = this_tp_cd_file_dataframe.loc[this_tp_cd_file_dataframe['cell'] == daughter_cell2]

                        #                 print(zxy_pos1,zxy_pos2)

                        y1 = int(float(zxy_pos1.iloc[0]['x']) / 712 * 356)  # labelled as X in cd file
                        x1 = int(float(zxy_pos1.iloc[0]['y']) / 512 * 256)  # labelled as Y in cd file
                        z1 = z_resolution - int(float(zxy_pos1.iloc[0]['z']) / raw_z_resolution * z_resolution)

                        y2 = int(float(zxy_pos2.iloc[0]['x']) / 712 * 356)  # labelled as X in cd file
                        x2 = int(float(zxy_pos2.iloc[0]['y']) / 512 * 256)  # labelled as Y in cd file
                        z2 = z_resolution - int(float(zxy_pos2.iloc[0]['z']) / raw_z_resolution * z_resolution)

                        if segmented_volume[x1,y1,z1]==segmented_volume[x2,y2,z2] and segmented_volume[x1,y1,z1]==another_one_label:
                            segmented_volume_new[segmented_volume==another_one_label]=cell_mother_label

            saving_new_volume_path=os.path.join(saving_new_volume_root_path,embryo_name,'{}_{}.nii.gz'.format(embryo_name, str(tp).zfill(3)))
            nib_save(segmented_volume_new,saving_new_volume_path)




if __name__ == '__main__':
    # merge_single_cells()
    process_dividing_cells()
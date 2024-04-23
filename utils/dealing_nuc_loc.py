import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os
from tqdm import tqdm
import pickle
from treelib import Tree
import numpy as np

from utils.cell_tree import construct_celltree, read_cd_file
from utils.data_io import check_folder


def save_the_morphological_and_nuc_location_file(name_dictionary_path, embryo_name, running_max_time,CD_file_root,stat_file_root,raw_z_resolution=92,z_resolution=214,three_d_resolution=0.18):

    label_name_dict = pd.read_csv(name_dictionary_path, index_col=0).to_dict()['0']
    name_label_dict = {value: key for key, value in label_name_dict.items()}

    # ----really important, ({raw image x}/{3D volume x}*{xy_resolution})-----------
    # volume_coefficient = ((512 / 256) * 0.09) ** 3
    # surface_coefficient = ((512 / 256) * 0.09) ** 2
    volume_coefficient=three_d_resolution**3
    surface_coefficient=three_d_resolution**2
    # ---------------------read cd file---------------------------------
    cd_file_path = os.path.join(CD_file_root, 'CD{}.csv'.format(embryo_name))
    # cd_file_all_dict = {}
    cd_file_dataframe=read_cd_file(cd_file_path)
    # print('constructing cell tree for ', embryo_name)
    cell_tree = construct_celltree(cd_file_path, running_max_time,name_dictionary_path)
    # ---------------------------------------------------------------

    # ==================================================================================================================
    for tp in tqdm(range(1, running_max_time + 1), desc='generating {} nucloc file per time point'.format(embryo_name)):
        # cd_dict_this = {}
        no_repeat_record_list = []
        this_tp_cd_file_dataframe=cd_file_dataframe.loc[cd_file_dataframe['time']==tp]
        # for (cell_name_tem, tp_tem), values_tem in cd_file_all_dict.items():
        #     # print(type(tp_tem),type(tp))
        #     if str(tp) == tp_tem:
        #         cd_dict_this[cell_name_tem] = values_tem

        stat_path_this_embryo = os.path.join(stat_file_root, embryo_name)
        # read the cell volume pkl file
        with open(os.path.join(stat_path_this_embryo, '{}_{}_volume.txt'.format(embryo_name, str(tp).zfill(3))),
                  'rb') as handle:
            volume_dict = pickle.load(handle)
        # read the cell surface area pkl file
        with open(os.path.join(stat_path_this_embryo, '{}_{}_surface.txt'.format(embryo_name, str(tp).zfill(3))),
                  'rb') as handle:
            surface_dict = pickle.load(handle)
        # x y z is the size of the 3D volume, designed by you
        df_nucLoc = pd.DataFrame(
            columns=['nucleus_label', 'nucleus_name', 'x_256', 'y_356', 'z_{}'.format(z_resolution), 'volume', 'surface', 'note'])
        for index_tmp in this_tp_cd_file_dataframe.index:
            cell_name_=this_tp_cd_file_dataframe.loc[index_tmp]['cell']
            cell_label_ = name_label_dict[cell_name_]
            #             print(zxy_pos)
            if cell_label_ in volume_dict.keys():
                y = int(float(this_tp_cd_file_dataframe.loc[index_tmp]['x']) / 712 * 356)  # y is labelled as X in cd file
                x = int(float(this_tp_cd_file_dataframe.loc[index_tmp]['y']) / 512 * 256)  # x is labelled as Y in cd file
                z = z_resolution - int(float(this_tp_cd_file_dataframe.loc[index_tmp]['z']) / raw_z_resolution * z_resolution)

                df_nucLoc.loc[len(df_nucLoc.index)] = [cell_label_, cell_name_, x, y, z,
                                                       volume_dict[cell_label_] * volume_coefficient,
                                                       surface_dict[cell_label_] * surface_coefficient, None]
                continue
            # -------------deal with dividing or lost cellsssssssssssssss----------------------------
            cell_mother_node = cell_tree.parent(cell_name_)
            cell_mother_name_ = cell_mother_node.tag
            cell_mother_label_ = name_label_dict.get(cell_mother_name_, None)
            if cell_mother_label_ in volume_dict.keys() and cell_mother_label_ not in no_repeat_record_list:
                # mother exist,  dividing
                no_repeat_record_list.append(cell_mother_label_)

                children_list = cell_tree.children(cell_mother_name_)
                daughter_cell1 = children_list[0].tag
                daughter_cell2 = children_list[1].tag
                # print('dividing ', embryo_name, tp, cell_mother_name_, daughter_cell1, daughter_cell2)

                cell_label1 = name_label_dict[daughter_cell1]
                cell_label2 = name_label_dict[daughter_cell2]

                zxy_pos1 = this_tp_cd_file_dataframe.loc[this_tp_cd_file_dataframe['cell']==daughter_cell1]
                zxy_pos2 = this_tp_cd_file_dataframe.loc[this_tp_cd_file_dataframe['cell']==daughter_cell2]

                #                 print(zxy_pos1,zxy_pos2)

                y1 = int(float(zxy_pos1.iloc[0]['x']) / 712 * 356)  # labelled as X in cd file
                x1 = int(float(zxy_pos1.iloc[0]['y']) / 512 * 256)  # labelled as Y in cd file
                z1 = z_resolution - int(float(zxy_pos1.iloc[0]['z']) / raw_z_resolution * z_resolution)

                y2 = int(float(zxy_pos2.iloc[0]['x']) / 712 * 356)  # labelled as X in cd file
                x2 = int(float(zxy_pos2.iloc[0]['y']) / 512 * 256)  # labelled as Y in cd file
                z2 = z_resolution - int(float(zxy_pos2.iloc[0]['z']) / raw_z_resolution * z_resolution)

                df_nucLoc.loc[len(df_nucLoc.index)] = [cell_mother_label_, cell_mother_name_, None, None, None,
                                                       volume_dict[cell_mother_label_] * volume_coefficient,
                                                       surface_dict[cell_mother_label_] * surface_coefficient, 'mother']
                df_nucLoc.loc[len(df_nucLoc.index)] = [cell_label1, daughter_cell1, x1, y1, z1, None, None,
                                                       'child of {}'.format(cell_mother_name_)]
                df_nucLoc.loc[len(df_nucLoc.index)] = [cell_label2, daughter_cell2, x2, y2, z2, None, None,
                                                       'child of {}'.format(cell_mother_name_)]
            elif cell_mother_label_ not in no_repeat_record_list:
                # print('lost cell ', embryo_name, tp, cell_name_)
                y = int(
                    float(this_tp_cd_file_dataframe.loc[index_tmp]['x']) / 712 * 356)  # y is labelled as X in cd file
                x = int(
                    float(this_tp_cd_file_dataframe.loc[index_tmp]['y']) / 512 * 256)  # x is labelled as Y in cd file
                z = z_resolution - int(
                    float(this_tp_cd_file_dataframe.loc[index_tmp]['z']) / raw_z_resolution * z_resolution)

                df_nucLoc.loc[len(df_nucLoc.index)] = [cell_label_, cell_name_, x, y, z,None, None, 'lost']

        nucLoc_save_file_path = os.path.join(stat_file_root, 'NucLocFile', embryo_name,
                                             '{}_{}_cellInfo.csv'.format(embryo_name,
                                                                       str(tp).zfill(3)))
        check_folder(nucLoc_save_file_path)
        df_nucLoc.to_csv(nucLoc_save_file_path, index=False)
    # =================================================================================================================

    # -==============assemble ========== surface-------------and-----------volume===================================
    all_names = [cname for cname in cell_tree.expand_tree(mode=Tree.WIDTH)]
    # for idx, cell_name in enumerate(all_names):
    volume_embryo = pd.DataFrame(
        np.full(shape=(running_max_time, len(all_names)), fill_value=np.nan, dtype=np.float32),
        index=range(1, running_max_time + 1), columns=all_names)

    surface_embryo = pd.DataFrame(
        np.full(shape=(running_max_time, len(all_names)), fill_value=np.nan, dtype=np.float32),
        index=range(1, running_max_time + 1), columns=all_names)

    for tp in tqdm(range(1, running_max_time + 1),
                   desc='assembling volume and surface area of {} result'.format(embryo_name)):
        path_tmp = os.path.join(stat_file_root, embryo_name)
        with open(os.path.join(path_tmp, '{}_{}_volume.txt'.format(embryo_name, str(tp).zfill(3))),
                  'rb') as handle:
            volume_dict = pickle.load(handle)
        with open(os.path.join(path_tmp, '{}_{}_surface.txt'.format(embryo_name, str(tp).zfill(3))),
                  'rb') as handle:
            surface_dict = pickle.load(handle)

        for cell_label_, vol_value in volume_dict.items():
            cell_name_ = label_name_dict[cell_label_]
            volume_embryo.loc[tp, cell_name_] = (vol_value * volume_coefficient).astype(np.float32)

        for cell_label_, sur_value in surface_dict.items():
            cell_name_ = label_name_dict[cell_label_]
            surface_embryo.loc[tp, cell_name_] = (sur_value * surface_coefficient).astype(np.float32)

    volume_embryo = volume_embryo.loc[:, ((volume_embryo != 0) & (~np.isnan(volume_embryo))).any(axis=0)]
    volume_embryo.to_csv(os.path.join(stat_file_root, embryo_name + '_volume.csv'))
    surface_embryo = surface_embryo.loc[:, ((surface_embryo != 0) & (~np.isnan(surface_embryo))).any(axis=0)]
    surface_embryo.to_csv(os.path.join(stat_file_root, embryo_name + '_surface.csv'))

    # ------------contact-----------initialize the contact csv  file----------------------
    # Get tuble lists with elements from the list

    name_combination = []
    first_level_names = []
    for i, name1 in enumerate(all_names):
        for name2 in all_names[i + 1:]:
            if not (cell_tree.is_ancestor(name1, name2) or cell_tree.is_ancestor(name2, name1)):
                first_level_names.append(name1)
                name_combination.append((name1, name2))

    multi_index = pd.MultiIndex.from_tuples(name_combination, names=['cell1', 'cell2'])
    # print(multi_index)
    stat_embryo = pd.DataFrame(
        np.full(shape=(running_max_time, len(name_combination)), fill_value=np.nan, dtype=np.float32),
        index=range(1, running_max_time + 1), columns=multi_index)
    # set zero element to express the exist of the specific nucleus
    for cell_name in all_names:
        if cell_name not in first_level_names:
            continue
        try:
            cell_time = cell_tree.get_node(cell_name).data.get_time()
            cell_time = [x for x in cell_time if x <= running_max_time]
            stat_embryo.loc[cell_time, (cell_name, slice(None))] = 0
        except:
            cell_name
    # print(stat_embryo)
    # edges_view = point_embryo.edges(data=True)
    for tp in tqdm(range(1, running_max_time + 1),
                   desc='assembling contact surface of {} result'.format(embryo_name)):
        path_tmp = os.path.join(stat_file_root, embryo_name)
        with open(os.path.join(path_tmp, '{}_{}_contact.txt'.format(embryo_name, str(tp).zfill(3))),
                  'rb') as handle:
            contact_dict = pickle.load(handle)
        for contact_sur_idx, contact_sur_value in contact_dict.items():
            [cell1, cell2] = contact_sur_idx.split('_')
            cell1_name = label_name_dict[int(cell1)]
            cell2_name = label_name_dict[int(cell2)]
            if (cell1_name, cell2_name) in stat_embryo.columns:
                stat_embryo.loc[tp, (cell1_name, cell2_name)] = float(contact_sur_value) * surface_coefficient
            elif (cell2_name, cell1_name) in stat_embryo.columns:
                stat_embryo.loc[tp, (cell2_name, cell1_name)] = float(contact_sur_value) * surface_coefficient
            else:
                pass
                # print('columns missing (cell1_name, cell2_name)')
    stat_embryo = stat_embryo.loc[:, ((stat_embryo != 0) & (~np.isnan(stat_embryo))).any(axis=0)]
    # print(stat_embryo)
    stat_embryo.to_csv(os.path.join(stat_file_root, embryo_name + '_contact.csv'))
    # --------------------------------------------------------------------------------------------
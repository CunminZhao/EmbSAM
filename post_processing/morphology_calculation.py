import os.path
import time
from glob import glob
import numpy as np
from scipy import ndimage
import pickle
from tqdm import tqdm
import multiprocessing as mp
import pandas as pd

from utils.dealing_nuc_loc import save_the_morphological_and_nuc_location_file
from utils.data_io import nib_load, check_folder, nib_save


def calculate_cell_surface_and_contact_points(config):
    embryo_name_tp_path = config[0]
    stat_data_path = config[1]

    embryo_name, time_point = os.path.basename(embryo_name_tp_path).split('_')[:2]

    if embryo_name_tp_path is None:
        raise Exception("Sorry, no path_embryo given!")

    # ------------------------calculate surface points using dialation for each cell --------------------
    frame_this_embryo = str(time_point).zfill(3)
    file_name = embryo_name + '_' + frame_this_embryo + '.nii.gz'

    segmented_arr = nib_load(embryo_name_tp_path).astype(int)
    # .transpose([2, 1, 0])

    start_time = time.time()
    # -----!!!!!!!!get cell edge boundary!!!!--------------
    cell_bone_mask = np.zeros(segmented_arr.shape)
    # start_time=time.time()
    for cell_idx in np.unique(segmented_arr)[1:]:
        this_cell_arr = (segmented_arr == cell_idx)
        this_cell_arr_dialation = ndimage.binary_dilation(this_cell_arr, iterations=1)
        cell_bone_mask[np.logical_xor(this_cell_arr_dialation, this_cell_arr)] = 1
    print('edge boundary timing', time.time() - start_time)

    # cell_mask = segmented_arr != 0
    # boundary_mask_tmp = np.logical_xor(cell_mask == 0 , ndimage.binary_dilation(cell_mask))
    # boundary_mask=np.zeros(segmented_arr.shape)
    # boundary_mask[boundary_mask_tmp]=1
    #
    # nib_save(cell_bone_mask,r'./test_1.nii.gz')
    # print((cell_bone_mask==1).sum())
    # nib_save(boundary_mask,r'./test_2.nii.gz')
    # print((boundary_mask==1).sum())

    [x_bound, y_bound, z_bound] = np.nonzero(cell_bone_mask)
    boundary_elements = []

    # find boundary/points between cells
    start_time = time.time()
    for (x, y, z) in zip(x_bound, y_bound, z_bound):
        neighbors = segmented_arr[np.ix_(range(x - 1, x + 2), range(y - 1, y + 2), range(z - 1, z + 2))]
        neighbor_labels = list(np.unique(neighbors))[1:]  # with order
        # print(neighbor_labels)
        # if 0 in neighbor_labels:
        #     neighbor_labels.remove(0)
        if len(neighbor_labels) == 2:  # contact between two cells
            boundary_elements.append(sorted(neighbor_labels))
    print('getting contact pairs', time.time() - start_time)

    # cell contact pairs
    cell_contact_pairs = list(np.unique(np.array(boundary_elements), axis=0))
    # cell_contact_pair_renew = []

    volume_dict = {}
    surface_dict = {}
    contact_dict = {}
    weight_surface = 1.2031  # !1.2031... is derived by other papers

    start_time = time.time()
    for (label1, label2) in cell_contact_pairs:
        contact_mask_tmp = np.logical_and(ndimage.binary_dilation(segmented_arr == label1),
                                          ndimage.binary_dilation(segmented_arr == label2))
        contact_mask = np.logical_and(contact_mask_tmp, cell_bone_mask)
        contact_sum = contact_mask.sum()
        if contact_sum > 2:
            # cell_contact_pair_renew.append((label1, label2))
            str_key = str(label1) + '_' + str(label2)
            # contact_area_dict[str_key] = 0
            contact_dict[str_key] = contact_sum * weight_surface
    print('get pair contact surface', time.time() - start_time)

    cell_list = np.unique(segmented_arr)
    for cell_key in cell_list:
        if cell_key != 0:
            this_cell_mask = np.logical_xor(ndimage.binary_dilation(segmented_arr == cell_key),
                                            (segmented_arr == cell_key))
            # if is_debug:
            #     print('-------',cell_key,'---------')
            #     print('surface num',(cell_mask==1).sum())
            #     print('inside sum',(volume == cell_key).sum())
            volume_dict[cell_key] = (segmented_arr == cell_key).sum()
            surface_dict[cell_key] = this_cell_mask.sum() * weight_surface  # 1.2031... is derived by other papers
            irregularity = surface_dict[cell_key] ** (1 / 2) / volume_dict[cell_key] ** (1 / 3)

            if irregularity < 2.199085:
                print('irregularity   ', irregularity)
                print('impossible small surface', time_point, cell_key)

            # total_cell_contact=0
            # for (cell1, cell2) in cell_contact_pair_renew:
            #     idx = str(cell1) + '_' + str(cell2)
            #     # idx_test=
            #     if cell_key in (cell1, cell2):
            #         this_contact_area = contact_dict[idx]
            #         total_cell_contact += this_contact_area
            #     # --------------------contact-----------------------------------------
            # print(surface_dict[cell_key],total_cell_contact,time_point, cell_key)

    path_tmp = os.path.join(stat_data_path, embryo_name)
    check_folder(path_tmp)
    with open(os.path.join(path_tmp, file_name.split('.')[0] + '_volume.txt'), 'wb+') as handle:
        pickle.dump(volume_dict, handle, protocol=4)
    with open(os.path.join(path_tmp, file_name.split('.')[0] + '_surface.txt'), 'wb+') as handle:
        pickle.dump(surface_dict, handle, protocol=4)
    with open(os.path.join(path_tmp, file_name.split('.')[0] + '_contact.txt'), 'wb+') as handle:
        pickle.dump(contact_dict, handle, protocol=4)

    # -------------------------------------------------------------------------------------------------------




if __name__ == '__main__':
    # is_generate_cell_wise_gui_data= True # depulicate all raw images and segmented files for ITK-SNAP-CVE software

    # =====================calculate volume surface contact=====================================
    # embryo_names = ['Emb1','Emb2','Emb3','Emb4','Emb5']
    #bias_this=0

    embryo_names = ['Uncompressed2']
    bias_this=117

    # embryo_names = ['compress1', 'Compressed2', 'Uncompressed1']
    # bias_this=0

    # cell_identity_assigned_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\seg_result\seg_cell'
    # annotated_root_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\seg_result\cd files'
    # name_dictionary_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\seg_result\name_dictionary.csv'

    cell_identity_assigned_path = r'H:\EmbSAM\revision\4data\dividing_segcell'
    annotated_root_path = r'H:\EmbSAM\revision\4data\cdfiles'
    name_dictionary_path = r'H:\EmbSAM\revision\4data\name_dictionary.csv'
    # cell_fate_dictionary = r'/home/cimda/INNERDisk1/ZELIN_MEMB_DATA/CMap CSahepr 34 packed membrane nucleus/CellFate.xls'

    stat_path = os.path.join(cell_identity_assigned_path, 'Statistics')

    label_name_dict = pd.read_csv(name_dictionary_path, index_col=0).to_dict()['0']
    name_label_dict = {value: key for key, value in label_name_dict.items()}

    for idx, embryo_name in enumerate(embryo_names):
        # =======================calculate volume surface and contact, take long time=========================
        configs = []
        this_embryo_segmented_files = sorted(glob(os.path.join(cell_identity_assigned_path, embryo_name, '*nii.gz')))
        #
        max_time = len(this_embryo_segmented_files)

        for file_path in this_embryo_segmented_files:
            # config_tmp['time_point'] = tp
            configs.append([file_path,stat_path])
        mp_cpu_num = min(len(configs), mp.cpu_count() // 2)

        # mp_cpu_num = min(len(configs), 1)

        mpPool = mp.Pool(mp_cpu_num)
        print('total ',mp.cpu_count(), 'cpu, we create ', mp_cpu_num)
        for idx_, _ in enumerate(
                tqdm(mpPool.imap_unordered(calculate_cell_surface_and_contact_points, configs), total=len(this_embryo_segmented_files),
                     desc="calculating {} segmentations (contact, surface, volume)".format(embryo_name))):
            #
            pass
        # ===========================================================================================

        # ===============================just group them into readable csv===============================
        save_the_morphological_and_nuc_location_file(name_dictionary_path, embryo_name, max_time,
                                                     annotated_root_path,
                                                     # os.path.join(annotated_root_path, embryo_name),
                                                     stat_path, raw_z_resolution=68, z_resolution=160,
                                                     three_d_resolution=0.18,cd_file_segmented_bias=bias_this)
        # ===============================================================================================

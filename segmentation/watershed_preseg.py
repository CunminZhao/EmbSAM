import multiprocessing as mp
from tqdm import tqdm
import glob
import os
import numpy as np
from scipy import ndimage
from scipy.stats import mode
from skimage.segmentation import watershed

from segmentation.ProcessLib import construct_weighted_graph, set_boundary_zero
from utils.data_io import nib_load, nib_save



def instance_seg_for_binary(parameters_this, local_max_h=4):
    print('binary membrane ->> instance segmentation is_nuc_labelled False')
    segMemb_file_path = parameters_this[0]
    #segMemb_file_path='/home/zhaolab/zcm/home/Zelin/190311plc1mp1/feature_fusion/190311plc1mp1/190311plc1mp1_005.nii.gz'
    saving_path_this_file = parameters_this[1]
    #saving_path_this_file='/home/zhaolab/zcm/home/Zelin/190311plc1mp1/feature_fusion/190311plc1mp1'
    embryo_name_tp = '_'.join(os.path.basename(segMemb_file_path).split('.')[0].split('_')[:2])
    image0 = nib_load(segMemb_file_path)
    labels = np.unique(image0)
    assert len(labels) == 2
    image_tmp = image0

    # adjust the direction
    # cell_bin_image = np.transpose(image_tmp, [2, 1, 0])
    cell_bin_image = (image_tmp == 0).astype(np.uint8)

    # ===========================================================
    #               Construct weighted graphload ?
    # ===========================================================
    print('constructing weighted graph load for ', embryo_name_tp)
    point_list, edge_list, edge_weight_list = construct_weighted_graph(cell_bin_image, local_max_h)
    # ===========================================================
    #        CLuster points based on their connections
    # ===========================================================
    # delete all edges that come cross the membrane
    print('clustering all edges and delete crossed memebran edges ', embryo_name_tp)
    valid_edge_list = [edge_list[i] for i in range(len(edge_weight_list)) if edge_weight_list[i] < 10]
    point_tomerge_list0 = []
    for one_edge in valid_edge_list:
        added_flag = 0
        point1 = one_edge[0]
        point2 = one_edge[1]
        for i in range(len(point_tomerge_list0)):
            if (point1 in point_tomerge_list0[i]) or (point2 in point_tomerge_list0[i]):
                point_tomerge_list0[i] = list(set().union([point1, point2], point_tomerge_list0[i]))
                added_flag = 1
                break
        if not added_flag:
            point_tomerge_list0.append([point1, point2])
    # Combine all clusters that have shared vertexs
    cluster_tem1 = point_tomerge_list0 * 1
    cluster_tem2 = point_tomerge_list0 * 1
    point_tomerge_list = []
    merged_cluster = []
    while len(cluster_tem1):
        delete_index = []
        cluster_in1 = cluster_tem1.pop()
        if cluster_in1 in merged_cluster:
            continue
        cluster_final = set(cluster_in1)
        for cluster_in2 in cluster_tem2:
            tem_final = set(cluster_final).intersection(cluster_in2)
            if len(tem_final):
                merged_cluster.append(cluster_in2)
                cluster_final = set().union(cluster_final, cluster_in2)
        point_tomerge_list.append(list(cluster_final))
    # ===========================================================
    #               Seeded watershed segmentation
    # ===========================================================
    print('doing watershed segmentation ', embryo_name_tp)
    marker_volume0 = np.zeros_like(cell_bin_image, dtype=np.uint8)
    tem_point_list = np.transpose(np.array(point_list), [1, 0]).tolist()
    marker_volume0[tem_point_list[0], tem_point_list[1], tem_point_list[2]] = 1
    struc_el1 = np.ones((3, 3, 3), dtype=bool)
    #marker_volume1 = ndimage.morphology.binary_dilation(marker_volume0, structure=struc_el1)
    marker_volume1 = ndimage.binary_dilation(marker_volume0, structure=struc_el1)
    marker_volume = ndimage.label(marker_volume1)[0]
    # EDT on mmembrane-based image
    #memb_edt = ndimage.morphology.distance_transform_edt(cell_bin_image > 0)
    memb_edt = ndimage.distance_transform_edt(cell_bin_image > 0)
    memb_edt_reversed = memb_edt.max() - memb_edt
    # Implement watershed segmentation
    watershed_seg = watershed(memb_edt_reversed, marker_volume.astype(np.uint16), watershed_line=True)
    # ===========================================================
    #  Deal with over segmentation based on clutered local maximum
    # ===========================================================
    print('deleting the over segmentation based on clustered local maximum ', embryo_name_tp)
    merged_seg = watershed_seg.copy()
    for one_merged_points in point_tomerge_list:
        first_point = point_list[one_merged_points[0]]
        one_label = watershed_seg[first_point[0], first_point[1], first_point[2]]
        for other_point in one_merged_points[1:]:
            point_location = point_list[other_point]
            new_label = watershed_seg[point_location[0], point_location[1], point_location[2]]
            merged_seg[watershed_seg == new_label] = one_label
        one_mask = merged_seg == one_label
        one_mask_closed = ndimage.binary_closing(one_mask)
        merged_seg[one_mask_closed != 0] = one_label
    # Set background as 0
    #background_label = mode(merged_seg, axis=None)[0][0]
    background_label = mode(merged_seg, axis=None)[0]
    #目前是这一步报错了
    merged_seg[merged_seg == background_label] = 0
    merged_seg = set_boundary_zero(merged_seg)
    # ===========================================================
    #  Seperate membrane region from the segmentation result
    # ===========================================================
    # cell_without_memb = np.copy(merged_seg)
    # cell_without_memb[memb_bin != 0] = 0
    # ===========================================================
    #  Save final result
    # ===========================================================
    print('Finished: ', embryo_name_tp, 'segMemb ---> segCell !')

    save_name = os.path.join(saving_path_this_file, embryo_name_tp + "_pre_seg.npz")
    np.savez_compressed(save_name, merged_seg)



def run_membrane2cell(seg_memb_root_dir, embryo_names,is_one_by_one=False):
    '''

    :param args: transform binary membrane to separate regions using multiple processes
    :return:
    '''
    print("hi")
    for embryo_name in embryo_names:
        # embryo_average_mask = get_eggshell(raw_image_dir=args.validate_data_path, wide_type_embryo_names=args.predicting_embryos)
        #segmemb_embryos_names = glob.glob(os.path.join(seg_memb_root_dir, embryo_name, '*segMemb.nii.gz'))
        segmemb_embryos_names = glob.glob(os.path.join(seg_memb_root_dir, embryo_name, '*.nii.gz'))
        #saving_path_this_file = os.path.join(r'/home/zhaolab/zcm/home/final_version/SAMFDE-tosubmit/ground_truth/short_interval_output_19xxx/190311plc1mp1_segMemb/',embryo_name)
        saving_path_this_file = os.path.join(seg_memb_root_dir,embryo_name)
        parameters = []
        for file_name in segmemb_embryos_names:
            parameters.append([file_name, saving_path_this_file])

            # segment_membrane([embryo_name, file_name, embryo_mask])
        if is_one_by_one:
            for para in parameters:
                instance_seg_for_binary(para)
                
        else:
            mp_cpu_num = int(mp.cpu_count()/2)
            #mp_cpu_num=20
            print('all cpu process is ', mp.cpu_count(), 'we created ', mp_cpu_num)
            mpPool = mp.Pool(min(len(parameters),mp_cpu_num))
            for _ in tqdm(mpPool.imap_unordered(instance_seg_for_binary, parameters), total=len(parameters),
                          desc="{} membrane --> cell, all cpu process is {}, we created {}".format(embryo_name,
                                                                                                   str(mp.cpu_count()),
                                                                                                   str(mp_cpu_num))):
                pass
                                                                                                       
    print("done")


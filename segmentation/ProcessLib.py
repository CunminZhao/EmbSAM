#  import dependent library
import os
import glob
import random
import numpy as np
from scipy import ndimage, stats
from skimage.morphology import h_maxima, binary_opening, ball
#from scipy.ndimage.morphology import binary_closing, distance_transform_edt
from scipy.ndimage import binary_closing, distance_transform_edt
# from skimage.measure import marching_cubes_lewiner, mesh_surface_area
from scipy.spatial import Delaunay
# from scipy.stats import mode

# import user defined library
from utils.data_io import nib_load, nib_save


# ================================================================================
#       extra tools
# ================================================================================
#  construct local maximum graph
def construct_weighted_graph(bin_image, local_max_h=2):
    '''
    Construct edge weight graph from binary MembAndNuc.
    :param bin_image: cell binary MembAndNuc
    :return point_list: all points embedded in the triangulation, used for location query
    :return edge_list: list of edges in the triangulation
    :return edge_weight_list: edge weight corresponds to the edge list.
    '''

    volume_shape = bin_image.shape
    #bin_cell = ndimage.morphology.binary_opening(bin_image).astype(np.float32)
    bin_cell = ndimage.binary_opening(bin_image).astype(np.float32)
    bin_memb = bin_cell == 0
    #bin_cell_edt = ndimage.morphology.distance_transform_edt(bin_cell)
    bin_cell_edt = ndimage.distance_transform_edt(bin_cell)
    #
    #print(bin_cell_edt.shape, np.unique(bin_cell_edt))
    #
    # get local maximum mask
    local_maxima_mask = h_maxima(bin_cell_edt, local_max_h)
    [maxima_x, maxima_y, maxima_z] = np.nonzero(local_maxima_mask)
    #  find boundary points to force large weight
    x0 = np.where(maxima_x == 0)[0]
    x1 = np.where(maxima_x == volume_shape[0] - 1)[0]
    y0 = np.where(maxima_y == 0)[0]
    y1 = np.where(maxima_y == volume_shape[1] - 1)[0]
    z0 = np.where(maxima_z == 0)[0]
    z1 = np.where(maxima_z == volume_shape[2] - 1)[0]
    b_indx = np.concatenate((x0, y0, z0, x1, y1, z1), axis=None).tolist()

    point_list = np.stack((maxima_x, maxima_y, maxima_z), axis=1)
    tri_of_max = Delaunay(point_list)
    triangle_list = tri_of_max.simplices
    edge_list = []
    for i in range(triangle_list.shape[0]):
        for j in range(triangle_list.shape[1] - 1):
            edge_list.append([triangle_list[i][j - 1], triangle_list[i][j]])
        edge_list.append([triangle_list[i][j], triangle_list[i][0]])
    # add edges for all boundary points
    for i in range(len(b_indx)):
        for j in range(i, len(b_indx)):
            one_point = b_indx[i]
            another_point = b_indx[j]
            if ([one_point, another_point] in edge_list) or ([another_point, one_point] in edge_list):
                continue
            edge_list.append([one_point, another_point])

    weights_volume = bin_memb * 10000  # construct weights volume for graph
    edge_weight_list = []
    for one_edge in edge_list:
        start_x0 = point_list[one_edge[0]]
        end_x1 = point_list[one_edge[1]]
        if (one_edge[0] in b_indx) and (one_edge[1] in b_indx):
            edge_weight = 0  # All edges between boundary points are set as zero
        elif (one_edge[0] in b_indx) or (one_edge[1] in b_indx):
            edge_weight = 10000 * 10
        else:
            edge_weight = line_weight_integral(start_x0, end_x1, weights_volume)

        edge_weight_list.append(edge_weight)

    return point_list.tolist(), edge_list, edge_weight_list


#  integrate along a line
def line_weight_integral(x0, x1, weight_volume):
    # find all points between start and end
    inline_points = all_points_inline(x0, x1)
    points_num = inline_points.shape[0]
    line_weight = 0
    for i in range(points_num):
        point_weight = weight_volume[inline_points[i][0],
        inline_points[i][1],
        inline_points[i][2]]
        line_weight = line_weight + point_weight

    return line_weight


#  get all lines along a point
def all_points_inline(x0, x1):
    d = np.diff(np.array((x0, x1)), axis=0)[0]
    j = np.argmax(np.abs(d))
    D = d[j]
    aD = np.abs(D)
    return x0 + (np.outer(np.arange(aD + 1), d) + (aD >> 1)) // aD

    # backup points that should be labelled together


def combine_background_maximum(point_weight_list):
    point_tomerge_list0 = []
    for one_edge in point_weight_list:
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

    return point_tomerge_list0

    #  combine local maximums inside the embryo


def combine_inside_maximum(cluster1, cluster2):
    point_tomerge_list = []
    merged_cluster = []
    while len(cluster1):
        delete_index = []
        cluster_in1 = cluster1.pop()
        if cluster_in1 in merged_cluster:
            continue
        cluster_final = set(cluster_in1)
        for cluster_in2 in cluster2:
            tem_final = set(cluster_final).intersection(cluster_in2)
            if len(tem_final):
                merged_cluster.append(cluster_in2)
                cluster_final = set().union(cluster_final, cluster_in2)
        point_tomerge_list.append(list(cluster_final))
    return point_tomerge_list


#  reverse over-segmentation with merged maximum.
def reverse_seg_with_max_cluster(watershed_seg, init_list, max_cluster):
    merged_seg = watershed_seg.copy()
    for one_merged_points in max_cluster:
        first_point = init_list[one_merged_points[0]]
        one_label = watershed_seg[first_point[0], first_point[1], first_point[2]]
        for other_point in one_merged_points[1:]:
            point_location = init_list[other_point]
            new_label = watershed_seg[point_location[0], point_location[1], point_location[2]]
            merged_seg[watershed_seg == new_label] = one_label
        one_mask = merged_seg == one_label
        one_mask_closed = ndimage.binary_closing(one_mask)
        merged_seg[one_mask_closed != 0] = one_label

    return merged_seg


#  set all boundary torched labels as zero
def set_boundary_zero(pre_seg):
    '''
    SET_BOUNARY_ZERO is used to set all segmented regions attached to the boundary as zero background.
    :param pre_seg:
    :return:
    '''
    opened_mask = binary_opening(pre_seg)
    pre_seg[opened_mask == 0] = 0
    seg_shape = pre_seg.shape
    boundary_mask = np.zeros_like(pre_seg, dtype=np.uint8)
    boundary_mask[0:2, :, :] = 1;
    boundary_mask[:, 0:2, :] = 1;
    boundary_mask[:, :, 0:2] = 1
    boundary_mask[seg_shape[0] - 1:, :, :] = 1;
    boundary_mask[:, seg_shape[1] - 1:, :] = 1;
    boundary_mask[:, :, seg_shape[2] - 1:] = 1
    boundary_labels = np.unique(pre_seg[boundary_mask != 0])
    for boundary_label in boundary_labels:
        pre_seg[pre_seg == boundary_label] = 0

    return pre_seg


#   filter over-segmentation with binary nucleus loc
def cell_filter_with_nucleus(cell_seg, nuc_seg):
    init_all_labels = np.unique(cell_seg).tolist()
    keep_labels = (np.unique(cell_seg[nuc_seg > 0])).tolist()
    filtered_labels = list(set(init_all_labels) - set(keep_labels))
    for label in filtered_labels:
        cell_seg[cell_seg == label] = 0

    return cell_seg


def get_largest_connected_region(embryo_mask):
    label_structure = np.ones((3, 3, 3))
    #embryo_mask = ndimage.morphology.binary_closing(embryo_mask, structure=label_structure)
    embryo_mask = ndimage.binary_closing(embryo_mask, structure=label_structure)
    [labelled_regions, _] = ndimage.label(embryo_mask, label_structure)
    count_label = np.bincount(labelled_regions.flat)
    count_label[0] = 0
    valid_edt_mask0 = (labelled_regions == np.argmax(count_label))
    #valid_edt_mask0 = ndimage.morphology.binary_closing(valid_edt_mask0)
    valid_edt_mask0 = ndimage.binary_closing(valid_edt_mask0)

    return valid_edt_mask0.astype(np.uint8)


def delete_isolate_labels(discrete_edt):
    '''
    delete all unconnected binary SegMemb
    '''
    label_structure = np.ones((3, 3, 3))
    [labelled_edt, _] = ndimage.label(discrete_edt, label_structure)

    # get the largest connected label
    [most_label, _] = stats.mode(labelled_edt[discrete_edt == discrete_edt.max()], axis=None)

    valid_edt_mask0 = (labelled_edt == most_label[0])
    #valid_edt_mask = ndimage.morphology.binary_closing(valid_edt_mask0, iterations=2)
    valid_edt_mask = ndimage.binary_closing(valid_edt_mask0, iterations=2)
    filtered_edt = np.copy(discrete_edt)
    filtered_edt[valid_edt_mask == 0] = 0

    return filtered_edt


# ================================================================
#   get egg shell ZELIN: I DONT KNOW WHAT IS THIS
# ================================================================
def get_eggshell(raw_image_dir, wide_type_embryo_names, wide_type_name, hollow=False):
    '''
    Get eggshell of specific embryo
    :param embryo_name:
    :return:
    '''
    # wide_type_folder = os.path.join(raw_image_dir, wide_type_name, "RawMemb")
    embryo_tp_list = glob.glob(os.path.join(raw_image_dir, "*.nii.gz"))
    random.shuffle(embryo_tp_list)
    overlap_num = 15 if len(embryo_tp_list) > 15 else len(embryo_tp_list)
    embryo_sum = nib_load(embryo_tp_list[0]).astype(np.float32)
    for tp_file in embryo_tp_list[1:overlap_num]:
        embryo_sum += nib_load(tp_file)

    embryo_mask = otsu3d(embryo_sum)
    embryo_mask = get_largest_connected_region(embryo_mask)
    embryo_mask[0:2, :, :] = False
    embryo_mask[:, 0:2, :] = False
    embryo_mask[:, :, 0:2] = False
    embryo_mask[-3:, :, :] = False
    embryo_mask[:, -3:, :] = False
    embryo_mask[:, :, -3:] = False
    if hollow:
        #dilated_mask = ndimage.morphology.binary_dilation(embryo_mask, np.ones((3, 3, 3)), iterations=2)
        dilated_mask = ndimage.binary_dilation(embryo_mask, np.ones((3, 3, 3)), iterations=2)
        #ndimage.binary_dilation
        eggshell_mask = np.logical_and(dilated_mask, ~embryo_mask)
        return eggshell_mask.astype(np.uint8)
    return embryo_mask.astype(np.uint8)


def otsu3d(gray):
    # raw membrane gii.gz
    pixel_number = gray.shape[0] * gray.shape[1] * gray.shape[2]
    mean_weigth = 1.0 / pixel_number
    his, bins = np.histogram(gray, np.arange(0, 257))
    final_thresh = -1
    final_value = -1
    intensity_arr = np.arange(256)
    for t in bins[1:-1]:  # This goes from 1 to 254 uint8 range (Pretty sure wont be those values)
        pcb = np.sum(his[:t])
        pcf = np.sum(his[t:])
        Wb = pcb * mean_weigth
        Wf = pcf * mean_weigth

        mub = np.sum(intensity_arr[:t] * his[:t]) / float(pcb)
        muf = np.sum(intensity_arr[t:] * his[t:]) / float(pcf)
        # print mub, muf
        value = Wb * Wf * (mub - muf) ** 2

        if value > final_value:
            final_thresh = t
            final_value = value
    final_img = gray.copy()
    final_img[gray > final_thresh] = 1
    final_img[gray < final_thresh] = 0
    return final_img



def combine_division_mp(para):
    embryo = para[0]
    memb_file = para[1]
    nuc_file = para[2]
    cell_file = para[3]
    cell_tree = para[4]
    overwrite = para[5]
    number_dict = para[6]
    name_dict = para[7]

    t = int(filename2t(memb_file))

    seg_map = nib_load(memb_file)
    seg_bin = (seg_map > 0.93 * seg_map.max()).astype(np.float32)
    seg_nuc = nib_load(nuc_file)
    seg_cell = nib_load(cell_file)

    labels = np.unique(seg_nuc).tolist()
    labels.pop(0)
    processed_labels = []
    output_seg_cell = seg_cell.copy()
    cell_labels = np.unique(seg_cell).tolist()

    for one_label in labels:
        one_times = cell_tree[name_dict[one_label]].data.get_time()
        if any(time < t for time in one_times):  # if previous division exist
            continue
        if (one_label in processed_labels):
            continue
        parent_label = cell_tree.parent(name_dict[one_label])
        if parent_label is None:
            continue
        another_label = [number_dict[a.tag] for a in cell_tree.children(parent_label.tag)]
        another_label.remove(one_label)
        another_label = another_label[0]

        if (one_label not in cell_labels) or (another_label not in cell_labels):
            continue

        x0 = np.stack(np.where(seg_nuc == one_label)).squeeze().tolist()
        x1 = np.stack(np.where(seg_nuc == another_label)).squeeze().tolist()
        edge_weight = line_weight_integral(x0=x0, x1=x1, weight_volume=seg_bin)
        if edge_weight == 0:
            mask = np.logical_or(seg_cell == one_label, seg_cell == another_label)
            mask = binary_closing(mask, structure=np.ones((3, 3, 3)))
            output_seg_cell[mask] = number_dict[parent_label.tag]
            one_times.remove(t)
            another_times = cell_tree[name_dict[another_label]].data.get_time()
            another_times.remove(t)
            cell_tree[name_dict[one_label]].data.set_time(one_times)
            cell_tree[name_dict[another_label]].data.set_time(another_times)
        processed_labels += [one_label, another_label]

    if not overwrite:
        seg_save_file = os.path.join("./output", embryo, "SegCellTimeCombined",
                                     embryo + "_" + str(t).zfill(3) + "_segCell.nii.gz")
    else:
        seg_save_file = cell_file
    nib_save(output_seg_cell, seg_save_file)


# get t from file name
def filename2t(filename):
    base_name = os.path.basename(filename)

    return int(base_name.split("_")[1])


def line_weight_integral(x0, x1, weight_volume):
    # find all points between start and end
    inline_points = all_points_inline(x0, x1).astype(np.uint16)
    points_num = inline_points.shape[0]
    line_weight = 0
    for i in range(points_num):
        point_weight = weight_volume[inline_points[i][0],
        inline_points[i][1],
        inline_points[i][2]]
        line_weight = line_weight + point_weight
    return line_weight


import numpy as np

import os.path
import time
from glob import glob
import numpy as np
from scipy import ndimage
import pickle
import pandas as pd
import seaborn as sns

import matplotlib.pyplot as plt

from utils.data_io import nib_load


def fit_sphere(xs, ys, zs):
    """
    Fit a sphere to the points (xs, ys, zs) via linear least squares.
    Returns (center, radius).
    """
    # Assemble A · p = b, where p = [2*xc, 2*yc, 2*zc, (r^2 - xc^2 - yc^2 - zc^2)]
    A = np.column_stack((xs, ys, zs, np.ones_like(xs)))
    b = xs**2 + ys**2 + zs**2

    # Solve for p in the least‐squares sense
    p, *_ = np.linalg.lstsq(A, b, rcond=None)
    a, b, c, d = p

    # Recover sphere center (xc, yc, zc)
    center = np.array([a, b, c]) / 2.0

    # Recover radius: r = sqrt(xc^2 + yc^2 + zc^2 + d)
    radius = np.sqrt(np.dot(center, center) + d)

    return center, radius


def calculate_curvature_direction():

    embryo_names=['Emb5']

    gui_root_path=r'H:\EmbSAM\revision\ITK-SNAP-CVE Data'

    name_dictionary_path = r'H:\EmbSAM\revision\4data\GUIData\name_dictionary.csv'
    statistic_morphology_root_path=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\EmbSAM\seg_result\seg_cell\Statistics'
    label_name_dict = pd.read_csv(name_dictionary_path, index_col=0).to_dict()['0']
    name_label_dict = {value: key for key, value in label_name_dict.items()}

    target_contact_pairs = [
        # ('ABplp', 'E'), ('ABplp', 'Ep'), ('ABplp', 'Ea'),
                            ('C', 'ABpr'), ('C', 'ABpra'),('C', 'ABprp'),
                            # ('MS', 'ABpl'),('MS', 'ABpla'),('MS', 'ABplp'),
                            ]
    for embryo_name in embryo_names:
        curvature_dict = {}

        embryo_tp_list=sorted(glob(os.path.join(gui_root_path,embryo_name,'SegCell','*.nii.gz')))
        for idx, embryo_name_tp_path in enumerate(embryo_tp_list):
            print(embryo_name_tp_path)
            segmented_arr = nib_load(embryo_name_tp_path).astype(int)

            positive_cell_anchor='AB'

            target_contact_label_pairs = []
            for target_contact_pair in target_contact_pairs:
                cell_name1, cell_name2 = target_contact_pair
                cell_label1 = name_label_dict[cell_name1]
                cell_label2 = name_label_dict[cell_name2]

                target_contact_label_pairs.append(str(cell_label1)+'_'+str(cell_label2))
                target_contact_label_pairs.append(str(cell_label2)+'_'+str(cell_label1))

            contact_stat_file_path=os.path.join(statistic_morphology_root_path,embryo_name,'{}_{}_contact.txt'.format(embryo_name,str(idx+1).zfill(3)))
            # print(os.path.exists(contact_stat_file_path))
            with open(contact_stat_file_path,'rb') as handle:
                contact_dict = pickle.load(handle)
            # print(set(target_contact_label_pairs),set(contact_dict.keys()))

            if not bool(set(target_contact_label_pairs) & set(contact_dict.keys())):
                continue

            # print(set(target_contact_label_pairs),set(contact_dict.keys()))

            start_time = time.time()
            # -----!!!!!!!!get all cell edge boundary!!!!--------------
            cell_bone_mask = np.zeros(segmented_arr.shape)
            # start_time=time.time()
            for cell_idx in np.unique(segmented_arr)[1:]:
                this_cell_arr = (segmented_arr == cell_idx)
                this_cell_arr_dialation = ndimage.binary_dilation(this_cell_arr, iterations=1)
                cell_bone_mask[np.logical_xor(this_cell_arr_dialation, this_cell_arr)] = 1
            # print('edge boundary timing', time.time() - start_time)

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
            # print('getting contact pairs', time.time() - start_time)
            # ----------------------------------------------------------------------

            # cell contact pairs
            cell_contact_pairs = list(np.unique(np.array(boundary_elements), axis=0))
            # print(cell_contact_pairs)
            # print(target_contact_label_pairs)
            # cell_contact_pair_renew = []


            start_time = time.time()
            for (label1, label2) in cell_contact_pairs:
                if str(label1)+'_'+str(label2) in target_contact_label_pairs:
                    contact_mask_tmp = np.logical_and(ndimage.binary_dilation(segmented_arr == label1),
                                                      ndimage.binary_dilation(segmented_arr == label2))
                    contact_mask = np.logical_and(contact_mask_tmp, cell_bone_mask)
                    [x_pts, y_pts, z_pts] = np.nonzero(contact_mask)
                    # fit sphere
                    center_est, radius_est = fit_sphere(x_pts, y_pts, z_pts)
                    print(label1,label2)
                    print(f"Estimated center: {center_est}")
                    print(f"Estimated radius: {radius_est:.4f}")

                    # contact_surface_centroid=np.array([x_pts, y_pts, z_pts]).mean(axis=0)
                    # M = np.array([x_pts, y_pts, z_pts]) - contact_surface_centroid  # (N,3)
                    # _, _, Vt = np.linalg.svd(M, full_matrices=False)
                    # normal = Vt[-1]  # 对应最小奇异值的右奇异向量

                    name1=label_name_dict[label1]
                    name2=label_name_dict[label2]

                    this_cell_arr1 = (segmented_arr == label1)
                    [x_pts_1, y_pts_1, z_pts_1] = np.nonzero(this_cell_arr1)
                    x1=sum(x_pts_1)/len(x_pts_1)
                    y1=sum(y_pts_1)/len(y_pts_1)
                    z1=sum(z_pts_1)/len(z_pts_1)
                    distance1=((center_est[0]-x1)**2+(center_est[1]-y1)**2+(center_est[2]-z1)**2)**(1/2)

                    this_cell_arr2 = (segmented_arr == label2)
                    [x_pts_2, y_pts_2, z_pts_2] = np.nonzero(this_cell_arr2)
                    x2 = sum(x_pts_2) / len(x_pts_2)
                    y2 = sum(y_pts_2) / len(y_pts_2)
                    z2 = sum(z_pts_2) / len(z_pts_2)
                    distance2=((center_est[0]-x2)**2+(center_est[1]-y2)**2+(center_est[2]-z2)**2)**(1/2)

                    if distance1>distance2:
                        if name1.startswith(positive_cell_anchor):
                            curvature_dict[embryo_name+'_'+str(idx+1)+'_'+name1+'_'+name2]=-1/radius_est
                        else:
                            curvature_dict[embryo_name+'_'+str(idx+1)+'_'+name2+'_'+name1]=1/radius_est
                    else: # distance1<=distance2
                        if name1.startswith(positive_cell_anchor):
                            curvature_dict[embryo_name+'_'+str(idx+1)+'_'+name1+'_'+name2]=1/radius_est
                        else:
                            curvature_dict[embryo_name+'_'+str(idx+1)+'_'+name2+'_'+name1]=-1/radius_est

            print('get surface curvature', time.time() - start_time)
        print(curvature_dict)
        with open(os.path.join(r'H:\EmbSAM\revision',  '{}_{}_curvature.txt'.format('_'.join(target_contact_pairs[0]),embryo_name)), 'wb+') as handle:
            pickle.dump(curvature_dict, handle, protocol=4)

def plot_curvature():
    target_pairs = [
        'ABplp_E', 'ABplp_Ea','ABplp_Ep',
                    # 'ABpr_C', 'ABpra_C','ABprp_C',
                    # 'ABpl_MS', 'ABpla_MS'
                    ]
    embryo_name='Emb5'
    with open(os.path.join(r'H:\EmbSAM\revision',  '{}_curvature.txt'.format(embryo_name)), 'rb') as handle:
        curvature_dict = pickle.load(handle)
    curvature_pd=pd.DataFrame(columns=['Embryo Name','Cell-Cell Contact','Curvature','Time Point'])

    #  'ABplp_E',
    nucleus_dividing_timepoint=173
    membrane_dividing_timepoint=183
    direction=1

    #   'C_ABpr',
    # nucleus_dividing_timepoint = 127
    # membrane_dividing_timepoint = 135
    # direction = -1

    for key_this, value in curvature_dict.items():
        [embryo_name,time_point,contact_name1,contact_name2]=key_this.split('_')
        if int(time_point)>membrane_dividing_timepoint:
            continue
        if contact_name1+'_'+contact_name2 in target_pairs:
            curvature_pd.loc[len(curvature_pd)]=[embryo_name,contact_name1+'-'+contact_name2,value*direction/0.18,(int(time_point)-nucleus_dividing_timepoint)*10]

    ax = sns.lineplot(curvature_pd, x='Time Point', y='Curvature', hue='Cell-Cell Contact')
    font_size = 16

    sns.set(font="Arial")

    # sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    # sns.move_legend(ax, "upper right",fontsize=font_size)


    plt.xticks(fontsize=font_size, family='Arial')
    plt.yticks(fontsize=font_size, family='Arial')

    plt.xlabel("Time (s)", size=font_size, family='Arial')
    plt.ylabel(r'Curvature ($\rm \mu m^{-1}$)', size=font_size, family='Arial')

    # plt.title('Post 4-cell Stage',size=24,family='Arial')
    plt.savefig(embryo_name + target_pairs[0]+"_curvature" + ".pdf", format="pdf", dpi=300)
    plt.show()

# Example usage
if __name__ == "__main__":
    plot_curvature()
    # calculate_curvature_direction()

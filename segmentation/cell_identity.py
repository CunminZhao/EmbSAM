import pandas as pd
import numpy as np
from scipy.ndimage import zoom
import os
import shutil
import nibabel as nib
from .binarytree import *


#def extract_coordinates(csv_file_path, timepoint):
    #df = pd.read_csv(csv_file_path)
    #timepoint_df = df[df['time'] == timepoint]
    #coordinates_dict = {row['cell']: (int(row['y']/2), int(row['x']/2), int(row['z']*2.35)) for index, row in timepoint_df.iterrows()}
    #return coordinates_dict

def extract_coordinates(csv_file_path, timepoint, ratio):
    df = pd.read_csv(csv_file_path)
    timepoint_df = df[df['time'] == timepoint]
    coordinates_dict = {row['cell']: (int(row['y']/ratio[0]), int(row['x']/ratio[1]), int(row['z']*ratio[2])) for index, row in timepoint_df.iterrows()}
    return coordinates_dict




def divide_embryo(npz_file_path, coordinate, output_name, output_directory, target_shape):
    #npz_data = np.load(npz_file_path)
    #nii_data = npz_data['arr_0']
    img = nib.load(npz_file_path)
    nii_data = img.get_fdata()
    x, y, z = coordinate
    target_value = nii_data[x, y, z]
    #modified
    if target_value!=0:
        nii_data[nii_data != target_value] = 0
    else:
        nii_data[nii_data != 0] = 0
    #here

    
    zoom_factors = [t / float(s) for t, s in zip(target_shape, nii_data.shape)]
    resized_data = zoom(nii_data, zoom_factors, order=1)

    
    resized_data[resized_data != 0] = target_value
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_path = os.path.join(output_directory, output_name)
    
    nifti_img = nib.Nifti1Image(resized_data, affine=np.eye(4))
    nib.save(nifti_img, output_path)
    #np.savez_compressed(output_path, arr_0=resized_data)
    
    return (output_name, target_value, (x, y, z))



def merge_dividing(first_file_path, second_file_path, output_file_name):
    if not os.path.exists(first_file_path):
        raise FileNotFoundError(f"The file1 {first_file_path} does not exist.")
    
    if not os.path.exists(second_file_path):
        raise FileNotFoundError(f"The file2 {second_file_path} does not exist.")

    output_file_path = os.path.join(os.path.dirname(first_file_path), output_file_name)
    shutil.move(first_file_path, output_file_path)
    print(f"Renamed {first_file_path} to {output_file_path}")

    os.remove(second_file_path)



def find_paired_keys_binarytree(input_dict):

    paired_results = [] 
    added = set()       

    for key in input_dict:
        result = binarytree(key)
        if result and len(result) > 0:
            candidate = result[0]

            if candidate in input_dict and candidate != key:

                pair = tuple(sorted([key, candidate]))
                if pair not in added:
                    added.add(pair)

                    paired_results.append((pair, (input_dict[pair[0]], input_dict[pair[1]])))
    return paired_results


def merge_cell_name(paired_results, niigz_file):

    img = nib.load(niigz_file)
    data = img.get_fdata()  

    results = []

    for pair_keys, coords in paired_results:

        p1, p2 = np.array(coords[0]), np.array(coords[1])
        

        distance = np.linalg.norm(p2 - p1)
        n_steps = int(np.ceil(distance)) + 1 
        
        xs = np.linspace(p1[0], p2[0], num=n_steps)
        ys = np.linspace(p1[1], p2[1], num=n_steps)
        zs = np.linspace(p1[2], p2[2], num=n_steps)
        
        xs = np.rint(xs).astype(int)
        ys = np.rint(ys).astype(int)
        zs = np.rint(zs).astype(int)
        
        line_coords = list(zip(xs, ys, zs))
        valid_coords = []
        shape = data.shape
        for x, y, z in line_coords:
            if 0 <= x < shape[0] and 0 <= y < shape[1] and 0 <= z < shape[2]:
                valid_coords.append((x, y, z))
        
        pixel_values = [data[x, y, z] for (x, y, z) in valid_coords]
        
        nonzero_pixels = [val for val in pixel_values if val != 0]
        unique_vals = np.unique(nonzero_pixels)
        
        if len(unique_vals) == 1:
            bt_result = binarytree(pair_keys[0])
            output = bt_result[1] if len(bt_result) > 1 else None
        else:
            output = "no"
        
        results.append((pair_keys, output))
    
    return results



def update_coordinates_from_merged(results, coordinates):

    for pair_keys, output in results:

        if output != "no":
            key1, key2 = pair_keys[0], pair_keys[1]

            new_key = binarytree(key1)[1]

            if key1 in coordinates:
                temp_value = coordinates[key1]

                del coordinates[key1]

                coordinates[new_key] = temp_value
            if key2 in coordinates:
                del coordinates[key2]
    return coordinates



def merge_dividing_cell_by_coordinates(input_dict, niigz_file):

    paired_results = find_paired_keys_binarytree(input_dict)

    results = merge_cell_name(paired_results, niigz_file)

    updated_coordinates = update_coordinates_from_merged(results, input_dict)
    
    return updated_coordinates


import pandas as pd
import numpy as np
from scipy.ndimage import zoom
import os
import shutil



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
    npz_data = np.load(npz_file_path)
    nii_data = npz_data['arr_0']
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
    np.savez_compressed(output_path, arr_0=resized_data)
    
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

import os
import nibabel as nib
import numpy as np
#from tqdm import tqdm
from scipy import ndimage
from scipy.ndimage import gaussian_filter, binary_fill_holes
import glob



def gaussian(input_path, output_path, smooth_factor=2, cutoff=0.5, lower_factor=0.2, upper_factor=0.9):
    img = nib.load(input_path)
    data = img.get_fdata()

    ##
    z_dim = data.shape[2]
    lower_index = int(np.ceil(z_dim * lower_factor))
    upper_index = int(np.floor(z_dim * upper_factor))
    
    data[:, :, :lower_index] = 0
    data[:, :, upper_index:] = 0
    ##
    
    binary_data = (data > 0).astype(np.int32)
    smoothed = gaussian_filter(binary_data.astype(float), sigma=smooth_factor)
    smoothed_binary = (smoothed > cutoff).astype(np.int32)
    
    smoothed_binary[:, :, -5:] = 0
    smoothed_binary[:, :, :5] = 0
    new_img = nib.Nifti1Image(smoothed_binary, img.affine, img.header)
    nib.save(new_img, output_path)



def process_gaussian(input_folder, output_folder,p1,p2, lower_factor=0.2, upper_factor=0.9):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.nii.gz') and not file_name.startswith('._'):
            input_filepath = os.path.join(input_folder, file_name)
            output_filepath = os.path.join(output_folder, file_name)

            gaussian(input_filepath, output_filepath,p1,p2, lower_factor, upper_factor)



def largest_region(niigz_file_path, output_path):
    nii_img = nib.load(niigz_file_path)
    data = nii_img.get_fdata()

    data = (data > 0.5).astype(np.int_)
    labeled_array, num_features = ndimage.label(data)
    if num_features == 0:
        nib.save(nii_img, output_path)
        print("No connected regions found. Original image saved.")
        return

    sizes = ndimage.sum(data, labeled_array, range(1, num_features + 1))
    largest_cc_label = np.argmax(sizes) + 1
    data[labeled_array != largest_cc_label] = 0
    new_nii_img = nib.Nifti1Image(data, affine=nii_img.affine, header=nii_img.header)
    nib.save(new_nii_img, output_path)



def process_largest(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.nii.gz') and not file_name.startswith('._'):
            input_filepath = os.path.join(input_folder, file_name)
            output_filepath = os.path.join(output_folder, file_name)

            largest_region(input_filepath, output_filepath)



def erode(niigz_file_path, output_path, erosion_factor=12):
    nii_img = nib.load(niigz_file_path)
    data = nii_img.get_fdata()
    binary_data = np.where(data > 0, 1, 0).astype(np.uint8)
    struct_elem = ndimage.generate_binary_structure(3, 3)
    eroded_data = ndimage.binary_erosion(binary_data, structure=struct_elem, iterations=erosion_factor)
    diff_data = binary_data - eroded_data.astype(np.int_)
    new_nii_img = nib.Nifti1Image(diff_data, affine=nii_img.affine, header=nii_img.header)
    nib.save(new_nii_img, output_path)



def process_erode(input_folder, output_folder, E=12):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.nii.gz') and not file_name.startswith('._'):
            input_filepath = os.path.join(input_folder, file_name)
            output_filepath = os.path.join(output_folder, file_name)
            erode(input_filepath, output_filepath, E)



def feature_fuse(folder_A, folder_B, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    files_A = [f for f in os.listdir(folder_A) if (f.endswith('.nii.gz') and not f.startswith('._'))]
    files_B = [f for f in os.listdir(folder_B) if (f.endswith('.nii.gz') and not f.startswith('._'))]

    pairs = set(files_A) & set(files_B)
    
    for file_name in pairs:
        file_path_A = os.path.join(folder_A, file_name)
        file_path_B = os.path.join(folder_B, file_name)

        img_A = nib.load(file_path_A)
        img_B = nib.load(file_path_B)
        data_A = img_A.get_fdata()
        data_B = img_B.get_fdata()
        new_data = data_A + data_B
        new_data = (new_data > 0).astype(np.uint8)
        
        new_img = nib.Nifti1Image(new_data, img_A.affine, img_A.header)
        output_path = os.path.join(output_folder, file_name)
        nib.save(new_img, output_path)



def fill_bubbles(input_directory, output_directory):
    if not input_directory.endswith('/'):
        input_directory += '/'
    if not output_directory.endswith('/'):
        output_directory += '/'
    os.makedirs(output_directory, exist_ok=True)
    for filepath in glob.glob(input_directory + '*.nii.gz'):
        # Load the image
        img = nib.load(filepath)
        data = img.get_fdata()
        if not np.array_equal(data, data.astype(bool)):
            raise ValueError(f"Image {filepath} does not contain only 0's and 1's")

        filled_data = binary_fill_holes(data).astype(np.int16)
        filled_img = nib.Nifti1Image(filled_data, img.affine, img.header)
        output_path = os.path.join(output_directory, os.path.basename(filepath))
        nib.save(filled_img, output_path)



def set_border_zero(folder_path):
    if not os.path.isdir(folder_path):
        print(f"Error: The folder {folder_path} does not exist.")
        return    
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.nii.gz'):
            file_path = os.path.join(folder_path, file_name)
            img = nib.load(file_path)
            data = img.get_fdata()
            #print(data.shape)
            data[:3, :, :] = 0
            data[-3:, :, :] = 0
            data[:, :3, :] = 0
            data[:, -3:, :] = 0
            data[:, :, :3] = 0
            data[:, :, -3:] = 0
            new_img = nib.Nifti1Image(data, img.affine, img.header)
            nib.save(new_img, file_path)   

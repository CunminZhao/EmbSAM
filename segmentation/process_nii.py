import os
import nibabel as nib
import numpy as np
from PIL import Image
#from tqdm import tqdm  
import cv2
import glob
from scipy.ndimage import zoom
from skimage.exposure import rescale_intensity


#modified
def process_rescale_intensity(input_folder, output_folder):
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    file_paths = sorted(glob.glob(os.path.join(input_folder, '*.nii.gz')))
    for file_path in file_paths:
        img = nib.load(file_path)
        img_data = img.get_fdata()
        v_min, v_max = np.percentile(img_data, (0.2, 99.9))
        #img_rescaled = rescale_intensity(img_data, in_range=(v_min, v_max), out_range=(0, 255.0))
        img_rescaled = rescale_intensity(img_data, in_range=(v_min, v_max), out_range=(0, 150.0))
        img_rescaled = img_rescaled.astype(np.uint8)
        new_img = nib.Nifti1Image(img_rescaled, img.affine, img.header)
        file_name = os.path.basename(file_path)
        output_file_path = os.path.join(output_folder, file_name)
        nib.save(new_img, output_file_path)
#here


def tif2niigz(input_folder, output_folder, specific_string, root_name, target_shape):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    png_files = [f for f in os.listdir(input_folder) 
                 if specific_string in f and f.endswith('.tif') and not f.startswith('._')]
    png_files.sort()
    image_matrices = []
    for png_file in png_files:
        img_path = os.path.join(input_folder, png_file)
        img = Image.open(img_path)
        img_matrix = np.array(img)
        image_matrices.append(img_matrix)

    combined_matrix = np.stack(image_matrices, axis=-1)
    #combined_matrix[:, :, :Tuple[0]] = 0
    #combined_matrix[:, :, Tuple[1]:] = 0
    #print(combined_matrix.shape)
    
    zoom_factors = [t / float(s) for t, s in zip(target_shape, combined_matrix.shape)]
    resized_data = zoom(combined_matrix, zoom_factors, order=1)
    combined_matrix=resized_data
    nifti_img = nib.Nifti1Image(combined_matrix, affine=np.eye(4))
    output_filename = os.path.join(output_folder, root_name+specific_string + '.nii.gz')
    nib.save(nifti_img, output_filename)
    return output_filename



def print_shapes(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.nii.gz'):
                file_path = os.path.join(root, file)
                try:
                    img = nib.load(file_path)
                    img_shape = img.header.get_data_shape()
                    print(f"File: {file} - Shape: {img_shape}")
                except Exception as e:
                    print(f"Error loading {file}: {e}")



def nii2png(input_folder, output_folder, Int):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    file_list = os.listdir(input_folder)

    #for file_name in tqdm(file_list, desc=f'shape({Int})', unit="file", miniters=1):
    for file_name in file_list:
        if file_name.lower().endswith('.nii.gz'):
            file_path = os.path.join(input_folder, file_name)
            nii = nib.load(file_path)
            data = nii.get_fdata()

            base_filename = os.path.splitext(os.path.splitext(file_name)[0])[0]

            for i in range(data.shape[int(Int)]):
                if(int(Int)==0):
                    slice_data = data[i, :, :]
                if(int(Int)==1):
                    slice_data = data[:, i, :]    
                if(int(Int)==2):
                    slice_data = data[:, :, i]
                #modified 
                #slice_data[slice_data < 50] = 0
                #here
                slice_data = slice_data.astype(np.uint8)
                img = Image.fromarray(slice_data)  
                img_save_path = os.path.join(output_folder, f'{base_filename}_slice_{i:03d}.png')
                img.save(img_save_path)



def get_image_dimensions(directory):
    dimensions = {}
    for filename in os.listdir(directory):
        if filename.endswith('.png'):
            img = Image.open(os.path.join(directory, filename))
            img=np.array(img)
            print(img.shape)



def gray2RBG(directory):
    #for filename in tqdm(os.listdir(directory), desc="grayscale: ", unit="file", miniters=1):
    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            img = Image.open(os.path.join(directory, filename))
            if len(img.getbands()) == 1:
                img = Image.merge("RGB", (img, img, img))
                img.save(os.path.join(directory, filename))



def resize_images(directory, size=(256, 256)):
    #for filename in tqdm(os.listdir(directory), desc="resize: ", unit="file", miniters=1):
    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            img = Image.open(os.path.join(directory, filename))
            img_resized = img.resize(size, Image.LANCZOS)
            img_resized.save(os.path.join(directory, filename))



#def increase_contrast(directory, alpha=2):
    #if not directory.endswith('/'):
        #directory += '/'

    #for filepath in tqdm(glob.glob(directory + '*.png'), desc="contrasting: ", unit="file", miniters=1):
        #img = cv2.imread(filepath)
        #adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=0)
        #cv2.imwrite(filepath, adjusted)

def increase_contrast(directory, value_threshold, alpha):
    if not directory.endswith('/'):
        directory += '/'
    #for filepath in tqdm(glob.glob(directory + '*.png'), desc="contrasting: ", unit="file", miniters=1):
    for filepath in glob.glob(directory + '*.png'):
        base_name = os.path.basename(filepath)
        parts = base_name.split('_')
        if len(parts) > 1 and parts[1].isdigit():
            value = int(parts[1])
            if value > value_threshold:
                img = cv2.imread(filepath)
                adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=0)
                cv2.imwrite(filepath, adjusted)



def RBG2gray(directory):
    #for filename in tqdm(os.listdir(directory), desc="gray: ", unit="file", miniters=1):
    for filename in os.listdir(directory):
        if filename.endswith('.png'):
            img = Image.open(os.path.join(directory, filename))
            grayscale_img = img.convert('L')
            grayscale_img.save(os.path.join(directory, filename))



def png2nii(folder_path, name_contains, output_path):
    png_files = [f for f in os.listdir(folder_path) if f.endswith('.png') and name_contains in f]
    png_files.sort()
    image_data = []
    for filename in png_files:
        file_path = os.path.join(folder_path, filename)
        image = Image.open(file_path)
        image_data.append(np.array(image))

    image_data = np.stack(image_data, axis=-1)
    print(image_data.shape)
    nifti_img = nib.Nifti1Image(image_data, affine=np.eye(4))
    nib.save(nifti_img, output_path)
    


def transpose_niigz(niigz_file_path, Str):
    nii = nib.load(niigz_file_path)
    data = nii.get_fdata()
    if(Str=='X'):
        transposed_data = data.transpose(2, 0, 1)
    if(Str=='Y'):
        transposed_data = data.transpose(0, 2, 1)
    if(Str=='Z'):
        transposed_data = data

    print(transposed_data.shape)
    new_nii = nib.Nifti1Image(transposed_data, affine=nii.affine, header=nii.header)
    nib.save(new_nii, niigz_file_path)
    print(f"Transposed NIfTI image saved and original file overwritten at: {niigz_file_path}")



def max_fusion(nii_file_paths, output_file_path):

    images_data = [nib.load(path).get_fdata() for path in nii_file_paths]
    if not all(img.shape == images_data[0].shape for img in images_data):
        raise ValueError("All images must have the same shape for fusion.")

    fused_data = np.fmax.reduce(images_data)
    example_nii = nib.load(nii_file_paths[0])
    fused_nii = nib.Nifti1Image(fused_data, affine=example_nii.affine, header=example_nii.header)
    nib.save(fused_nii, output_file_path)
    print(f"Fused image saved at: {output_file_path}")



def delete_files(directory, substring):
    if not os.path.isdir(directory):
        print(f"The directory {directory} does not exist.")
        return
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if substring in filename:
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    print(f"Deleted {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
            else:
                print(f"Skipping {file_path}, since it's not a file.")


import re
import os
import shutil
import numpy as np
import nibabel as nib
from tqdm import tqdm
from scipy.ndimage import gaussian_filter, zoom
from utils.test_unpaired import enhance
from segmentation.process_nii import *
from segmentation.bound_fix import *  
from segmentation.watershed_preseg import * 
from segmentation.cell_identity import * 
from segmentation.binarytree import binarytree
from segmentation.SAM import *
import argparse
import matplotlib.pyplot as plt
from matplotlib import patches
from scipy import ndimage
from matplotlib.colors import to_rgba
from skimage.filters import threshold_otsu
import warnings
warnings.filterwarnings("ignore")

def read_config(config_file_path):
    params = {}
    def convert_value(value):
        if value.isdigit():
            return int(value)
        try:
            if value.startswith('[') and value.endswith(']'):
                return list(map(int, value.strip('[]').split(',')))
            if value.startswith('(') and value.endswith(')'):
                return tuple(map(int, value.strip('()').split(',')))
        except ValueError:
            pass
        return value

    try:
        with open(config_file_path, 'r') as file:
            for line in file:
                if not line.strip() or line.strip().startswith('#'):
                    continue
                key, value = line.split('=')
                key = key.strip()
                value = value.strip()
                params[key] = convert_value(value)
    except FileNotFoundError:
        print(f"Error: The file {config_file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return params



def modify_config(inputpath, modelpath, cfgpath='./confs/LOL_smallNet.yml'):
    with open(cfgpath, 'r') as file:
        cfg_content = file.read()

    cfg_content = re.sub(r'(dataroot_unpaired:\s).*', r'\1' + inputpath, cfg_content)
    cfg_content = re.sub(r'(model_path:\s).*', r'\1' + modelpath, cfg_content)

    with open(cfgpath, 'w') as file:
        file.write(cfg_content)



def run_max_fusion(rootname, output_path):
    rootname=rootname
    output_path=output_path
    input_path=output_path
    #print(input_path)
    outputX=output_path+rootname+'_X.nii.gz'
    png2nii(input_path+'X/', rootname, outputX)
    transpose_niigz(outputX, 'X')
    print("Done")

    outputY=output_path+rootname+'_Y.nii.gz'
    png2nii(input_path+'Y/', rootname, outputY)
    transpose_niigz(outputY, 'Y')
    print("Done")

    outputZ=output_path+rootname+'_Z.nii.gz'
    png2nii(input_path+'Z/', rootname, outputZ)
    transpose_niigz(outputZ, 'Z')
    print("Done")
    max_fusion([outputX, outputY, outputZ], output_path+rootname+'.nii.gz')
    #max_fusion([outputX, outputZ], output_path+rootname+'.nii.gz')
    
    delete_files(output_path, '_X.nii.gz')
    delete_files(output_path, '_Y.nii.gz')
    delete_files(output_path, '_Z.nii.gz')



def delete(root_path, folder_names):
    for folder_name in folder_names:
        folder_path = os.path.join(root_path, folder_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

def move(root_path, target_folder_name):
    target_folder_path = os.path.join(root_path, target_folder_name)
    if not os.path.exists(target_folder_path):
        os.makedirs(target_folder_path)
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('.nii.gz'):
                source_file_path = os.path.join(root, file)
                destination_file_path = os.path.join(target_folder_path, file)
                
                shutil.move(source_file_path, destination_file_path)


def move2(src_folder, target_folder, pattern="_pre_seg.npz"):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for dirpath, dirnames, filenames in os.walk(src_folder):
        for filename in filenames:
            if pattern in filename:
                source_path = os.path.join(dirpath, filename)
                target_path = os.path.join(target_folder, filename)
                shutil.move(source_path, target_path)


def delete2(directory, substring):
    if not os.path.exists(directory):
        print("Directory does not exist:", directory)
        return
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if substring in filename and os.path.isfile(file_path):
            os.remove(file_path)



def reshape_nii_files(input_folder, output_folder, new_shape):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    nii_files = [f for f in os.listdir(input_folder) if f.endswith('.nii.gz')]
    
    for file_name in nii_files:
        file_path = os.path.join(input_folder, file_name)
        img = nib.load(file_path)
        data = img.get_fdata() 

        data_filtered = gaussian_filter(data, sigma=1)
        current_shape = data_filtered.shape
        if len(current_shape) != len(new_shape):
            raise ValueError("当前文件图像形状 {} 与目标形状 {} 不匹配。".format(current_shape, new_shape))
        zoom_factors = [n_new / n_current for n_new, n_current in zip(new_shape, current_shape)]

        data_resampled = zoom(data_filtered, zoom=zoom_factors, order=3)

        new_img = nib.Nifti1Image(data_resampled, affine=img.affine)
        output_file_path = os.path.join(output_folder, file_name)
        nib.save(new_img, output_file_path)



def process_fillholes(input_folder, output_folder, N=20):
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    nii_files = [f for f in os.listdir(input_folder) if f.endswith('.nii.gz')]
    
    for nii_file in nii_files:
        input_path = os.path.join(input_folder, nii_file)
        output_path = os.path.join(output_folder, nii_file)
        img = nib.load(input_path)
        data = img.get_fdata()
        
        # Convert non-zero values to 1 
        binary_mask = np.where(data != 0, 1, 0).astype(np.uint8)

        closed_mask = ndimage.binary_closing(binary_mask, 
                                           structure=np.ones((N,N,N)))
        filled_mask = ndimage.binary_fill_holes(closed_mask)

        processed_img = nib.Nifti1Image(filled_mask, img.affine, img.header)
        nib.save(processed_img, output_path)



def binary_img(input_folder, output_folder, K=20):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.nii.gz') and not file_name.startswith('._'):
            input_filepath = os.path.join(input_folder, file_name)
            output_filepath = os.path.join(output_folder, file_name)

            try:
                img = nib.load(input_filepath)
                img_data = img.get_fdata()
                
                img_data = gaussian_filter(img_data.astype(float), sigma=1)

                flat_data = img_data.flatten()
                otsu_thresh = threshold_otsu(flat_data) * 0.75
                
                img_data[img_data < otsu_thresh] = 0
                img_data[img_data >= otsu_thresh] = 255
                new_img = nib.Nifti1Image(img_data, np.eye(4))
                nib.save(new_img, output_filepath)
                
                print(f"processing {file_name}...")
                
            except Exception as e:
                print(f"Error processing {file_name}: {str(e)}")


def smooth_np(data, smooth_factor=2, cutoff=0.2):
    non_zero = np.unique(data[data != 0])
    if len(non_zero) == 0:
        return data
    elif len(non_zero) > 1:
        raise ValueError("输入数组中存在多个非零值，应该只有一个非零值。检测到: {}".format(non_zero))

    K = non_zero.item()

    binary_data = (data > 0).astype(np.int32)
    smoothed = gaussian_filter(binary_data.astype(float), sigma=smooth_factor)
    smoothed_binary = (smoothed > cutoff).astype(np.int32)
    result = smoothed_binary * K

    return result


def denoise_pipeline(raw_path, nii_path, rootname, data_shape, time_point, scale, 
                     output_X, output_Y, output_Z, opdir, result_X, result_Y, result_Z,
                     size_X, size_Y, size_Z, display=True):
    
    for i in time_point:
        specific_string = f'{i:03d}'
        print(tif2niigz(raw_path, nii_path, specific_string, rootname, data_shape))

    print_shapes(nii_path)


    print("processing...")
    process_rescale_intensity(nii_path, nii_path, scale)
    #return

    nii2png(nii_path, output_X, 0)
    nii2png(nii_path, output_Y, 1)
    nii2png(nii_path, output_Z, 2)

    S = (256, 256)
    gray2RBG(output_X)
    resize_images(output_X, S)
    gray2RBG(output_Y)
    resize_images(output_Y, S)
    gray2RBG(output_Z)
    resize_images(output_Z, S)

    ccf = './confs/LOL_smallNet.yml'
    print("-------------------------denoising-------------------------")
    modify_config(os.path.join(opdir, 'X/') , './model_parameters/X_axis.pth', ccf)
    enhance(cfgpath=ccf, out_dir=os.path.join(opdir, 'X_result'))
    
    modify_config(os.path.join(opdir, 'Y/'), './model_parameters/Y_axis.pth', ccf)
    enhance(cfgpath=ccf, out_dir=os.path.join(opdir, 'Y_result'))
    
    modify_config(os.path.join(opdir, 'Z/'), './model_parameters/Z_axis.pth', ccf)
    enhance(cfgpath=ccf, out_dir=os.path.join(opdir, 'Z_result'))

    resize_images(result_X, size_X)
    resize_images(result_Y, size_Y)
    resize_images(result_Z, size_Z)
    RBG2gray(result_X)
    RBG2gray(result_Y)
    RBG2gray(result_Z)

    folders_to_delete = ['X', 'Y', 'Z']
    for folder in folders_to_delete:
        folder_to_delete_path = os.path.join(opdir, folder)
        if os.path.isdir(folder_to_delete_path):
            shutil.rmtree(folder_to_delete_path)

    folders_to_rename = {'X_result': 'X', 'Y_result': 'Y', 'Z_result': 'Z'}
    for old_name, new_name in folders_to_rename.items():
        old_folder_path = os.path.join(opdir, old_name)
        new_folder_path = os.path.join(opdir, new_name)
        if os.path.isdir(old_folder_path):
            os.rename(old_folder_path, new_folder_path)

    for i in time_point:
        run_max_fusion(f'{rootname}{i:03d}', opdir)
    
    folder_names_to_delete = ["X", "Y", "Z"]
    target_folder_name = "denoised"
    delete(opdir, folder_names_to_delete)
    move(opdir, target_folder_name)

    smooth_nii_folder(opdir+"denoised")

    if display:
        display_central_slices(nii_path, opdir, rootname, time_point)



import os
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy.ndimage import gaussian_filter

def smooth_nii_folder(folder_path, sigma=1):
    folder = Path(folder_path)
    if not folder.is_dir():
        raise ValueError(f"文件夹不存在：{folder}")
    for nii_file in folder.glob("*.nii.gz"):
        try:
            img = nib.load(str(nii_file))
            data = img.get_fdata()
            orig_dtype = img.header.get_data_dtype()
            smoothed = gaussian_filter(data, sigma=sigma)
            smoothed = smoothed.astype(orig_dtype)
            smoothed_img = nib.Nifti1Image(smoothed, img.affine, img.header)
            nib.save(smoothed_img, str(nii_file))
        except Exception as e:
            print(e)


def display_central_slices(nii_path, opdir, rootname, time_point):
    for i in time_point:

        raw_file = os.path.join(nii_path, f"{rootname}{i:03d}.nii.gz")
        denoised_file = os.path.join(opdir, "denoised", f"{rootname}{i:03d}.nii.gz")
        
        try:
            raw_img = nib.load(raw_file)
            raw_data = raw_img.get_fdata()
        except Exception as e:
            print(f"load {raw_file} fail：", e)
            continue

        try:
            denoised_img = nib.load(denoised_file)
            denoised_data = denoised_img.get_fdata()
            denoised_data = gaussian_filter(denoised_data, sigma=1)
            
        except Exception as e:
            print(f"load denoised {denoised_file} file：", e)
            continue

        z_index_raw = int(raw_data.shape[2] / 4)
        z_index_denoised = int(denoised_data.shape[2] / 4)
        raw_slice = raw_data[:, :, z_index_raw]
        denoised_slice = denoised_data[:, :, z_index_denoised]

        fig, axes = plt.subplots(1, 2, figsize=(6, 3))
        axes[0].imshow(raw_slice, cmap='gray')
        axes[0].set_title(f'raw image {rootname}{i:03d} (Slice {z_index_raw})')
        axes[0].axis('off')
        
        axes[1].imshow(denoised_slice, cmap='gray')
        axes[1].set_title(f'denoised {rootname}{i:03d} (Slice {z_index_denoised})')
        axes[1].axis('off')
        
        plt.tight_layout()
        plt.show()


def init_config(config_file, nii_path, opdir):
    config_params = read_config(config_file)
    rootname   = config_params['rootname']
    CD_file    = config_params['CD_file']
    time_point = config_params['time_point']
    ori_shape  = config_params['ori_shape']
    raw_path   = config_params['raw_path']
    data_shape = config_params['data_shape']
    scale      = float(config_params['scale'])

    ratio = (ori_shape[0] / data_shape[0],
             ori_shape[1] / data_shape[1],
             data_shape[2] / ori_shape[2])
    
    output_X = os.path.join(opdir, 'X')
    output_Y = os.path.join(opdir, 'Y')
    output_Z = os.path.join(opdir, 'Z')
    result_X = os.path.join(opdir, 'X_result')
    result_Y = os.path.join(opdir, 'Y_result')
    result_Z = os.path.join(opdir, 'Z_result')

    size_X = (data_shape[2], data_shape[1])
    size_Y = (data_shape[2], data_shape[0])
    size_Z = (data_shape[1], data_shape[0])
    
    print("nii_path:", nii_path)
    print("opdir:", opdir)
    print("rootname:", rootname)
    print("CD_file:", CD_file)
    print("time_point:", time_point)
    print("ori_shape:", ori_shape)
    print("raw_path:", raw_path)
    print("data_shape:", data_shape)
    print("scale:", scale)
    
    return {
        'rootname': rootname,
        'CD_file': CD_file,
        'time_point': time_point,
        'ori_shape': ori_shape,
        'raw_path': raw_path,
        'data_shape': data_shape,
        'scale': scale,
        'ratio': ratio,
        'nii_path': nii_path,
        'opdir': opdir,
        'output_X': output_X,
        'output_Y': output_Y,
        'output_Z': output_Z,
        'result_X': result_X,
        'result_Y': result_Y,
        'result_Z': result_Z,
        'size_X': size_X,
        'size_Y': size_Y,
        'size_Z': size_Z
    }


def boundary_localization_pipeline(opdir, rootname, time_point, CD_file, ratio, ori_shape, display=True, N=10):
    binary_img(os.path.join(opdir, 'denoised'), os.path.join(opdir, 'gaussian'))

    process_fillholes(os.path.join(opdir, 'denoised'), os.path.join(opdir, 'boundary_largest'), N)

    process_erode(os.path.join(opdir, 'boundary_largest'), os.path.join(opdir, 'boundary_only'), E=8)

    process_largest(os.path.join(opdir, 'boundary_only'), os.path.join(opdir, 'boundary_only'))
    
    feature_fuse(os.path.join(opdir, 'boundary_only'), os.path.join(opdir, 'gaussian'), os.path.join(opdir, 'toseg'))

    set_border_zero(os.path.join(opdir, 'toseg'))
    
    print("-------------------------watershed coarse seg-------------------------")
    embryo_names = ['toseg']
    seg_memb_root_dir = opdir
    run_membrane2cell(seg_memb_root_dir, embryo_names, False)
    print("-----------------------bounding box prompts-----------------------")


    if display:
        display_denoised_with_segmentation(opdir, rootname, time_point)
    

    move2(os.path.join(opdir, 'toseg'), os.path.join(opdir, 'matrix'), pattern="_pre_seg.nii.gz")

    matrix_dir = os.path.join(opdir, 'matrix')
    if not matrix_dir.endswith(os.sep):
        matrix_dir += os.sep
    cd = CD_file
    listmp1 = []
    for i in time_point:
        p = os.path.join(matrix_dir, f'{rootname}{i:03d}_pre_seg.nii.gz')
        #print(p,i)
        coordinates = extract_coordinates(cd, i, ratio)
        updated_coordinates = merge_dividing_cell_by_coordinates(coordinates, p)
        
        for k, v in updated_coordinates.items():
            #k是cell name,v应该是3d坐标 
            output_name = f'{rootname}{i:03d}_{k}.nii.gz'
            output_path = os.path.join(matrix_dir, f'{rootname}{i:03d}')
            try:
                #print(p, v, output_name, output_path, ori_shape)
                #x=(output_name, target_value, (x, y, z))
                x = divide_embryo(p, v, output_name, output_path, ori_shape)
                listmp1.append((x, i, k))
            except Exception as e:
                print(e)
                continue


    delete2(os.path.join(opdir, 'matrix'), '_pre_seg.nii.gz')
    reshape_nii_files(opdir+'denoised/', opdir+'denoised2/',ori_shape)
    return


    

def display_denoised_with_segmentation(opdir, rootname, time_point):
    for i in time_point:
        denoised_file = os.path.join(opdir, "denoised", f"{rootname}{i:03d}.nii.gz")
        seg_file = os.path.join(opdir, "toseg", f"{rootname}{i:03d}_pre_seg.nii.gz")
        
        try:
            denoised_img = nib.load(denoised_file)
            denoised_data = denoised_img.get_fdata()
            denoised_data = gaussian_filter(denoised_data, sigma=1)
        except Exception as e:
            print(f"Loading denoised file {denoised_file} failed:", e)
            continue

        try:
            seg_img = nib.load(seg_file)
            seg_data = seg_img.get_fdata()
        except Exception as e:
            print(f"Loading segmentation file {seg_file} failed:", e)
            continue

        z_index = int(denoised_data.shape[2] / 4)
        
        denoised_slice = denoised_data[:, :, z_index]
        seg_slice = seg_data[:, :, z_index]
        
        unique_labels = np.unique(seg_slice)
        unique_labels = unique_labels[unique_labels != 0]

        boxes = {}
        for label in unique_labels:
            label_mask = (seg_slice == label)
            bbox = bounds(label_mask)
            if None not in bbox:
                boxes[label] = bbox

        fig, ax = plt.subplots(figsize=(5, 2.5))
        ax.imshow(denoised_slice, cmap='gray')
        
        for label, (min_x, max_x, min_y, max_y) in boxes.items():
            width = max_x - min_x
            height = max_y - min_y
            rect = patches.Rectangle((min_x, min_y), width, height,
                                     edgecolor='khaki', facecolor='none', linewidth=1)
            ax.add_patch(rect)
        
        ax.axis('off')
        plt.tight_layout()
        plt.show()



def segment_anything(opdir, target_shape, raw_path, rootname, predictor):
    
    directory=opdir+'matrix/'
    for entry in sorted(os.listdir(directory)):
        subfolder_path = os.path.join(directory, entry)
        #if os.path.isdir(subfolder_path):
        print("Processing subfolder:", subfolder_path)
        denoised_path = subfolder_path.replace("matrix", "denoised2") + ".nii.gz"
        denoised=nib.load(denoised_path).get_fdata()
        
        for file in sorted(os.listdir(subfolder_path)):
            if file.endswith('.nii.gz'):
                file_path = os.path.join(subfolder_path, file)
                #print("Processing file:", file_path)

                
                #print(file_path.split('_'))
                #tp = file_path.split('_')[3]
                file_name = os.path.basename(file_path)
                # 使用split分割并提取数字部分
                #tp = file_name.split('_')[1]
                
                #matrix = np.load(file_path)['arr_0']

                matrix = nib.load(file_path).get_fdata()
                

                SAM_result = []
                z_length = matrix.shape[2]
                for i in range(z_length):
                    slice_z = matrix[:, :, i].astype(np.uint8)
                    denoised_z=denoised[:, :, i].astype(np.uint8)
                    
                    unique_values = np.unique(slice_z)
    
                    if len(unique_values) == 1:
                        zero_image = np.zeros_like(slice_z)
                        SAM_result.append(zero_image)
                    elif len(unique_values) > 1:
                        value=unique_values[1]
                        bound = bounds(slice_z)
                        slice_z[slice_z != 0] = 255
                        #print(raw_path)
                        #print(rootname)
                        #print(type(tp))
                        #print(i+1)
                        #raw_image=load_raw(raw_path, rootname,tp ,i+1)   
                        
                        box=[bound[0],bound[2],bound[1],bound[3]]
                        #image_rgb = np.dstack((slice_z, slice_z, slice_z))
                        image_denoised = np.dstack((denoised_z, denoised_z, denoised_z))
                        #print(image_rbg.shape)
                        #raw_image=np.maximum(raw_image,image_rbg)
                        raw_image=image_denoised
                        predictor.set_image(raw_image)
                        input_box = np.array(box)
                        masks, _, _ = predictor.predict(
                            point_coords=None,
                            point_labels=None,
                            box=input_box[None, :],
                            multimask_output=False,)

                        seg_matrix=masks[0].astype(np.uint8)
                        seg_matrix[seg_matrix != 0] = value

                        area, perimeter, irregularity = calculate_metrics(seg_matrix)
                        if(float(irregularity)>9.02):
                            #print("fk",irregularity)
                            zero_image = np.zeros_like(slice_z)
                            SAM_result.append(zero_image)
                        else:
                            #print(irregularity)
                            SAM_result.append(seg_matrix)
                
                SAM_result = np.transpose(SAM_result, (1, 2, 0))
                SAM_result = smooth_np(SAM_result,2,0.2)
                current_shape = SAM_result.shape
                desired_shape = target_shape
                zoom_factors = [desired_shape[i] / current_shape[i] for i in range(len(desired_shape))]
                resized_data = zoom(SAM_result, zoom_factors, order=3)
                

                smoothed = gaussian_filter(resized_data.astype(float), sigma=2)
                resized_data = (smoothed > 0.7).astype(np.int32)

                
                resized_data[resized_data != 0] = value
                nifti_img = nib.Nifti1Image(resized_data, np.eye(4))
                #nifti_file_path = os.path.join(subdir, file)#.replace('.npz', '.nii.gz'))
                nifti_file_path = os.path.join(subfolder_path, file)#.replace('.npz', '.nii.gz'))
                nib.save(nifti_img, nifti_file_path)
                #os.remove(file_path)
                print(f'{nifti_file_path} done')
    os.rename(opdir+'matrix/', opdir+'result/')
    delete(opdir, ['boundary_only','gaussian','denoised','denoised2','boundary_largest','toseg'])
    print("done")
    


def Visualization(nii_path, opdir, rootname, time_point):
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta']

    for i in time_point:
        raw_file = os.path.join(nii_path, f"{rootname}{i:03d}.nii.gz")
        folder = os.path.join(opdir, "result", f"{rootname}{i:03d}")

        try:
            raw_img = nib.load(raw_file)
            raw_data = raw_img.get_fdata()
        except Exception as e:
            continue

        slice_index = int(raw_data.shape[2] / 4)
        raw_slice = raw_data[:, :, slice_index]
        merged_data = None
        found_file = False
        if not os.path.isdir(folder):
            continue
        for filename in os.listdir(folder):
            if filename.endswith('.nii.gz'):
                found_file = True
                file_path = os.path.join(folder, filename)
                try:
                    img = nib.load(file_path)
                    data = img.get_fdata()
                except Exception as e:
                    continue
                if merged_data is None:
                    merged_data = data
                else:
                    merged_data = np.maximum(merged_data, data)
        if not found_file:
            continue
        seg_slice = merged_data[:, :, slice_index]
        unique_labels = np.unique(seg_slice)
        unique_labels = unique_labels[unique_labels != 0]

        fig, ax = plt.subplots(figsize=(5,2.5))
        ax.imshow(raw_slice, cmap='gray')

        for idx, label in enumerate(unique_labels):
            color = colors[idx % len(colors)]
            rgba_color = to_rgba(color, alpha=0.4)
            binary_mask = seg_slice == label
            if np.any(binary_mask):
                overlay = np.zeros((binary_mask.shape[0], binary_mask.shape[1], 4))
                overlay[binary_mask] = rgba_color
                ax.imshow(overlay, interpolation='none')
                coords = np.argwhere(binary_mask)

        ax.axis('off')
        plt.tight_layout()
        plt.show()


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



def main():
    parser = argparse.ArgumentParser(description="running EmbSAM")
    parser.add_argument("--config_file", type=str, required=True, 
                        help="cfg_path './confs/running_Emb1-Copy1.txt'")
    parser.add_argument("--nii_path", type=str, required=True, 
                        help="nii_folder_path 'G:/EmbSAM_reviewer_material/fig_R/submission_250531/EmbSAM/nii'")
    parser.add_argument("--opdir", type=str, required=True, 
                        help="result_folder_path 'G:/EmbSAM_reviewer_material/fig_R/submission_250531/EmbSAM/output/'")
    
    args = parser.parse_args()

    config_file = args.config_file
    nii_path = args.nii_path
    opdir = args.opdir

    params = init_config(config_file, nii_path, opdir)

    denoise_pipeline(
        params['raw_path'],
        params['nii_path'],
        params['rootname'],
        params['data_shape'],
        params['time_point'],
        params['scale'],
        params['output_X'],
        params['output_Y'],
        params['output_Z'],
        params['opdir'],
        params['result_X'],
        params['result_Y'],
        params['result_Z'],
        params['size_X'],
        params['size_Y'],
        params['size_Z'],
        display=False
    )

    boundary_localization_pipeline(
        params['opdir'],
        params['rootname'],
        params['time_point'],
        params['CD_file'],
        params['ratio'],
        params['ori_shape'],
        display=False
    )

    sam_checkpoint = "./model_parameters/sam_vit_b_01ec64.pth"
    model_type = "vit_b"
    device = "cuda"
    predictor = load_model(sam_checkpoint, model_type, device)
    
    segment_anything(
        params['opdir'],
        params['data_shape'],
        params['raw_path'],
        params['rootname'],
        predictor
    )

if __name__ == '__main__':
    main()    
    
    





    

    

    

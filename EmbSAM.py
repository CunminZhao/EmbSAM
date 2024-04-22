import re
import os
import shutil
import numpy as np
import nibabel as nib
from tqdm import tqdm
from scipy.ndimage import zoom
from utils.test_unpaired import enhance
from segmentation.process_nii import *
from segmentation.bound_fix import *  
from segmentation.watershed_preseg import * 
from segmentation.cell_identity import * 
from segmentation.binarytree import binarytree
from segmentation.SAM import *
import argparse



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




def auto_segment_anything(directory, target_shape, raw_path, rootname, predictor):

    for subdir, dirs, files in os.walk(directory):
      
        for file in files:
            if file.endswith('.npz'):
                file_path = os.path.join(subdir, file)
                #print(file_path)
                #print(file_path.split('_'))
                tp = file_path.split('_')[3]
                
                matrix = np.load(file_path)['arr_0']
                SAM_result = []
                z_length = matrix.shape[2]
                for i in range(z_length):
                    slice_z = matrix[:, :, i].astype(np.uint8)
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
                        raw_image=load_raw(raw_path, rootname,tp ,i+1)             
                        box=[bound[0],bound[2],bound[1],bound[3]]
                        image_rbg = np.dstack((slice_z, slice_z, slice_z))
                        #print(image_rbg.shape)
                        raw_image=np.maximum(raw_image,image_rbg)
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
                current_shape = SAM_result.shape
                desired_shape = target_shape
                zoom_factors = [desired_shape[i] / current_shape[i] for i in range(len(desired_shape))]
                resized_data = zoom(SAM_result, zoom_factors, order=1)
                resized_data[resized_data != 0] = value
                nifti_img = nib.Nifti1Image(resized_data, np.eye(4))
                nifti_file_path = os.path.join(subdir, file.replace('.npz', '.nii.gz'))
                nib.save(nifti_img, nifti_file_path)
                os.remove(file_path)
                print(f'{nifti_file_path} done')
    print("done")



def main(cfg_file):
    #input of cfg_file
    config_params = read_config(cfg_file)
    rootname=config_params['rootname']
    CD_file=config_params['CD_file']
    time_point=config_params['time_point']
    ori_shape=config_params['ori_shape']
    raw_path=config_params['raw_path']
    data_shape=config_params['data_shape']
    scale=float(config_params['scale'])
    cutoff_lower=float(config_params['cutoff_lower'])
    cutoff_upper=float(config_params['cutoff_upper'])
    ratio=(ori_shape[0]/data_shape[0], ori_shape[1]/data_shape[1], data_shape[2]/ori_shape[2])
    nii_path = './nii_folder'
    opdir='./output_folder/'
    output_X=opdir+'X'
    output_Y=opdir+'Y'
    output_Z=opdir+'Z'
    result_X=opdir+'X_result/'
    result_Y=opdir+'Y_result/'
    result_Z=opdir+'Z_result/'
    size_X=(data_shape[2],data_shape[1])
    size_Y=(data_shape[2],data_shape[0])
    size_Z=(data_shape[1],data_shape[0])
    print("print the cfg file")
    print(nii_path)
    print(opdir)
    print(rootname)
    print(CD_file)
    print(time_point)
    print(ori_shape)
    print(raw_path)
    print(data_shape)
    print(scale)
    print(cutoff_lower)
    print(cutoff_upper)

    
    #convert tif to niigz
    for i in time_point:
        specific_string=f'{i:03d}'
        print(tif2niigz(raw_path, nii_path, specific_string,rootname,data_shape))

    print_shapes(nii_path)
    print("-------------------------rescale_intensity-------------------------")
    process_rescale_intensity(nii_path, nii_path, scale)
    print("rescale_intensity done")

    #convert nii to png in (x,y,z) for cell boundary enhancement
    nii2png(nii_path,output_X,0)
    nii2png(nii_path,output_Y,1)
    nii2png(nii_path,output_Z,2)
    
    #print("-------------------------increasing_contrast-------------------------")
    #increase_contrast(output_X,100,1.67)
    #increase_contrast(output_Y,100,1.67)
    #increase_contrast(output_Z,100,1.67)
    
    #increase_contrast(output_X,0,3)
    #increase_contrast(output_Y,0,3)
    #increase_contrast(output_Z,0,3)
    #print("processed contrast")

    print("-------------------------processing images-------------------------")
    gray2RBG(output_X)
    resize_images(output_X)
    gray2RBG(output_Y)
    resize_images(output_Y)
    gray2RBG(output_Z)
    resize_images(output_Z)
    print("processed images")

    print("-------------------------images denosing-------------------------")
    modify_config(opdir+'X/', './model_parameters/X_axis.pth','./confs/LOL_smallNet.yml')
    enhance(cfgpath='./confs/LOL_smallNet.yml', out_dir=opdir+'X_result')
    ##
    modify_config(opdir+'Y/','./model_parameters/Y_axis.pth','./confs/LOL_smallNet.yml')
    enhance(cfgpath='./confs/LOL_smallNet.yml', out_dir=opdir+'Y_result')
    ##
    modify_config(opdir+'Z/','./model_parameters/Z_axis.pth','./confs/LOL_smallNet.yml')
    enhance(cfgpath='./confs/LOL_smallNet.yml', out_dir=opdir+'Z_result')
    print("images denosing done")
    print("-------------------------post-processing-------------------------")
    increase_contrast(result_X,0,2)
    increase_contrast(result_Y,0,2)
    increase_contrast(result_Z,0,2)
    resize_images(result_X, size_X)
    resize_images(result_Y, size_Y)
    resize_images(result_Z, size_Z)
    RBG2gray(result_X)
    RBG2gray(result_Y)
    RBG2gray(result_Z)
    
    #delete and rename
    folders_to_delete = ['X', 'Y', 'Z']

    folders_to_rename = {'X_result': 'X', 'Y_result': 'Y', 'Z_result': 'Z'}

    for folder in folders_to_delete:
        folder_to_delete_path = os.path.join(opdir, folder)
        if os.path.isdir(folder_to_delete_path):
            shutil.rmtree(folder_to_delete_path)

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

    print("process_gaussian...")
    #process_gaussian(opdir+'denoised', opdir+'gaussian',2,0.5)
    process_gaussian(opdir+'denoised', opdir+'gaussian',2,0.5, cutoff_lower, cutoff_upper)
    delete(opdir, ['denoised'])

    #process_gaussian(nii_path, opdir+'boundary',5,0.3)
    process_gaussian(nii_path, opdir+'boundary',5,0.3, cutoff_lower, cutoff_upper)
    #process_gaussian(nii_path, opdir+'boundary',5,0.5)

    process_largest(opdir+'boundary/', opdir+'boundary_largest/')
    delete(opdir, ['boundary'])

    process_largest(opdir+'gaussian/', opdir+'gaussian/')

    fill_bubbles(opdir+'boundary_largest/', opdir+'boundary_largest/')

    process_erode(opdir+'boundary_largest/', opdir+'boundary_only/')
    delete(opdir, ['boundary_largest'])
    #modified
    process_largest(opdir+'boundary_only/', opdir+'boundary_only/')
    #here
    feature_fuse(opdir+'boundary_only/', opdir+'gaussian/', opdir+'toseg/')
    delete(opdir, ['boundary_only','gaussian'])

    set_border_zero(opdir+'toseg/')
    print("post-processing done")
    print("-------------------------watershed_preseg-------------------------")

    embryo_names = ['toseg']
    seg_memb_root_dir=opdir
    run_membrane2cell(seg_memb_root_dir, embryo_names,False)
    print("watershed_preseg done, the pipeline still working")
    move2(opdir+'toseg',opdir+'matrix')
    delete(opdir,['toseg'])
    print("-------------------------cell identity-------------------------")

    path = opdir+'matrix/'
    cd=CD_file
    listmp1=[]
    for i in time_point:
        p = path + f'{rootname}{i:03d}' + '_pre_seg.npz'
        coordinates = extract_coordinates(cd, i, ratio)
        for k, v in coordinates.items():
            output_name = f'{rootname}{i:03d}' + '_' + str(k) + '.npz'
            output_path = path + f'{rootname}{i:03d}'
            try:
                x=divide_embryo(p, v, output_name, output_path, ori_shape)
                listmp1.append((x,i,k))
            except Exception as e:
                continue
            

    path = opdir+'matrix/'

    k=0
    for i in range(len(listmp1)):
        for j in range(i + 1, len(listmp1)):
            A = listmp1[i]
            B = listmp1[j]
            if A[0][1] == B[0][1] and A[1] == B[1]:
                daughter_cell=binarytree(A[2])[0]
                mother_cell=binarytree(A[2])[1]
                if daughter_cell==B[2]:
                    print(A[2],B[2],A[1], "Yes")
                    p = path + f'{rootname}{A[1]:03d}/{rootname}{A[1]:03d}_{A[2]}.npz'
                    p2 = path + f'{rootname}{A[1]:03d}/{rootname}{A[1]:03d}_{B[2]}.npz'
                    p3 = f'{rootname}{A[1]:03d}_{mother_cell}.npz'

                    merge_dividing(p,p2,p3)
                else:
                    print(A[2],B[2],A[1], "No")
                k=k+1
    print(k)

    delete2(opdir+'matrix/', '_pre_seg.npz')
    print("-------------------------segment anything-------------------------")
    sam_checkpoint = "./model_parameters/sam_vit_b_01ec64.pth"
    model_type = "vit_b"
    device = "cuda"
    predictor=load_model(sam_checkpoint, model_type, device)

    auto_segment_anything(opdir+'matrix/', data_shape, raw_path, rootname, predictor)

    os.rename(opdir+'matrix/', opdir+'result/')
    print("all works done, please check the result in ./output_folder/result, thanks")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='cfg_file_path')
    parser.add_argument('-cfg_path', required=True, help='')
    args = parser.parse_args()

    main(args.cfg_path)

    
    
    





    

    

    

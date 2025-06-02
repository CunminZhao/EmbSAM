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
    """
    遍历 input_dict 中的每个 key，调用 binarytree 函数，
    如果返回结果的第一个元素 candidate 在字典中存在且不与当前 key 相同，
    则认为这两个 key 成对，并且保证每对只输出一次。
    
    最终返回的结果中，每个元素为一个元组，格式为：
      ((key1, key2), (value_of_key1, value_of_key2))
    其中 key1 与 key2 顺序为字典序排列。

    参数:
      input_dict -- 包含若干 key 和对应值的字典
      
    返回:
      paired_results -- 包含成对 key 及对应 value 的列表
    """
    paired_results = []  # 用于存储最终的 (keys pair, corresponding values) 结果
    added = set()        # 记录已添加的配对，防止 (a, b) 与 (b, a) 重复

    for key in input_dict:
        result = binarytree(key)
        if result and len(result) > 0:
            candidate = result[0]
            # 如果 candidate 存在于字典中，且不与当前 key 相同，认为两者成对
            if candidate in input_dict and candidate != key:
                # 按字典序排序，以确保 (key, candidate) 与 (candidate, key) 视为同一对
                pair = tuple(sorted([key, candidate]))
                if pair not in added:
                    added.add(pair)
                    # 根据排序后的 pair 取出对应的 value
                    paired_results.append((pair, (input_dict[pair[0]], input_dict[pair[1]])))
    return paired_results


def merge_cell_name(paired_results, niigz_file):
    """
    对于 paired_results 中的每一对 ((key1, key2), ((x1, y1, z1), (x2, y2, z2)))：
      1. 连接两个坐标点构成的线段（利用线性插值采样）
      2. 从 niigz 文件加载的图像数据中获取线段经过的像素值
      3. 筛选出非0像素，并利用 np.unique 统计其唯一值种类
      4. 如果唯一非0值的数量等于1，则返回 binarytree(key1)[1]，
         否则返回 "no"
    
    参数:
      paired_results -- 列表，每个元素格式为:
                        ((key1, key2), ((x1, y1, z1), (x2, y2, z2)))
      niigz_file    -- NIfTI 文件路径（例如 "xxx.nii.gz"）
    
    返回:
      results -- 列表，每个元素为 ((key1, key2), output)
                 其中 output 为 binarytree(key1)[1] 或 "no"
    """
    # 加载 NIfTI 图像数据
    img = nib.load(niigz_file)
    data = img.get_fdata()  # 假设为 3D 数据

    results = []

    for pair_keys, coords in paired_results:
        # 取出两个坐标点，转换为 numpy 数组
        p1, p2 = np.array(coords[0]), np.array(coords[1])
        
        # 计算两点间距离，决定采样步数
        distance = np.linalg.norm(p2 - p1)
        n_steps = int(np.ceil(distance)) + 1  # 保证至少包含两个端点
        
        # 按各维度进行线性插值
        xs = np.linspace(p1[0], p2[0], num=n_steps)
        ys = np.linspace(p1[1], p2[1], num=n_steps)
        zs = np.linspace(p1[2], p2[2], num=n_steps)
        
        # 将采样点四舍五入并转为整数索引
        xs = np.rint(xs).astype(int)
        ys = np.rint(ys).astype(int)
        zs = np.rint(zs).astype(int)
        
        # 组合为坐标元组，并过滤超出图像数据边界的点
        line_coords = list(zip(xs, ys, zs))
        valid_coords = []
        shape = data.shape
        for x, y, z in line_coords:
            if 0 <= x < shape[0] and 0 <= y < shape[1] and 0 <= z < shape[2]:
                valid_coords.append((x, y, z))
        
        # 获取坐标点在图像数据中的像素值
        pixel_values = [data[x, y, z] for (x, y, z) in valid_coords]
        
        # 筛选非0像素值，并统计唯一非0种类
        nonzero_pixels = [val for val in pixel_values if val != 0]
        unique_vals = np.unique(nonzero_pixels)
        
        # 如果唯一非0值的数量等于1，则返回 binarytree(keys[0])[1]，否则返回 "no"
        if len(unique_vals) == 1:
            bt_result = binarytree(pair_keys[0])
            output = bt_result[1] if len(bt_result) > 1 else None
        else:
            output = "no"
        
        results.append((pair_keys, output))
    
    return results



def update_coordinates_from_merged(results, coordinates):
    """
    根据 results 中的判断结果更新 coordinates 字典。
    
    对于 results 中每个元素 ((key1, key2), output)：
      如果 output 不等于 "no"（即代表条件满足，说明通过插值采样统计的非0像素
      的唯一值数量等于 1，并且已通过 binarytree 得到新的标记），则执行下列操作：
      
         1. 将 coordinates 里面原来的 key1 替换为 binarytree(key1)[1]（新 key 保持 value 不变）
         2. 删除 coordinates 中 key2 及其对应的 value
         
    参数:
      results     -- 来自 process_paired_lines_new 的结果，格式为 [ ((key1, key2), output), ... ]
      coordinates -- 从 extract_coordinates 得到的字典，键为各个 key，值不变
      
    返回:
      更新后的 coordinates 字典
    """
    for pair_keys, output in results:
        # 只有 output 不为 "no" 时，才进行替换和删除操作
        if output != "no":
            key1, key2 = pair_keys[0], pair_keys[1]
            # 获取新的 key: 根据 binarytree(key1) 的返回值，取第二个元素
            new_key = binarytree(key1)[1]
            # 如果 coordinates 中存在 key1，则将其对应的 value 保留，并更新 key 为 new_key
            if key1 in coordinates:
                temp_value = coordinates[key1]
                # 删除原来的 key1
                del coordinates[key1]
                # 添加新的 key，新 key 如果已存在则覆盖（或根据需要进行其他处理）
                coordinates[new_key] = temp_value
            # 删除 key2 及其对应的 value（如果存在）
            if key2 in coordinates:
                del coordinates[key2]
    return coordinates



def merge_dividing_cell_by_coordinates(input_dict, niigz_file):
    """
    综合上述三个步骤：
      1. 使用 find_paired_keys_and_values 在 input_dict 中找出成对坐标
      2. 调用 process_paired_lines_new 利用 niigz 文件检测成对坐标间的线段
      3. 根据检测结果更新 input_dict：
           如果一对的线段采样结果满足唯一非0值（即返回 binarytree(key1)[1]），
           则将 input_dict 中 key1 替换为 binarytree(key1)[1]，同时删除 key2
           
    参数:
      input_dict  -- 包含 key 和对应坐标（例如 (x, y, z)）的字典
      niigz_file  -- NIfTI (.nii.gz) 文件路径
      
    返回:
      updated_coordinates -- 更新后的坐标字典
    """
    # 第一步：查找成对 key 及对应坐标
    paired_results = find_paired_keys_binarytree(input_dict)
    
    # 第二步：处理成对坐标连接线段上的图像像素值
    results = merge_cell_name(paired_results, niigz_file)
    
    # 第三步：根据判断结果更新输入字典
    updated_coordinates = update_coordinates_from_merged(results, input_dict)
    
    return updated_coordinates

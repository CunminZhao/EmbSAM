import glob
import os.path
import math

from PIL import Image
import numpy as np

target_root=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\切片\PH-7_1'

seg_img_list=sorted(glob.glob(os.path.join(target_root,'*_seg.png')))

# 1	P0
# 2	AB
# 3	P1
# 4	ABa
# 5	ABp
# 6	EMS
# 7	P2
# green 129 red 60 pink 67 46 47 dark red

mapping1={72:1,73:1,
         129:2,
         60:3,}

mapping2={
         129:4,
         60:3,
         67:5}

mapping3={
         129:6,
         60:7,
         67:4,

    46:5,
    47:5
          }

mapping_to_rgb_r={1:17,2:17,3:255,4:200,5:17,6:255,7:255}
mapping_to_rgb_g={1:17,2:255,3:17,4:255,5:255,6:200,7:17}
mapping_to_rgb_b={1:255,2:17,3:17,4:17,5:200,6:17,7:200}

for png_path in seg_img_list:

    file_name_this=os.path.basename(png_path).split('.')[0]
    print(file_name_this)
    image_this=Image.open(png_path)
    # tem=np.asarray(image_this)
    image_arr=np.asarray(image_this.convert('L'))
    # tem_saving_arr=np.zeros(image_arr.shape)
    saving_arr=np.zeros(list(image_arr.shape)+[3])
    # grayscale_arr=0.299*image_arr[:,:,0]+0.587*image_arr[:,:,1]+0.114*image_arr[:,:,2]
    label_list,counting_list=np.unique(image_arr,return_counts=True)
    print(label_list[counting_list>1000],counting_list[counting_list>1000])
    for effective_label in label_list[counting_list>1000][1:]:
        mask_this=image_arr == effective_label
        cell_label_this=mapping1[effective_label]
        # tem_saving_arr[mask_this]=cell_label_this
        saving_arr[:,:][mask_this]=(mapping_to_rgb_r[cell_label_this],mapping_to_rgb_g[cell_label_this],mapping_to_rgb_b[cell_label_this])
        # saving_arr[:,:,1][mask_this]=
        # saving_arr[:,:,2][mask_this]=
        # saving_arr[:,:,0][mask_this]=mapping_to_rgb_r[cell_label_this]

    # print(np.unique(saving_arr, return_counts=True))
    img_saving = Image.fromarray(saving_arr.astype(np.uint8))
    # image_arr_post=np.asarray(img_saving)
    # img_saving.putpalette(P)
    # print(np.unique(image_arr[:,:,0]),np.unique(image_arr[:,:,1]),np.unique(image_arr[:,:,2]),np.unique(image_arr[:,:,3]))
    img_saving.save(os.path.join(target_root,file_name_this+'_unified.png'),'PNG')
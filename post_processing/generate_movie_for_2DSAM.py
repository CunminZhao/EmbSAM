import glob
import os
import cv2

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tifffile as tiff
from skimage.exposure import rescale_intensity
from skimage.transform import resize

raw_tif_root=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\2dsam_data\raw images'
embryo_name=r'10(earliest)'
segmented_img_root=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\2dsam_data\seg_assigned\10earliest(1-2)'

movie_saving_root=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\2dsam_data\movie_pngs'

offset_tp=0

saving_path_the_combined_pngs=os.path.join(movie_saving_root,embryo_name)
if not os.path.exists(saving_path_the_combined_pngs):
    os.mkdir(saving_path_the_combined_pngs)

tps_num=len(glob.glob(os.path.join(segmented_img_root,'*.png')))

tif_img=tiff.imread(os.path.join(raw_tif_root,embryo_name+'.tif'))
tif_array=np.array(tif_img)
green_c_max=np.max(tif_array[:,0,:,:])
tif_array[:,0,:,:]=tif_array[:,0,:,:]/green_c_max*256
red_c_max=np.max(tif_array[:,1,:,:])
tif_array[:,1,:,:]=tif_array[:,1,:,:]/red_c_max*256
# tif_array=tif_array.astype(np.uint8)
v_min, v_max = np.percentile(tif_array, (1, 99))  # erase the outrange grayscale # no need to do this, would lower the contrast
tif_array = rescale_intensity(tif_array, in_range=(v_min, v_max), out_range=(0, 255.0))
# print(np.max(tif_array))



for imag_idx in range(tps_num):
    image_shape=tif_array.shape[2:4]

    tif_arr_this_frame=np.zeros(list(image_shape)+[3])
    tif_arr_this_frame[:,:,0]=tif_array[imag_idx,1,:,:]
    tif_arr_this_frame[:,:,1]=tif_array[imag_idx,0,:,:]

    tif_img_this_frame = Image.fromarray(tif_arr_this_frame.astype(np.uint8))
    # tif_img_this_frame.save('tmp.png','PNG')
    png_path=os.path.join(segmented_img_root,'{}_0_slice_{}_seg_unified.png'.format(embryo_name,str(imag_idx)))
    png_segmented=Image.open(png_path).resize(image_shape)

    text_height = 100

    combined_image = Image.new(tif_img_this_frame.mode, (image_shape[0]*2,image_shape[1]+text_height), color='black')
    combined_image.paste(tif_img_this_frame,(0,text_height))
    combined_image.paste(png_segmented,(image_shape[0],text_height))

    time_this_tp = "{:.0f}".format((imag_idx+1 - offset_tp) * 10)

    # Add text to the image
    draw = ImageDraw.Draw(combined_image)
    font = ImageFont.truetype('arial.ttf', size=60)
    text1 = 'Time: ' + time_this_tp + ' sec'
    textwidth, textheight = draw.textsize(text1, font)
    width, height = combined_image.size
    x = (width - textwidth) // 2
    y = 20
    draw.text((x, y), text1, fill="white", font=font)

    saving_path_for_this_png=os.path.join(saving_path_the_combined_pngs,'{}_{}.png'.format(embryo_name,str(imag_idx+1).zfill(3)))
    combined_image.save(saving_path_for_this_png,'PNG')

video_name = os.path.join(saving_path_the_combined_pngs,'video.mp4')
IS_FLIPPED_MIRROR = False

# images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
images_paths = glob.glob(os.path.join(saving_path_the_combined_pngs, '*.png'))

# STOP_FRAME=int(len(images)*(4/5))

# print(images[:44])
# frame = cv2.imread(os.path.join(image_folder, images[0]))
frame = cv2.imread(images_paths[0])

height, width, layers = frame.shape

video = cv2.VideoWriter(video_name, 0x7634706d, 10, (width, height))

for image_path in images_paths:
    video.write(cv2.imread(image_path))

cv2.destroyAllWindows()
video.release()







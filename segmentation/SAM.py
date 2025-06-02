import os
import numpy as np
import torch
#import matplotlib.pyplot as plt
import cv2
import sys
from segment_anything import sam_model_registry, SamPredictor



def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)
    


def show_points(coords, labels, ax, marker_size=375):
    pos_points = coords[labels==1]
    neg_points = coords[labels==0]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)   
    


def show_box(box, ax):
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0,0,0,0), lw=2)) 



def load_model(sam_checkpoint, model_type, device):
    sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
    sam.to(device=device)
    predictor = SamPredictor(sam)
    return predictor



def load_raw(raw_path, rootname, tp, slice_num):
    fn = f'{rootname}{tp:03}_p{slice_num+1:02}.tif'
    raw_image_path = os.path.join(raw_path, fn)
    image = cv2.imread(raw_image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image[image >200]=200
    return image



def bounds(arr):
    nonzero_y, nonzero_x = np.nonzero(arr)
    
    min_x = np.min(nonzero_x) if nonzero_x.size else None
    max_x = np.max(nonzero_x) if nonzero_x.size else None
    min_y = np.min(nonzero_y) if nonzero_y.size else None
    max_y = np.max(nonzero_y) if nonzero_y.size else None
    
    return (min_x, max_x, min_y, max_y)



def perimeter(img_data):
    img_data[img_data>0]=255
    img=img_data
    edges = cv2.Canny(img, threshold1=250, threshold2=255)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) >= 1:
        target_contour = max(contours, key=cv2.contourArea)
        epsilon = 0.01 * cv2.arcLength(target_contour, True)  
        approx_curve = cv2.approxPolyDP(target_contour, epsilon, True)

        perimeter = cv2.arcLength(approx_curve, True)
    else:
        perimeter = 0

    return perimeter



def calculate_metrics(data):
    area = np.count_nonzero(data)
    
    p = perimeter(data)
    if area == 0:
        irregularity = 0
    else:
        irregularity = p / np.sqrt(area)
    return area, p, f"{irregularity:.3f}"



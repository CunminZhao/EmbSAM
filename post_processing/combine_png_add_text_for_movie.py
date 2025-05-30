import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import glob
import json

def generate_1plus1_contact_curvature():
    png_sorce_path = r'H:\EmbSAM\revision\figure_5_movie\B_figures'
    png_combined_target_path=r'H:\EmbSAM\revision\figure_5_movie\B_movie_combined'
    # raw_seg_gui_path=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\MembraneProjectData\GUIData\WebData_CMap_cell_label_v3'

    png_embryo_list1 = sorted(glob.glob(os.path.join(png_sorce_path, '*up_view.png')))
    # png_embryo_list2 = sorted(glob.glob(os.path.join(png_sorce_path, '*up_view.png')))

    width, height = 1920, 1080
    mask_width_start = 720
    mask_height_start = 340
    mask_width_stop = 1220
    mask_height_stop = 780
    mask = (mask_width_start, mask_height_start, mask_width_stop, mask_height_stop)

    for idx, png_snaps1 in enumerate(png_embryo_list1):
        # embryo_name, embryo_tp = os.path.basename(png_snaps1).split('_')[1:3]

        # embryo_name_tp = '_'.join([embryo_name, embryo_tp])
        png1 = Image.open(png_snaps1).transpose(Image.FLIP_LEFT_RIGHT).crop(mask)
        # png2 = Image.open(png_embryo_list2[idx]).transpose(Image.FLIP_LEFT_RIGHT).crop(mask)
        # png3 = Image.open(png_embryo_list3[idx]).transpose(Image.FLIP_LEFT_RIGHT).crop(mask)

        # Create a new image with the same mode and size as the first image
        text_height = 80
        # top_text_image=upper_right_png.crop((0,0,))
        combined_image = Image.new(png1.mode, (png1.width * 1, text_height + png1.height * 1), color=(0, 0, 0))

        # Paste the images into the new image
        combined_image.paste(png1, (0, text_height))
        # combined_image.paste(png2, (png1.width, text_height))
        # combined_image.paste(png3, (png1.width * 2, text_height))

        time_this_tp=(int(os.path.basename(png_snaps1).split('_')[1])-127)*10
        # time_this_tp = "{:.2f}".format((255 + 1 - 5) * 1.43)

        # Add text to the image
        draw = ImageDraw.Draw(combined_image)
        font = ImageFont.truetype('arial.ttf', size=50)
        text1 = 'Time: ' + str(time_this_tp) + ' sec'
        textwidth, textheight = draw.textsize(text1, font)
        width, height = combined_image.size
        x = (width - textwidth) // 2
        y = textheight
        draw.text((x, y), text1, fill="white", font=font)

        combined_image.save(os.path.join(png_combined_target_path, 'ABplp_E'+str(idx).zfill(3) + '_combined.png'))



def generate_itk_view_png_sequence():
    png_sorce_path = r'F:\CMap_paper\Figures\3DLapseEmbryo'
    gui_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\MembraneProjectData\GUIData\WebData_CMap_cell_label_v3'

    half_png_list = glob.glob(os.path.join(png_sorce_path, 'SnapsHalfTest', '*.png'))

    width, height = 1920, 1080
    mask_width_start = 420
    mask_height_start = 0
    mask_width_stop = 1500
    mask_height_stop = 970
    mask = (mask_width_start, mask_height_start, mask_width_stop, mask_height_stop)

    for idx, half_png_path in enumerate(half_png_list):
        embryo_name, embryo_tp = os.path.basename(half_png_path).split('_')[:2]

        embryo_name_tp = '_'.join([embryo_name, embryo_tp])

        upper_left_png = Image.open(
            os.path.join(png_sorce_path, 'SnapsFrontUpTest',
                         embryo_name_tp + '_segCell_render_up_looking.png')).transpose(
            Image.FLIP_LEFT_RIGHT).crop(mask)
        upper_right_png = Image.open(
            os.path.join(png_sorce_path, 'SnapsFrontUpTest',
                         embryo_name_tp + '_segCell_render_front_looking.png')).transpose(
            Image.FLIP_LEFT_RIGHT).crop(mask)
        below_right_png = Image.open(os.path.join(png_sorce_path, 'SnapsFrontUpTest',
                                                  embryo_name_tp + '_segCell_render_tail_looking.png')).transpose(
            Image.FLIP_LEFT_RIGHT).crop(mask)
        below_left_png = Image.open(half_png_path).transpose(Image.FLIP_LEFT_RIGHT).crop(mask)

        # Create a new image with the same mode and size as the first image
        text_height = 200
        # top_text_image=upper_right_png.crop((0,0,))
        combined_image = Image.new(upper_left_png.mode,
                                   (upper_left_png.width * 2, text_height + upper_left_png.height * 2), color='black')

        # Paste the images into the new image
        combined_image.paste(upper_left_png, (0, text_height))
        combined_image.paste(upper_right_png, (upper_left_png.width, text_height))
        combined_image.paste(below_left_png, (0, text_height + upper_left_png.height))
        combined_image.paste(below_right_png, (upper_left_png.width, text_height + upper_left_png.height))

        tp_cell_file_path = os.path.join(gui_path, embryo_name, 'TPCell', embryo_name_tp + '_cells.txt')
        # Open the file for reading
        with open(tp_cell_file_path, 'r') as file:
            # Read the contents of the file into a string
            contents = file.read()
            # Split the string into a list using the comma as the delimiter
            my_list = contents.split(',')

        time_this_tp = "{:.2f}".format((idx + 1) * 1.43)
        cell_number_this_tp = str(len(my_list))

        # Add text to the image
        draw = ImageDraw.Draw(combined_image)
        font = ImageFont.truetype('arial.ttf', size=90)
        text1 = 'Time: ' + time_this_tp + ' min' + ' ; ' + 'Cell Number: ' + cell_number_this_tp
        textwidth, textheight = draw.textsize(text1, font)
        width, height = combined_image.size
        x = (width - textwidth) // 2
        y = textheight + 25
        draw.text((x, y), text1, fill="white", font=font)

        # Save the new image
        combined_image.save(os.path.join(png_sorce_path, 'Snaps', embryo_name_tp + '_combined.png'))


def generate_2plus3_view_png_sequence():
    DELETEDCAPTURING = False
    png_sorce_path = r'F:\CMap_paper\Figures\3DLapseEmbryo'
    raw_seg_gui_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\MembraneProjectData\GUIData\WebData_CMap_cell_label_v3'

    tif_embryo_list = glob.glob(os.path.join(png_sorce_path, 'tif', '*.tif'))
    print(tif_embryo_list)

    width, height = 1920, 1080
    mask_width_start = 500
    mask_height_start = 100
    mask_width_stop = 1400
    mask_height_stop = 900
    mask = (mask_width_start, mask_height_start, mask_width_stop, mask_height_stop)

    for idx, half_tif_embryo in enumerate(tif_embryo_list):
        embryo_name, embryo_tp = os.path.basename(half_tif_embryo).split('_')[:2]

        embryo_name_tp = '_'.join([embryo_name, embryo_tp])
        is_changed_tmp = False
        upper_left_png_path = os.path.join(png_sorce_path, 'DeletedSnapsFrontUpTest',
                                           embryo_name_tp + '_segCell_render_up_looking.png')
        if os.path.exists(upper_left_png_path):
            is_changed_tmp = True
        if DELETEDCAPTURING and is_changed_tmp:
            upper_left_png = Image.open(
                os.path.join(png_sorce_path, 'DeletedSnapsFrontUpTest',
                             embryo_name_tp + '_segCell_render_up_looking.png')).crop(mask)
            upper_middle_png = Image.open(
                os.path.join(png_sorce_path, 'DeletedSnapsFrontUpTest',
                             embryo_name_tp + '_segCell_render_front_looking.png')).crop(mask)
            upper_right_png = Image.open(os.path.join(png_sorce_path, 'DeletedSnapsFrontUpTest',
                                                      embryo_name_tp + '_segCell_render_tail_looking.png')).crop(mask)
            below_left_png = Image.open(
                os.path.join(png_sorce_path, 'DeletedSnapsHalfTest',
                             embryo_name_tp + '_up_half_looking.png')).crop(mask)
            below_middle_png = Image.open(
                os.path.join(png_sorce_path, 'DeletedSnapsHalfTest',
                             embryo_name_tp + '_front_half_looking.png')).crop(mask)
            below_right_png = Image.open(
                os.path.join(png_sorce_path, 'DeletedSnapsHalfTest',
                             embryo_name_tp + '_tail_half_looking.png')).crop(mask)
        else:
            upper_left_png = Image.open(
                os.path.join(png_sorce_path, 'SnapsFrontUpTest',
                             embryo_name_tp + '_segCell_render_up_looking.png')).crop(mask)
            upper_middle_png = Image.open(
                os.path.join(png_sorce_path, 'SnapsFrontUpTest',
                             embryo_name_tp + '_segCell_render_front_looking.png')).crop(mask)
            upper_right_png = Image.open(os.path.join(png_sorce_path, 'SnapsFrontUpTest',
                                                      embryo_name_tp + '_segCell_render_tail_looking.png')).crop(mask)
            below_left_png = Image.open(
                os.path.join(png_sorce_path, 'SnapsHalfTest',
                             embryo_name_tp + '_up_half_looking.png')).crop(mask)
            below_middle_png = Image.open(
                os.path.join(png_sorce_path, 'SnapsHalfTest',
                             embryo_name_tp + '_front_half_looking.png')).crop(mask)
            below_right_png = Image.open(
                os.path.join(png_sorce_path, 'SnapsHalfTest',
                             embryo_name_tp + '_tail_half_looking.png')).crop(mask)

        # Create a new image with the same mode and size as the first image
        text_height = 200
        # top_text_image=upper_right_png.crop((0,0,))
        combined_image = Image.new(upper_left_png.mode,
                                   (upper_left_png.width * 3, text_height + upper_left_png.height * 2), color='black')

        # Paste the images into the new image
        combined_image.paste(upper_left_png, (0, text_height))
        combined_image.paste(upper_middle_png, (upper_left_png.width, text_height))
        combined_image.paste(upper_right_png, (upper_left_png.width * 2, text_height))
        combined_image.paste(below_left_png, (0, text_height + upper_left_png.height))
        combined_image.paste(below_middle_png, (upper_left_png.width, text_height + upper_left_png.height))
        combined_image.paste(below_right_png, (upper_left_png.width * 2, text_height + upper_left_png.height))

        tp_cell_file_path = os.path.join(raw_seg_gui_path, embryo_name, 'TPCell', embryo_name_tp + '_cells.txt')
        # Open the file for reading
        with open(tp_cell_file_path, 'r') as file:
            # Read the contents of the file into a string
            contents = file.read()
            # Split the string into a list using the comma as the delimiter
            my_list = contents.split(',')

        time_this_tp = "{:.2f}".format((idx + 1) * 1.43)
        cell_number_this_tp = str(len(my_list))

        # Add text to the image
        draw = ImageDraw.Draw(combined_image)
        font = ImageFont.truetype('arial.ttf', size=90)
        text1 = 'Time: ' + time_this_tp + ' min' + ' ; ' + 'Total Cell Number: ' + cell_number_this_tp
        textwidth, textheight = draw.textsize(text1, font)
        width, height = combined_image.size
        x = (width - textwidth) // 2
        y = textheight + 25
        draw.text((x, y), text1, fill="white", font=font)

        # Save the new image
        if DELETEDCAPTURING:
            combined_image.save(os.path.join(png_sorce_path, 'DeletedSnaps', embryo_name_tp + '_combined.png'))

        else:
            combined_image.save(os.path.join(png_sorce_path, 'Snaps', embryo_name_tp + '_combined.png'))


def generate_1plus3_view_png_IntestineTwisting():
    # DELETEDCAPTURING=False
    png_sorce_path = r'F:\CMap_paper\Figures\Intestine Twisting'
    # raw_seg_gui_path=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\MembraneProjectData\GUIData\WebData_CMap_cell_label_v3'

    png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, 'Snaps1', '*.png'))
    png_embryo_list2 = glob.glob(os.path.join(png_sorce_path, 'Snaps2', '*.png'))
    png_embryo_list3 = glob.glob(os.path.join(png_sorce_path, 'Snaps3', '*.png'))

    # print(tif_embryo_list)
    with open('F:\CMap_paper\Figures\Intestine Twisting\E_cell_number_dict.txt', 'r') as f:
        E_cell_number_dict = json.loads(f.read())

    width, height = 1920, 1080
    mask_width_start = 500
    mask_height_start = 100
    mask_width_stop = 1400
    mask_height_stop = 1000
    mask = (mask_width_start, mask_height_start, mask_width_stop, mask_height_stop)

    for idx, png_snaps1 in enumerate(png_embryo_list1):
        embryo_name, embryo_tp = os.path.basename(png_snaps1).split('_')[1:3]

        embryo_name_tp = '_'.join([embryo_name, embryo_tp])
        png1 = Image.open(png_snaps1).transpose(Image.FLIP_LEFT_RIGHT).crop(mask)
        png2 = Image.open(png_embryo_list2[idx]).transpose(Image.FLIP_LEFT_RIGHT).crop(mask)
        png3 = Image.open(png_embryo_list3[idx]).transpose(Image.FLIP_LEFT_RIGHT).crop(mask)

        # Create a new image with the same mode and size as the first image
        text_height = 300
        # top_text_image=upper_right_png.crop((0,0,))
        combined_image = Image.new(png1.mode, (png1.width * 3, text_height + png1.height * 1), color='black')

        # Paste the images into the new image
        combined_image.paste(png1, (0, text_height))
        combined_image.paste(png2, (png1.width, text_height))
        combined_image.paste(png3, (png1.width * 2, text_height))

        time_this_tp = "{:.2f}".format((int(embryo_tp) + 1 - 5) * 1.43)

        # Add text to the image
        draw = ImageDraw.Draw(combined_image)
        font = ImageFont.truetype('arial.ttf', size=90)
        text1 = 'Time: ' + time_this_tp + ' min' + ' ; ' + 'E Cell Number: ' + str(
            E_cell_number_dict[str(int(embryo_tp) - 1)])
        textwidth, textheight = draw.textsize(text1, font)
        width, height = combined_image.size
        x = (width - textwidth) // 2
        y = textheight + 25
        draw.text((x, y), text1, fill="white", font=font)

        combined_image.save(os.path.join(png_sorce_path, '1plus3figures', embryo_name_tp + '_combined.png'))


def generate_1plus2_z1z3andIntestineTwisting():
    png_sorce_path = r'F:\CMap_paper\Figures\Intestine Twisting'
    # raw_seg_gui_path=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\MembraneProjectData\GUIData\WebData_CMap_cell_label_v3'

    png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, 'InstetineFrontSnaps', '*.png'))
    png_embryo_list2 = glob.glob(os.path.join(png_sorce_path, 'Z1Z2InstetineFrontSnaps', '*.png'))

    # print(tif_embryo_list)
    with open('F:\CMap_paper\Figures\Intestine Twisting\E_cell_number_dict.txt', 'r') as f:
        E_cell_number_dict = json.loads(f.read())

    width, height = 1920, 1080
    mask_width_start = 400
    mask_height_start = 100
    mask_width_stop = 1500
    mask_height_stop = 1080
    mask = (mask_width_start, mask_height_start, mask_width_stop, mask_height_stop)

    for idx, png_snaps1 in enumerate(png_embryo_list1):
        # embryo_name, embryo_tp = os.path.basename(png_snaps1).split('_')[1:3]

        # embryo_name_tp = '_'.join([embryo_name, embryo_tp])
        png1 = Image.open(png_snaps1).transpose(Image.FLIP_LEFT_RIGHT).crop(mask)
        png2 = Image.open(png_embryo_list2[idx]).transpose(Image.FLIP_LEFT_RIGHT).crop(mask)
        # png3 = Image.open(png_embryo_list3[idx]).transpose(Image.FLIP_LEFT_RIGHT).crop(mask)

        # Create a new image with the same mode and size as the first image
        text_height = 300
        # top_text_image=upper_right_png.crop((0,0,))
        combined_image = Image.new(png1.mode, (png1.width * 2, text_height + png1.height * 1), color=(70, 71, 71))

        # Paste the images into the new image
        combined_image.paste(png1, (0, text_height))
        combined_image.paste(png2, (png1.width, text_height))
        # combined_image.paste(png3, (png1.width * 2, text_height))

        time_this_tp = "{:.2f}".format((255 + 1 - 5) * 1.43)

        # Add text to the image
        draw = ImageDraw.Draw(combined_image)
        font = ImageFont.truetype('arial.ttf', size=90)
        text1 = 'Time: ' + time_this_tp + ' min' + ' ; ' + 'E Cell Number: ' + str(
            E_cell_number_dict[str(255 - 1)])
        textwidth, textheight = draw.textsize(text1, font)
        width, height = combined_image.size
        x = (width - textwidth) // 2
        y = textheight + 25
        draw.text((x, y), text1, fill="white", font=font)

        combined_image.save(os.path.join(png_sorce_path, 'rotation1plus2figures', str(idx).zfill(3) + '_combined.png'))


def generate_1plus1_gastrulation():
    # Read the list from the text file

    png_sorce_path = r'F:\CMap_paper\Figures\Gastrulation\Snaps1'
    dst_png_path = r'F:\CMap_paper\Figures\Gastrulation\Snaps1textadded'
    png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, '*.png'))[19:138]
    # png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, '*.png'))[26:188]
    raw_seg_gui_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\MembraneProjectData\GUIData\WebData_CMap_cell_label_v3'

    # print(tif_embryo_list)
    # cell_number_this = 21

    mask_width_start = 400
    mask_height_start = 150
    mask_width_stop = 1550
    mask_height_stop = 1000
    mask = (mask_width_start, mask_height_start, mask_width_stop, mask_height_stop)

    target_mtl_color_list = [
        # (6,0,237),
        (0, 100, 100),
        (0, 240, 0),
        (247, 2, 245),
        (240, 0, 0),
        (1, 1, 1),
        (242, 244, 0),
        (200, 200, 200)
    ]
    target_mtl_name_list = [
        # 'Gastrulating AB cells',
        'Gastrulating MS cells', 'Gastrulating E cells', 'Gastrulating C cells', 'Gastrulating D cells',
        'Gastrulating Z2/Z3 cells', 'P2/P3/P4 cells',
        'Other cells']
    text_height = 100

    color_bar_text_width = 450
    rectangle_size = 30

    for idx, png_snaps1 in enumerate(png_embryo_list1):
        embryo_name, embryo_tp = os.path.basename(png_snaps1).split('_')[1:3]

        png1 = Image.open(png_snaps1).crop(mask)

        # Create a new image with the same mode and size as the first image
        # text_height = 150
        # top_text_image=upper_right_png.crop((0,0,))
        combined_image = Image.new(png1.mode, (png1.width * 1 + color_bar_text_width, text_height + png1.height * 1),
                                   color=(133, 133, 133))

        # Paste the images into the new image
        combined_image.paste(png1, (0, 0 + text_height))
        # width, height = 1920, 1150

        tp_cell_file_path = os.path.join(raw_seg_gui_path, embryo_name, 'TPCell',
                                         embryo_name + '_' + embryo_tp + '_cells.txt')
        # Open the file for reading
        with open(tp_cell_file_path, 'r') as file:
            # Read the contents of the file into a string
            contents = file.read()
            # Split the string into a list using the comma as the delimiter
            my_list = contents.split(',')

        # time_this_tp = "{:.2f}".format((idx + 1) * 1.43)
        cell_number_this_tp = str(len(my_list))
        time_this_tp = "{:.2f}".format((int(embryo_tp) - 5 + 1) * 1.43)
        draw = ImageDraw.Draw(combined_image)
        font = ImageFont.truetype('arial.ttf', size=50)
        text1 = 'Time: ' + time_this_tp + ' min' + ' ; ' + 'Total Cell Number: ' + cell_number_this_tp
        # text2 =
        textwidth, textheight = draw.textsize(text1, font)
        width, height = combined_image.size
        x = (width - textwidth) // 2
        y = textheight * 1.5
        draw.text((x, y), text1, fill="black", font=font)
        #
        # textwidth, textheight = draw.textsize(text2, font)
        # x = (width - textwidth) // 2
        # y = textheight * 2 + 25
        # draw.text((x, y), text2, fill="white", font=font)

        draw = ImageDraw.Draw(combined_image)
        for lineage_idx, [lineage_name, color_rgb] in enumerate(zip(target_mtl_name_list, target_mtl_color_list)):
            print(lineage_idx, lineage_name, color_rgb)
            rect_x0 = 1150
            rect_y1 = (height + text_height - len(
                target_mtl_name_list) * rectangle_size * 2) // 2 + rectangle_size + lineage_idx * rectangle_size * 2

            rect_x1 = rect_x0 + rectangle_size

            rect_y0 = rect_y1 - rectangle_size
            # create rectangle image
            print((rect_x0, rect_y0, rect_x1, rect_y1))
            draw.rectangle((rect_x0, rect_y0, rect_x1, rect_y1), fill=color_rgb)

            font = ImageFont.truetype('arial.ttf', size=30)
            text_this = '  ' + lineage_name
            # textwidth, textheight = draw.textsize(text_this, font)
            draw.text((rect_x1, rect_y0), text_this, fill="black", font=font)

        combined_image.save(os.path.join(dst_png_path, str(idx).zfill(3) + '.png'))


def generate_1plus1_skininterdigitating():
    png_sorce_path = r'F:\CMap_paper\Figures\Skin Interdigitation\Skin_snaps\200109plc1p1'
    dst_png_path = r'F:\CMap_paper\Figures\Skin Interdigitation\Skin_snaps\200109plc1p1textadded'
    png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, '*.png'))

    # print(tif_embryo_list)
    cell_number_this = 21

    width, height = 1920, 1080
    mask_width_start = 500
    mask_height_start = 300
    mask_width_stop = 1400
    mask_height_stop = 800
    mask = (mask_width_start, mask_height_start, mask_width_stop, mask_height_stop)

    for idx, png_snaps1 in enumerate(png_embryo_list1):
        if len(os.path.basename(png_snaps1).split('_')) > 2:
            embryo_name, embryo_tp = os.path.basename(png_snaps1).split('_')[1:3]
        else:
            embryo_tp = 173

        png1 = Image.open(png_snaps1).crop(mask)

        # Create a new image with the same mode and size as the first image
        text_height = 150
        # top_text_image=upper_right_png.crop((0,0,))
        combined_image = Image.new(png1.mode, (png1.width * 1, text_height + png1.height * 1), color='black')

        # Paste the images into the new image
        combined_image.paste(png1, (0, text_height))

        time_this_tp = "{:.2f}".format((int(embryo_tp) - 5 + 1) * 1.43)

        # Add text to the image
        draw = ImageDraw.Draw(combined_image)
        font = ImageFont.truetype('arial.ttf', size=50)
        text1 = 'Time: ' + time_this_tp + ' min' + ' ; '
        text2 = 'Total Cell Number: ' + str(cell_number_this)
        textwidth, textheight = draw.textsize(text1, font)
        width, height = combined_image.size
        x = (width - textwidth) // 2
        y = textheight
        draw.text((x, y), text1, fill="white", font=font)

        textwidth, textheight = draw.textsize(text2, font)
        x = (width - textwidth) // 2
        y = textheight * 2 + 25
        draw.text((x, y), text2, fill="white", font=font)

        combined_image.save(os.path.join(dst_png_path, str(idx).zfill(3) + '.png'))


def generate_1plus3_neuron_development():
    png_sorce_path = r'F:\CMap_paper\Figures\Neuron Development\200113plc1p2_snaps'
    dst_png_path = r'F:\CMap_paper\Figures\Neuron Development\textadded'
    png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, '*up.png'))
    png_embryo_list2 = glob.glob(os.path.join(png_sorce_path, '*front.png'))
    png_embryo_list3 = glob.glob(os.path.join(png_sorce_path, '*head.png'))

    # png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, '*.png'))[26:188]
    raw_seg_gui_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\MembraneProjectData\GUIData\WebData_CMap_cell_label_v3'

    # print(tif_embryo_list)
    # cell_number_this = 21

    mask_width_start = 400
    mask_height_start = 150
    mask_width_stop = 1600
    mask_height_stop = 1000
    mask = (mask_width_start, mask_height_start, mask_width_stop, mask_height_stop)

    target_mtl_color_list = [
        # (157, 157, 157), # unspecified
        (66, 141, 72),  # neuron
        (248, 4, 6)  # skinnnnnn

    ]
    target_mtl_name_list = [
        # 'Unspecified ancestors of neuron cells',
        'Neuron cells',
        'Skin cells']
    text_height = 200
    color_bar_height = 150

    rectangle_size = 60

    for idx, png_snaps1_path in enumerate(png_embryo_list1):
        embryo_name, embryo_tp = os.path.basename(png_snaps1_path).split('_')[:2]

        png1 = Image.open(png_snaps1_path).crop(mask)
        png2 = Image.open(png_embryo_list2[idx]).crop(mask)
        png3 = Image.open(png_embryo_list3[idx]).crop(mask)

        # Create a new image with the same mode and size as the first image
        # text_height = 150
        # top_text_image=upper_right_png.crop((0,0,))
        combined_image = Image.new(png1.mode, (png1.width * 3, text_height + png1.height * 1 + color_bar_height),
                                   color='black')

        # Paste the images into the new image
        combined_image.paste(png1, (0, 0 + text_height))
        combined_image.paste(png2, (png1.width * 1, 0 + text_height))
        combined_image.paste(png3, (png1.width * 2, 0 + text_height))

        # width, height = 1920, 1150

        tp_cell_file_path = os.path.join(raw_seg_gui_path, embryo_name, 'TPCell',
                                         embryo_name + '_' + embryo_tp + '_cells.txt')
        # Open the file for reading
        with open(tp_cell_file_path, 'r') as file:
            # Read the contents of the file into a string
            contents = file.read()
            # Split the string into a list using the comma as the delimiter
            my_list = contents.split(',')

        title_font_size = int(rectangle_size * 1.5)
        legend_font_size = rectangle_size
        # time_this_tp = "{:.2f}".format((idx + 1) * 1.43)
        cell_number_this_tp = str(len(my_list))
        time_this_tp = "{:.2f}".format((int(embryo_tp) - 1) * 1.43)
        draw = ImageDraw.Draw(combined_image)
        font = ImageFont.truetype('arial.ttf', size=title_font_size)
        text1 = 'Time: ' + time_this_tp + ' min' + ' ; ' + 'Total Cell Number: ' + cell_number_this_tp
        # text2 =
        textwidth, textheight = draw.textsize(text1, font)
        width, height = combined_image.size
        x = (width - textwidth) // 2
        y = textheight
        draw.text((x, y), text1, fill="white", font=font)
        #
        # textwidth, textheight = draw.textsize(text2, font)
        # x = (width - textwidth) // 2
        # y = textheight * 2 + 25
        # draw.text((x, y), text2, fill="white", font=font)

        draw = ImageDraw.Draw(combined_image)
        for lineage_idx, [lineage_name, color_rgb] in enumerate(zip(target_mtl_name_list, target_mtl_color_list)):
            print(lineage_idx, lineage_name, color_rgb)
            rect_x0 = width // len(target_mtl_name_list) * lineage_idx + 450
            rect_y1 = height - color_bar_height // 4 * 3 + rectangle_size // 2

            rect_x1 = rect_x0 + rectangle_size

            rect_y0 = rect_y1 - rectangle_size
            # create rectangle image
            print((rect_x0, rect_y0, rect_x1, rect_y1))
            draw.rectangle((rect_x0, rect_y0, rect_x1, rect_y1), fill=color_rgb)

            font = ImageFont.truetype('arial.ttf', size=legend_font_size)
            text_this = '  ' + lineage_name
            # textwidth, textheight = draw.textsize(text_this, font)
            draw.text((rect_x1, rect_y0), text_this, fill="white", font=font)

        combined_image.save(os.path.join(dst_png_path, str(idx).zfill(3) + '.png'))


def generate_1plus3_muscle_bodywall():
    png_sorce_path = r'F:\CMap_paper\Figures\Muscle Cells\Snaps'
    dst_png_path = r'F:\CMap_paper\Figures\Muscle Cells\1plus3200113p2'
    png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, '*up.png'))
    png_embryo_list2 = glob.glob(os.path.join(png_sorce_path, '*front.png'))
    png_embryo_list3 = glob.glob(os.path.join(png_sorce_path, '*head.png'))

    # png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, '*.png'))[26:188]
    raw_seg_gui_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\MembraneProjectData\GUIData\WebData_CMap_cell_label_v3'

    # print(tif_embryo_list)
    # cell_number_this = 21

    mask_width_start = 400
    mask_height_start = 150
    mask_width_stop = 1550
    mask_height_stop = 1000
    mask = (mask_width_start, mask_height_start, mask_width_stop, mask_height_stop)

    target_mtl_color_list = [
        (6, 0, 237),
        (0, 100, 100),
        (247, 2, 245),
        (240, 0, 0),
        (170, 170, 170)
    ]
    # target_mtl_name_list = ['AB', 'MS', 'C', 'D', 'P']
    target_mtl_name_list = ['AB cell',
                            'MS cells', 'C cells', ' D cells', 'P1/P2/P3 cells']
    text_height = 200
    color_bar_height = 150

    rectangle_size = 60

    for idx, png_snaps1_path in enumerate(png_embryo_list1):
        embryo_name, embryo_tp = os.path.basename(png_snaps1_path).split('_')[1:3]

        png1 = Image.open(png_snaps1_path).crop(mask)
        png2 = Image.open(png_embryo_list2[idx]).crop(mask)
        png3 = Image.open(png_embryo_list3[idx]).crop(mask)

        # Create a new image with the same mode and size as the first image
        # text_height = 150
        # top_text_image=upper_right_png.crop((0,0,))
        combined_image = Image.new(png1.mode, (png1.width * 3, text_height + png1.height * 1 + color_bar_height),
                                   color='black')

        # Paste the images into the new image
        combined_image.paste(png1, (0, 0 + text_height))
        combined_image.paste(png2, (png1.width * 1, 0 + text_height))
        combined_image.paste(png3, (png1.width * 2, 0 + text_height))

        # width, height = 1920, 1150

        tp_cell_file_path = os.path.join(raw_seg_gui_path, embryo_name, 'TPCell',
                                         embryo_name + '_' + embryo_tp + '_cells.txt')
        # Open the file for reading
        with open(tp_cell_file_path, 'r') as file:
            # Read the contents of the file into a string
            contents = file.read()
            # Split the string into a list using the comma as the delimiter
            my_list = contents.split(',')

        title_font_size = int(rectangle_size * 1.5)
        legend_font_size = rectangle_size
        # time_this_tp = "{:.2f}".format((idx + 1) * 1.43)
        cell_number_this_tp = str(len(my_list))
        time_this_tp = "{:.2f}".format((int(embryo_tp) - 1) * 1.43)
        draw = ImageDraw.Draw(combined_image)
        font = ImageFont.truetype('arial.ttf', size=title_font_size)
        text1 = 'Time: ' + time_this_tp + ' min' + ' ; ' + 'Total Cell Number: ' + cell_number_this_tp
        # text2 =
        textwidth, textheight = draw.textsize(text1, font)
        width, height = combined_image.size
        x = (width - textwidth) // 2
        y = textheight
        draw.text((x, y), text1, fill="white", font=font)
        #
        # textwidth, textheight = draw.textsize(text2, font)
        # x = (width - textwidth) // 2
        # y = textheight * 2 + 25
        # draw.text((x, y), text2, fill="white", font=font)

        draw = ImageDraw.Draw(combined_image)
        for lineage_idx, [lineage_name, color_rgb] in enumerate(zip(target_mtl_name_list, target_mtl_color_list)):
            print(lineage_idx, lineage_name, color_rgb)
            rect_x0 = width // len(target_mtl_name_list) * lineage_idx + 100
            rect_y1 = height - color_bar_height // 4 * 3 + rectangle_size // 2

            rect_x1 = rect_x0 + rectangle_size

            rect_y0 = rect_y1 - rectangle_size
            # create rectangle image
            print((rect_x0, rect_y0, rect_x1, rect_y1))
            draw.rectangle((rect_x0, rect_y0, rect_x1, rect_y1), fill=color_rgb)

            font = ImageFont.truetype('arial.ttf', size=legend_font_size)
            text_this = '  ' + lineage_name
            # textwidth, textheight = draw.textsize(text_this, font)
            draw.text((rect_x1, rect_y0), text_this, fill="white", font=font)

        combined_image.save(os.path.join(dst_png_path, str(idx).zfill(3) + '.png'))
def generate_1plus3_muscle_bodywall_with_ABsister():
    png_sorce_path = r'F:\CMap_paper\Figures\Body wall muscle with AB sister\snaps'
    dst_png_path = r'F:\CMap_paper\Figures\Body wall muscle with AB sister\1plus3pngs'
    png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, '*up.png'))
    png_embryo_list2 = glob.glob(os.path.join(png_sorce_path, '*front.png'))
    png_embryo_list3 = glob.glob(os.path.join(png_sorce_path, '*head.png'))

    # png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, '*.png'))[26:188]
    raw_seg_gui_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\MembraneProjectData\GUIData\WebData_CMap_cell_label_v3'

    # print(tif_embryo_list)
    # cell_number_this = 21

    mask_width_start = 400
    mask_height_start = 150
    mask_width_stop = 1550
    mask_height_stop = 1000
    mask = (mask_width_start, mask_height_start, mask_width_stop, mask_height_stop)

    target_mtl_color_list = [
        (6, 0, 237),
        # (50, 50, 255),

        (0, 100, 100),
        (247, 2, 245),
        (240, 0, 0),
        (170, 170, 170)
    ]
    # target_mtl_name_list = ['AB', 'MS', 'C', 'D', 'P']
    target_mtl_name_list = ['AB cells',
                            'MS cells', 'C cells', ' D cells', 'P1/P2/P3 cells']
    text_height = 200
    color_bar_height = 150

    rectangle_size = 60

    for idx, png_snaps1_path in enumerate(png_embryo_list1):
        embryo_name, embryo_tp = os.path.basename(png_snaps1_path).split('_')[1:3]

        png1 = Image.open(png_snaps1_path).crop(mask)
        png2 = Image.open(png_embryo_list2[idx]).crop(mask)
        png3 = Image.open(png_embryo_list3[idx]).crop(mask)

        # Create a new image with the same mode and size as the first image
        # text_height = 150
        # top_text_image=upper_right_png.crop((0,0,))
        combined_image = Image.new(png1.mode, (png1.width * 3, text_height + png1.height * 1 + color_bar_height),
                                   color='black')

        # Paste the images into the new image
        combined_image.paste(png1, (0, 0 + text_height))
        combined_image.paste(png2, (png1.width * 1, 0 + text_height))
        combined_image.paste(png3, (png1.width * 2, 0 + text_height))

        # width, height = 1920, 1150

        tp_cell_file_path = os.path.join(raw_seg_gui_path, embryo_name, 'TPCell',
                                         embryo_name + '_' + embryo_tp + '_cells.txt')
        # Open the file for reading
        with open(tp_cell_file_path, 'r') as file:
            # Read the contents of the file into a string
            contents = file.read()
            # Split the string into a list using the comma as the delimiter
            my_list = contents.split(',')

        title_font_size = int(rectangle_size * 1.5)
        legend_font_size = rectangle_size
        # time_this_tp = "{:.2f}".format((idx + 1) * 1.43)
        cell_number_this_tp = str(len(my_list))
        time_this_tp = "{:.2f}".format((int(embryo_tp) - 1) * 1.43)
        draw = ImageDraw.Draw(combined_image)
        font = ImageFont.truetype('arial.ttf', size=title_font_size)
        text1 = 'Time: ' + time_this_tp + ' min' + ' ; ' + 'Total Cell Number: ' + cell_number_this_tp
        # text2 =
        textwidth, textheight = draw.textsize(text1, font)
        width, height = combined_image.size
        x = (width - textwidth) // 2
        y = textheight
        draw.text((x, y), text1, fill="white", font=font)
        #
        # textwidth, textheight = draw.textsize(text2, font)
        # x = (width - textwidth) // 2
        # y = textheight * 2 + 25
        # draw.text((x, y), text2, fill="white", font=font)

        draw = ImageDraw.Draw(combined_image)
        for lineage_idx, [lineage_name, color_rgb] in enumerate(zip(target_mtl_name_list, target_mtl_color_list)):
            print(lineage_idx, lineage_name, color_rgb)
            rect_x0 = width // len(target_mtl_name_list) * lineage_idx + 50
            rect_y1 = height - color_bar_height // 4 * 3 + rectangle_size // 2

            rect_x1 = rect_x0 + rectangle_size

            rect_y0 = rect_y1 - rectangle_size
            # create rectangle image
            print((rect_x0, rect_y0, rect_x1, rect_y1))
            draw.rectangle((rect_x0, rect_y0, rect_x1, rect_y1), fill=color_rgb)

            font = ImageFont.truetype('arial.ttf', size=legend_font_size)
            text_this = '  ' + lineage_name
            # textwidth, textheight = draw.textsize(text_this, font)
            draw.text((rect_x1, rect_y0), text_this, fill="white", font=font)

        combined_image.save(os.path.join(dst_png_path, str(idx).zfill(3) + '.png'))

def generate_color_box_png_lineage_fate():
    png_sorce_path = r'F:\CMap_paper\Figures\Movie Lineage\Snaps'
    png_dst_path = r'F:\CMap_paper\Figures\Movie Lineage\SnapsColorTextAdded'
    png_file_list = glob.glob(os.path.join(png_sorce_path, '*.png'))
    raw_seg_gui_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\MembraneProjectData\GUIData\WebData_CMap_cell_label_v3'

    color_list=[(6,0,237),(247,2,245),(225,156,152),(157,157,157),(0,230,226),(242,244,0)]
    color_text_list=['AB','C','D','E','MS','P']

    # png_sorce_path = r'F:\CMap_paper\Figures\Movie Fate\200113plc1p2Snaps'
    # png_dst_path = r'F:\CMap_paper\Figures\Movie Fate\200113plc1p2SnapsColorTextAdded'
    # png_file_list = glob.glob(os.path.join(png_sorce_path, '*.png'))
    # raw_seg_gui_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\MembraneProjectData\GUIData\WebData_CMap_cell_label_v3'
    # color_list = [(66, 141, 72), (248, 4, 6), (21, 2, 12), (10, 13, 222), (254, 0, 252), (19, 209, 245),
    #               (189, 183, 107), (157, 157, 157),(255, 255, 0)]
    # color_text_list = ['Neuron', 'Skin', 'Muscle', 'Pharynx', 'Intestine', 'Germline', 'Death', 'Unspecified', 'Others']
    # text_number

    # print(len(png_file_list))
    text_height_title = 100
    mask_width_start = 420
    mask_height_start = 200
    # mask_width_stop = 1700  # cell fate ,long legend
    mask_width_stop = 1600 # cell lineage, short legend
    mask_height_stop = 880  # CELL LIANGE SHORT LEGEND
    # mask_height_stop=930 # cell fate
    mask = (mask_width_start, mask_height_start, mask_width_stop, mask_height_stop)
    _, singleheight = Image.open(png_file_list[0]).crop(mask).size

    rectangle_size = 30

    for png_path in png_file_list:
        embryo_name, embryo_tp = os.path.basename(png_path).split('_')[1:3]
        print(embryo_name, embryo_tp)
        drawing_png = Image.open(png_path).crop(mask)

        draw = ImageDraw.Draw(drawing_png)

        for lineage_idx, [lineage_name, color_rgb] in enumerate(zip(color_text_list, color_list)):
            # print(lineage_idx,lineage_name,color_rgb)
            rect_x0 = 1050
            rect_y1 = (singleheight - len(
                color_text_list) * rectangle_size * 2) // 2 + rectangle_size + lineage_idx * rectangle_size * 2 - 10

            rect_x1 = rect_x0 + rectangle_size

            rect_y0 = rect_y1 - rectangle_size
            # create rectangle image
            print((rect_x0, rect_y0, rect_x1, rect_y1))
            draw.rectangle((rect_x0, rect_y0, rect_x1, rect_y1), fill=color_rgb)

            font = ImageFont.truetype('arial.ttf', size=30)
            text_this = ' ' + lineage_name + ' '
            textwidth, textheight = draw.textsize(text_this, font)
            draw.text((rect_x1, rect_y0), text_this, fill="black", font=font)

        combined_image = Image.new(drawing_png.mode, (drawing_png.width, drawing_png.height + text_height_title),
                                   color=(192, 192, 192))
        combined_image.paste(drawing_png, (0, 0 + text_height_title))
        title_font_size = int(rectangle_size * 2)
        tp_cell_file_path = os.path.join(raw_seg_gui_path, embryo_name, 'TPCell',
                                         embryo_name + '_' + embryo_tp + '_cells.txt')
        # Open the file for reading
        with open(tp_cell_file_path, 'r') as file:
            # Read the contents of the file into a string
            contents = file.read()
            # Split the string into a list using the comma as the delimiter
            my_list = contents.split(',')
        cell_number_this_tp = str(len(my_list))
        time_this_tp = "{:.2f}".format((int(embryo_tp) - 1) * 1.43)
        draw = ImageDraw.Draw(combined_image)
        font = ImageFont.truetype('arial.ttf', size=title_font_size)
        text1 = 'Time: ' + time_this_tp + ' min' + ' ; ' + 'Total Cell Number: ' + cell_number_this_tp
        # text2 =
        textwidth, textheight = draw.textsize(text1, font)
        wholewidth, wholeheight = combined_image.size
        x = (wholewidth - textwidth) // 2
        y = textheight * 0.7
        draw.text((x, y), text1, fill="black", font=font)

        combined_image.save(os.path.join(png_dst_path, os.path.basename(png_path)))


def generate_1plus3_kidney_cells():
    # 200109plc1p1  200113plc1p2  200326plc1p4
    embryo_name_this = '200109plc1p1'
    with open(os.path.join(r'F:\CMap_paper\Figures\KidneyCell\{}'.format(embryo_name_this),
                           embryo_name_this + '_appearance.txt'), 'r') as f:
        embryo_appearance_list = json.loads(f.read())
    png_sorce_path = r'F:\CMap_paper\Figures\KidneyCell\{}_snaps'.format(embryo_name_this)
    dst_png_path = r'F:\CMap_paper\Figures\KidneyCell\{}_textadded'.format(embryo_name_this)
    png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, '*up.png'))
    png_embryo_list2 = glob.glob(os.path.join(png_sorce_path, '*front.png'))
    png_embryo_list3 = glob.glob(os.path.join(png_sorce_path, '*head.png'))

    # png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, '*.png'))[26:188]
    raw_seg_gui_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\MembraneProjectData\GUIData\WebData_CMap_cell_label_v3'

    # print(tif_embryo_list)
    # cell_number_this = 21

    mask_width_start = 450
    mask_height_start = 100
    mask_width_stop = 1480
    mask_height_stop = 1050
    mask = (mask_width_start, mask_height_start, mask_width_stop, mask_height_stop)

    target_mtl_color_list = [
        (218, 55, 56),
        (55, 220, 57),
        (189, 183, 107)
    ]
    target_mtl_name_list = ['Kidney cell and its ancestor',
                            'Non-apoptotic sister of the kidney cell and its ancestor',
                            'Apoptotic sister of the kidney cell and its ancestor'
                            ]
    text_height = 200
    color_bar_height = 650

    rectangle_size = 60

    for idx, png_snaps1_path in enumerate(png_embryo_list1):
        embryo_name, embryo_tp = os.path.basename(png_snaps1_path).split('_')[:2]
        print(embryo_name, embryo_tp)
        png1 = Image.open(png_snaps1_path).crop(mask)
        png2 = Image.open(png_embryo_list2[idx]).crop(mask)
        png3 = Image.open(png_embryo_list3[idx]).crop(mask)

        # Create a new image with the same mode and size as the first image
        # text_height = 150
        # top_text_image=upper_right_png.crop((0,0,))
        combined_image = Image.new(png1.mode, (png1.width * 3, text_height + png1.height * 1 + color_bar_height),
                                   color='black')

        # Paste the images into the new image
        combined_image.paste(png1, (0, 0 + text_height))
        combined_image.paste(png2, (png1.width * 1, 0 + text_height))
        combined_image.paste(png3, (png1.width * 2, 0 + text_height))

        # width, height = 1920, 1150

        tp_cell_file_path = os.path.join(raw_seg_gui_path, embryo_name, 'TPCell',
                                         embryo_name + '_' + embryo_tp + '_cells.txt')
        # Open the file for reading
        with open(tp_cell_file_path, 'r') as file:
            # Read the contents of the file into a string
            contents = file.read()
            # Split the string into a list using the comma as the delimiter
            my_list = contents.split(',')

        title_font_size = int(rectangle_size * 1.5)
        legend_font_size = rectangle_size
        # time_this_tp = "{:.2f}".format((idx + 1) * 1.43)
        cell_number_this_tp = str(len(my_list))
        time_this_tp = "{:.2f}".format((int(embryo_tp) - 1) * 1.43)
        draw = ImageDraw.Draw(combined_image)
        font = ImageFont.truetype('arial.ttf', size=title_font_size)
        text1 = 'Time: ' + time_this_tp + ' min' + ' ; ' + 'Total Cell Number: ' + cell_number_this_tp
        # text2 =
        textwidth, textheight = draw.textsize(text1, font)
        width, height = combined_image.size
        x = (width - textwidth) // 2
        y = textheight
        draw.text((x, y), text1, fill="white", font=font)

        # =============================================
        lineage_idx = 0
        draw = ImageDraw.Draw(combined_image)
        lineage_name = target_mtl_name_list[lineage_idx]
        color_rgb = target_mtl_color_list[lineage_idx]
        # print(lineage_idx, lineage_name, color_rgb)
        rect_x0 = 800
        rect_y1 = height - color_bar_height // 4 * 3 + rectangle_size // 2

        rect_x1 = rect_x0 + rectangle_size

        rect_y0 = rect_y1 - rectangle_size
        # create rectangle image
        # print((rect_x0, rect_y0, rect_x1, rect_y1))
        draw.rectangle((rect_x0, rect_y0, rect_x1, rect_y1), fill=color_rgb)

        font = ImageFont.truetype('arial.ttf', size=legend_font_size)
        text_this = '      ' + lineage_name
        # textwidth, textheight = draw.textsize(text_this, font)
        draw.text((rect_x1, rect_y0), text_this, fill="white", font=font)
        cell_names_list_tmp = embryo_appearance_list[lineage_idx].get(embryo_name + '_' + embryo_tp + '_' + 'segCell',
                                                                      [])
        if 'ABplpappaap' in cell_names_list_tmp:
            drawing_cell_names = '      ABplpappaap (kidney cell)'
        else:
            drawing_cell_names = '      ' + ','.join(cell_names_list_tmp)
        # textwidth, textheight = draw.textsize(text_this, font)
        draw.text((rect_x1, rect_y0 - rectangle_size * 1.2), drawing_cell_names, fill="white", font=font)

        # ================================================================
        lineage_idx = 1
        draw = ImageDraw.Draw(combined_image)
        lineage_name = target_mtl_name_list[lineage_idx]
        color_rgb = target_mtl_color_list[lineage_idx]
        # print(lineage_idx, lineage_name, color_rgb)
        rect_x0 = 800
        rect_y1 = height - color_bar_height // 4 * 3 + rectangle_size // 2 + 3.5 * rectangle_size

        rect_x1 = rect_x0 + rectangle_size

        rect_y0 = rect_y1 - rectangle_size
        # create rectangle image
        # print((rect_x0, rect_y0, rect_x1, rect_y1))
        draw.rectangle((rect_x0, rect_y0, rect_x1, rect_y1), fill=color_rgb)

        font = ImageFont.truetype('arial.ttf', size=legend_font_size)
        text_this = '      ' + lineage_name
        # textwidth, textheight = draw.textsize(text_this, font)
        draw.text((rect_x1, rect_y0), text_this, fill="white", font=font)
        drawing_cell_names = '      ' + ','.join(
            embryo_appearance_list[lineage_idx].get(embryo_name + '_' + embryo_tp + '_' + 'segCell', []))
        # textwidth, textheight = draw.textsize(text_this, font)
        draw.text((rect_x1, rect_y0 - rectangle_size * 1.2), drawing_cell_names, fill="white", font=font)

        # ========================================================================
        lineage_idx = 2
        draw = ImageDraw.Draw(combined_image)
        lineage_name = target_mtl_name_list[lineage_idx]
        color_rgb = target_mtl_color_list[lineage_idx]
        # print(lineage_idx, lineage_name, color_rgb)
        rect_x0 = 800
        rect_y1 = height - color_bar_height // 4 * 3 + rectangle_size // 2 + 7 * rectangle_size

        rect_x1 = rect_x0 + rectangle_size

        rect_y0 = rect_y1 - rectangle_size
        # create rectangle image
        # print((rect_x0, rect_y0, rect_x1, rect_y1))
        draw.rectangle((rect_x0, rect_y0, rect_x1, rect_y1), fill=color_rgb)

        font = ImageFont.truetype('arial.ttf', size=legend_font_size)
        text_this = '      ' + lineage_name
        # textwidth, textheight = draw.textsize(text_this, font)
        draw.text((rect_x1, rect_y0), text_this, fill="white", font=font)
        drawing_cell_names = '      ' + ','.join(
            embryo_appearance_list[lineage_idx].get(embryo_name + '_' + embryo_tp + '_' + 'segCell', []))
        # textwidth, textheight = draw.textsize(text_this, font)
        draw.text((rect_x1, rect_y0 - rectangle_size * 1.2), drawing_cell_names, fill="white", font=font)

        combined_image.save(os.path.join(dst_png_path, embryo_name + '_' + embryo_tp + '.png'))


def generate_1plus5_tissue_pngs():
    tissue_list = ['neuron', 'pharynx', 'skin', 'muscle', 'intestine']
    png_sorce_path = r'F:\CMap_paper\Figures\TissueMovieNoLoss'
    dst_png_path = r'F:\CMap_paper\Figures\TissueMovieNoLoss\textadded'
    png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, '{}'.format(tissue_list[0]), '*.png'))
    png_embryo_list2 = glob.glob(os.path.join(png_sorce_path, '{}'.format(tissue_list[1]), '*.png'))
    png_embryo_list3 = glob.glob(os.path.join(png_sorce_path, '{}'.format(tissue_list[2]), '*.png'))
    png_embryo_list4 = glob.glob(os.path.join(png_sorce_path, '{}'.format(tissue_list[3]), '*.png'))
    png_embryo_list5 = glob.glob(os.path.join(png_sorce_path, '{}'.format(tissue_list[4]), '*.png'))
    png_axis_list = glob.glob(os.path.join(png_sorce_path, '{}'.format('axis_rotating'), '*.png'))

    mask_width_start = 450
    mask_height_start = 150
    mask_width_stop = 1480
    mask_height_stop = 950
    mask = (mask_width_start, mask_height_start, mask_width_stop, mask_height_stop)

    axis_mask_width_start = 420
    axis_mask_height_start = 250
    axis_mask_width_stop = 1920 - axis_mask_width_start
    axis_mask_height_stop = 1080 - axis_mask_height_start
    axis_mask = (axis_mask_width_start, axis_mask_height_start, axis_mask_width_stop, axis_mask_height_stop)

    text_height = 150

    # color_bar_height = 650
    rectangle_size = 80

    for idx, png_snaps1_path in enumerate(png_embryo_list1):
        # embryo_name, embryo_tp = os.path.basename(png_snaps1_path).split('_')[:2]
        # print(embryo_name,embryo_tp)
        png1 = Image.open(png_snaps1_path).crop(mask)
        png2 = Image.open(png_embryo_list2[idx]).crop(mask)
        png3 = Image.open(png_embryo_list3[idx]).crop(mask)
        png4 = Image.open(png_embryo_list4[idx]).crop(mask)
        png5 = Image.open(png_embryo_list5[idx]).crop(mask)
        png_axi = Image.open(png_axis_list[idx]).crop(axis_mask)

        # Create a new image with the same mode and size as the first image
        # text_height = 150
        # top_text_image=upper_right_png.crop((0,0,))
        combined_image = Image.new(png1.mode, (png1.width * 5, text_height + png1.height * 1 + +png_axi.height),
                                   color=(71, 71, 71))

        # Paste the images into the new image

        combined_image.paste(png1, (0, 0 + text_height))
        combined_image.paste(png2, (png1.width * 1, 0 + text_height))
        combined_image.paste(png3, (png1.width * 2, 0 + text_height))
        combined_image.paste(png4, (png1.width * 3, 0 + text_height))
        combined_image.paste(png5, (png1.width * 4, 0 + text_height))

        combined_image.paste(png_axi,
                             (combined_image.width // 2 - png_axi.width // 2, combined_image.height - png_axi.height))

        title_font_size = int(rectangle_size * 1.5)
        draw = ImageDraw.Draw(combined_image)
        font = ImageFont.truetype('arial.ttf', size=title_font_size)
        # width, height = combined_image.size
        width = png1.width * 5

        # text_whole = 'Tissue presentation'
        # textwidth, textheight = draw.textsize(text_whole, font)
        # x = (width - textwidth) // 2
        # y = textheight*0.1
        # draw.text((x, y), text_whole, fill="white", font=font)
        # #tissue_list = ['neuron', 'pharynx', 'skin', 'muscle', 'intestine']

        font = ImageFont.truetype('arial.ttf', size=int(title_font_size * 0.75))

        text1 = 'Neuron'
        textwidth, textheight = draw.textsize(text1, font)
        x = width // 5 * 0.5 - textwidth // 2
        y = textheight * 0.2
        draw.text((x, y), text1, fill="white", font=font)

        text2 = 'Pharynx'
        textwidth, textheight = draw.textsize(text1, font)
        x = width // 5 * 1.5 - textwidth // 2
        draw.text((x, y), text2, fill="white", font=font)

        text3 = 'Skin'
        textwidth, textheight = draw.textsize(text3, font)
        x = width // 5 * 2.5 - textwidth // 2
        draw.text((x, y), text3, fill="white", font=font)

        text4 = 'Muscle'
        textwidth, textheight = draw.textsize(text4, font)
        x = width // 5 * 3.5 - textwidth // 2
        draw.text((x, y), text4, fill="white", font=font)

        text5 = 'Intestine'
        textwidth, textheight = draw.textsize(text5, font)
        x = width // 5 * 4.5 - textwidth // 2
        draw.text((x, y), text5, fill="white", font=font)

        combined_image.save(os.path.join(dst_png_path, '{}.png'.format(str(idx).zfill(3))))


def generate_1plus2_view_png_one_embryo():
    # DELETEDCAPTURING=False
    embryo_name=r'Membrane'
    offset_tp=34
    # 34 for 190315xxx
    # 92 for membrane
    # offset_tp=7
    #FOR MP1

    # offset_tp=15 for mp3
    is_flipped=False
    png_sorce_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\movie ems dividing\png'
    annotated_nuc_path=r'F:\packed membrane nucleus 3d niigz'
    saving_path_root=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\movie ems dividing\video pngs'


    # view=3

    # png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, embryo_name, '*up_view.png'))
    # png_embryo_list2 = glob.glob(os.path.join(png_sorce_path, embryo_name, '*side_view.png'))
    # png_embryo_list3 = glob.glob(os.path.join(png_sorce_path, embryo_name, '*head_view.png'))

    png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, '*up_view.png'))
    png_embryo_list2 = glob.glob(os.path.join(png_sorce_path, '*side_view.png'))

    # png_sorce_path = r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\Figure7-movie\pngs2'
    # annotated_nuc_path = r'F:\packed membrane nucleus 3d niigz'
    #
    # png_embryo_list1 = glob.glob(os.path.join(png_sorce_path, '*up_view.png'))
    # png_embryo_list2 = glob.glob(os.path.join(png_sorce_path, '*side_view.png'))
    # # png_embryo_list3 = glob.glob(os.path.join(png_sorce_path, '*head_view.png'))


    width, height = 1920, 1080

    # for mp1's gastrulation
    mask_width_start = 400
    mask_height_start = 200
    mask_width_stop = 1400
    mask_height_stop = 900

    # # for mp1,mp3
    # mask_width_start = 600
    # mask_height_start = 300
    # mask_width_stop = 1250
    # mask_height_stop = 800


    # for mp3
    # mask_width_start = 300
    # mask_height_start = 0
    # mask_width_stop = 1600
    # mask_height_stop = 1100

    mask = (mask_width_start, mask_height_start, mask_width_stop, mask_height_stop)

    for idx, png_snaps1 in enumerate(png_embryo_list1):
        embryo_name, embryo_tp = os.path.basename(png_snaps1).split('_')[:2]

        embryo_name_tp = '_'.join([embryo_name, embryo_tp])

        annotated_cell_niigz=os.path.join(annotated_nuc_path,embryo_name,'AnnotatedNuc',embryo_name_tp+'_annotatedNuc.nii.gz')
        if os.path.exists(annotated_cell_niigz):
            annotated_niigz=nib_load(annotated_cell_niigz)
            cell_number=len(np.unique(annotated_niigz))-1
        else:

            cd_file_path=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\cdfiles\CD190315plc1mp1.csv'

            # cd_file_path=r'C:\Users\zelinli6\OneDrive - City University of Hong Kong - Student\Documents\02paper cunmin segmentation\cdfiles\DataS1_CellTracing.csv'
            cd_file_this=pd.read_csv(cd_file_path)
            cell_number=len(cd_file_this.loc[cd_file_this['time']==int(embryo_tp)])


        if is_flipped:
            png1 = Image.open(png_snaps1).transpose(Image.FLIP_LEFT_RIGHT).crop(mask)
            # png2 = Image.open(png_embryo_list2[idx]).crop(mask)

            png2 = Image.open(png_embryo_list2[idx]).transpose(Image.FLIP_LEFT_RIGHT).crop(mask)
            # png3 = Image.open(png_embryo_list3[idx]).transpose(Image.FLIP_LEFT_RIGHT).crop(mask)
        else:
            png1 = Image.open(png_snaps1).crop(mask)
            png2 = Image.open(png_embryo_list2[idx]).crop(mask)
            # png3 = Image.open(png_embryo_list3[idx]).crop(mask)

        # Create a new image with the same mode and size as the first image
        text_height = 200
        # top_text_image=upper_right_png.crop((0,0,))
        combined_image = Image.new(png1.mode, (png1.width * 2, text_height + png1.height * 1), color='black')

        # Paste the images into the new image
        combined_image.paste(png1, (0, text_height))
        combined_image.paste(png2, (png1.width, text_height))
        # combined_image.paste(png3, (png1.width * 2, text_height))

        time_this_tp = "{:.0f}".format((int(embryo_tp) -offset_tp) * 10)

        # Add text to the image
        draw = ImageDraw.Draw(combined_image)
        font = ImageFont.truetype('arial.ttf', size=60)
        text1 = 'Time: ' + time_this_tp + ' sec' + ' ; ' + 'Cell Number: ' + str(cell_number)
        textwidth, textheight = draw.textsize(text1, font)
        width, height = combined_image.size
        x = (width - textwidth) // 2
        y = textheight + 25
        draw.text((x, y), text1, fill="white", font=font)

        # # =============================temmmmmmmm=======for only one embryo dv axis===================
        # font = ImageFont.truetype('arial.ttf', size=60)
        #
        # if int(embryo_tp)<=37:
        #     x = (width - textwidth) // 4+50
        #     y = height//4*3-100
        #     draw.text((x, y), 'AB', fill="white", font=font)
        #
        #     x = (width - textwidth) // 2+225
        #     y = height // 4 * 3-50
        #     draw.text((x, y), 'P1', fill="white", font=font)
        # elif 37<int(embryo_tp)<=46:
        #
        #     x = (width - textwidth) // 4 + 25
        #     y = height // 4 * 3 - 75
        #     draw.text((x, y), 'ABa', fill="white", font=font)
        #
        #     x = (width - textwidth) // 4 + 210
        #     y = height // 4 * 3 - 180
        #     draw.text((x, y), 'ABa', fill="white", font=font)
        #
        #     x = (width - textwidth) // 4 + 300
        #     y = height // 4 * 3 - 15
        #     draw.text((x, y), 'P1', fill="white", font=font)
        # else:
        #
        #     x = (width - textwidth) // 4 + 5
        #     y = height // 4 * 3 - 75
        #     draw.text((x, y), 'ABa', fill="white", font=font)
        #
        #     x = (width - textwidth) // 4 + 200
        #     y = height // 4 * 3 - 180
        #     draw.text((x, y), 'ABa', fill="white", font=font)
        #
        #     x = (width - textwidth) // 4 + 210
        #     y = height // 4 * 3 + 15
        #     draw.text((x, y), 'EMS', fill="white", font=font)
        #
        #     x = (width - textwidth) // 4 + 400
        #     y = height // 4 * 3 - 75
        #     draw.text((x, y), 'P2', fill="white", font=font)


        # saving_path=os.path.join(png_sorce_path, 'combined_'+embryo_name, embryo_name_tp + '_combined.png')
        saving_path = os.path.join(
            saving_path_root,
            embryo_name_tp + '_combined.png')
        check_folder(saving_path)
        combined_image.save(saving_path)

if __name__ == '__main__':
    generate_1plus1_contact_curvature()

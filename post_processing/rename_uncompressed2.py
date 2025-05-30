import os
import glob

def rename_files(folder):
    # Get all .txt files in the folder
    for filepath in glob.glob(os.path.join(folder, "*.nii.gz")):
        filename = os.path.basename(filepath)
        # Expecting the format: prefix_number_suffix.txt
        parts = filename.split('.')[0].split('_')
        # if len(parts) < 3:
        #     print(f"Skipping '{filename}' (unexpected format)")
        #     continue

        try:
            # Assume the number is the second element (index 1)
            num = int(parts[1])
        except ValueError:
            print(f"Skipping '{filename}' (number conversion failed)")
            continue

        # Subtract 117 from the number
        new_num = num-117
        # Replace the number in the parts list
        parts[1] = str(new_num).zfill(3)
        # Reconstruct the new filename
        new_filename = '_'.join(parts)+'.nii.gz'
        new_filepath = os.path.join(folder, new_filename)
        print(f"Renaming '{filepath}' to '{new_filepath}'")
        os.rename(filepath, new_filepath)

if __name__ == "__main__":
    folder = r'H:\EmbSAM\revision\4data\raw_image_niigz\Uncompressed2'
    if os.path.isdir(folder):
        rename_files(folder)
    else:
        print("The specified path is not a valid directory.")

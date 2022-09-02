import os
import sys
import glob
import shutil
import timeit
import datetime

from threading import Lock
from concurrent.futures import ThreadPoolExecutor

import PIL
from PIL import Image


def main():
    inputs_dict = ask_inputs()

    inputs_dict['Images'] = [f for f in glob.glob(os.path.join(
        inputs_dict['Input folder'], '*.jpg'))]

    if len(inputs_dict["Images"]) > 0:
        print(f'* Images found: {len(inputs_dict["Images"])}')
    else:
        print('\nNo images found in the given folder. Exiting...')
        sys.exit()

    inputs_dict['Output folder'] = create_output_folder(
        inputs_dict['Input folder'])

    starttime = timeit.default_timer()

    global total_images, total_images_resized
    total_images = len(inputs_dict["Images"])
    total_images_resized = 0

    with ThreadPoolExecutor(os.cpu_count() + 4) as executor:
        futures = [executor.submit(resize_image, image, inputs_dict)
             for image in inputs_dict['Images']]

        for future in futures:
            future.add_done_callback(progress)

    failed_images = check_failures(inputs_dict)

    print(
        f'\n\nSuccessfully resized {total_images-len(failed_images)}/{total_images} images in {str(datetime.timedelta(seconds=timeit.default_timer() - starttime))}')
    
    if len(failed_images) == 1:
        print(f'Failed to resize the following ({len(failed_images)}) image: {", ".join(failed_images)}')
    elif len(failed_images) > 1:
        print(f'Failed to resize the following ({len(failed_images)}) images: {", ".join(failed_images)}')
    

def resize_image(image, inputs_dict):
    img = Image.open(image)

    # images will be rotated if this won't be used
    img = PIL.ImageOps.exif_transpose(img)

    wpercent = (inputs_dict['Image width'] / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))

    img = img.resize((inputs_dict['Image width'],
                     hsize), Image.Resampling.LANCZOS)

    output_img_fullpath = os.path.join(
        inputs_dict['Output folder'], os.path.basename(image))

    img.save(output_img_fullpath)


def ask_inputs():
    inputs_dict = {}
    # Ask for input folder
    while True:
        input_folder = input("\nPlease type input folder:\n")
        if os.path.exists(input_folder) and os.path.isdir(input_folder) and os.access(input_folder, os.W_OK):
            print()
            print("Input folder: {}".format(input_folder))
            break
        else:
            print('Invalid input folder path or without write permission')
            continue

    inputs_dict['Input folder'] = input_folder

    while True:
        try:
            img_width = int(input("\nType width:\n"))
            if img_width > 0:
                break
            else:
                print('Please type an integer > 0')
                continue
        except Exception:
            print('Please type an integer...')
            continue

    inputs_dict['Image width'] = img_width

    print()
    for key, value in inputs_dict.items():
        print(f'* {key}: {value}')

    return inputs_dict


def create_output_folder(input_folder):
    output_folder = os.path.join(input_folder, 'resized_images')

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

    try:
        os.makedirs(output_folder)
        print(f'\nOutput folder has been created: {output_folder}\n')
    except Exception:
        print('\n*** Unable to create output folder... no clue why... will try to continue.... :)')

    return output_folder


def check_failures(inputs_dict):
    output_images_lst = [os.path.basename(f) for f in glob.glob(os.path.join(inputs_dict['Output folder'], '*.jpg'))]
    input_images_lst = [os.path.basename(f) for f in inputs_dict['Images']]

    return list(set(input_images_lst) - set(output_images_lst))


def progress(self):
    suffix=""
    
    global lock
    lock = Lock()

    with lock:
        global total_images_resized
        total_images_resized += 1

        bar_len = 50
        filled_len = int(round(bar_len * total_images_resized / float(total_images)))

        percents = round(100.0 * total_images_resized / float(total_images), 1)
        bar = '#' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s complete%s\r' % (bar, percents, '%', suffix))
        sys.stdout.flush()


if __name__ == '__main__':
    main()

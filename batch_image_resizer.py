import os
import sys
import glob
import shutil
import timeit

from concurrent.futures import ThreadPoolExecutor

import PIL
from PIL import Image


def main():
    inputs_dict = ask_inputs()

    starttime = timeit.default_timer()

    inputs_dict['Images'] = [f for f in glob.glob(os.path.join(
        inputs_dict['Input folder'], '*.jpg'))]

    if len(inputs_dict["Images"]) > 0:
        print(f'* Images found: {len(inputs_dict["Images"])}')
    else:
        print('\nNo images found in the given folder. Exiting...')
        sys.exit()

    inputs_dict['Output folder'] = create_output_folder(
        inputs_dict['Input folder'])

    n_threads = len(inputs_dict['Images'])
    with ThreadPoolExecutor(n_threads) as executor:
        # _ = [executor.submit(resize_image, image, inputs_dict)
        #      for image in inputs_dict['Images']]

        failures = []
        counter = 0
        for i, image in enumerate(inputs_dict['Images']):
            try:
                executor.submit(resize_image, image, inputs_dict)
                counter += 1
            except Exception:
                failures.append(os.path.basename(image))

        progress(i+1, len(inputs_dict['Images']), suffix='')

    print(
        f'\n\nJob done in {round(timeit.default_timer() - starttime, 3)} seconds')
    print(
        f'Successfully resized images: {counter}/{len(inputs_dict["Images"])}')
    if len(failures) > 0:
        print(f'Failed to resize the following images: {", ".join(failures)}')


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
            break
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


def progress(count, total, suffix=''):
    bar_len = 50
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '#' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s complete%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()


if __name__ == '__main__':
    main()

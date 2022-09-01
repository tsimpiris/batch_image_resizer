import os
import glob


def main():
    ask_inputs()


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

    inputs_dict['input_folder'] = input_folder


if __name__ == '__main__':
    main()

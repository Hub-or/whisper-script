import os

import torch
import whisper
import shutil

from tqdm import tqdm
from pydub import AudioSegment


def save_to_txt(string_param, filename_param):
     with open(filename_param, 'w', encoding='utf-8') as file:
          file.write(string_param)


def expand_folder_get_item_list(root_folder_param, file_item_type_param=True,ignore_hidden_file_param=True):
    # Get all or specific layer item by file item type.
    # in:
    #     temp
    #         folder0
    #             folder1
    #             file1
    #         file0.txt
    # out:
    #     ['temp/file0.txt']
    ret_list = []
    hidden_list = []
    for root, dirs, files in os.walk(root_folder_param):
        if file_item_type_param is True:
            for file in files:
                if str(file).startswith('.'):
                    hidden_list.append(os.path.join(root, file))
                else:
                    ret_list.append(os.path.join(root, file))
        else:
            for dir in dirs:
                if str(dir).startswith('.'):
                    hidden_list.append(os.path.join(root, dir))
                else:
                    ret_list.append(os.path.join(root, dir))
        
    if ignore_hidden_file_param is False:
            ret_list.append(hidden_list)
    return ret_list


def second_to_duration(seconds_param):
    hours, remainder = divmod(seconds_param, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours}.{minutes}.{seconds}'


def slice_audio(file_param, temp_file_folder_param, duration_minute_param=1, export_format_param='mp3'):
    slice_time = 0
    sliced_millisecond = 0
    minute_multiplier = 1000 * 60
    every_slice_duration = duration_minute_param * minute_multiplier

    audio_data = AudioSegment.from_file(file_param)
    file_name = os.path.basename(file_param)
    file_name_without_extension = ''.join(str(file_name).split('.')[:-1])
    

    temp_file_list = []
    audio_duration = len(audio_data)
    while audio_duration > sliced_millisecond:
        sliced_audio_data = audio_data[sliced_millisecond:sliced_millisecond+every_slice_duration]
        temp_file = os.path.join(temp_file_folder_param, file_name_without_extension + f'({slice_time})') + f'.{export_format_param}'

        sliced_audio_data.export(temp_file, format=export_format_param)
        temp_file_list.append(temp_file)

        slice_time +=1
        sliced_millisecond = slice_time * minute_multiplier * duration_minute_param
    return temp_file_list


def transcribe(file_param, model_param, output_folder_param, temp_file_path_param, slice_duration_minute_param=1, language_param='en'):
    try:
        temp_file_folder = os.path.join(temp_file_path_param, r'TempFile')
        shutil.rmtree(temp_file_folder, True)
        os.makedirs(temp_file_folder, exist_ok=True)

        text_total = ''
        file_name = os.path.basename(file_param)
        temp_file_list = slice_audio(file_param, temp_file_folder, slice_duration_minute_param)
        print(os.getpid(), file_name)
        
        for ix, temp_file in tqdm(enumerate(temp_file_list), file_name, len(temp_file_list)):
            output = model_param.transcribe(temp_file, language=language_param)
            for sentence in output['segments']:
                start = int(sentence['start']) + ix * slice_duration_minute_param * 60
                end = int(sentence['end']) + ix * slice_duration_minute_param * 60
                text = sentence['text']
                text_total += f'{second_to_duration(start)} - {second_to_duration(end)}: {text}\n'
    except Exception:
        return file_param
    save_to_txt(text_total, os.path.join(output_folder_param, file_name[:-4] + f'_{language_param}' + '.txt'))


def lower_extention_name(file_name_param):
    file_extention = str(file_name_param).split('.')[-1].lower()
    extention_length = len(file_extention)
    file_name_param = file_name_param[:-extention_length] + file_extention
    return file_name_param


def format_file_extension(files_param):
    files = []
    for file in files_param:
        file_name = os.path.basename(file)
        parent_dir = os.path.dirname(file)
        new_file_name = lower_extention_name(file_name)
        new_file = os.path.join(parent_dir, new_file_name)
        os.rename(file, new_file)
        files.append(new_file)
    return files


if __name__ == "__main__":
    model_type = "medium"
    audio_file_type = "m4a"
    temp_file_folder = r"C:\Users\A\Desktop"
    source_folder = r'D:\Audios'
    text_output_folder = r'D:\AudioToText'

    exception_files = []
    files = expand_folder_get_item_list(source_folder)
    files = format_file_extension(files)
    files = sorted([file for file in files if file.endswith(f".{audio_file_type}")])
    if files:  #(exist)
        model = whisper.load_model(model_type)
    else:
        print("No files loaded.")
        exit()

    if torch.cuda.is_available():
        print('进程id', os.getpid())
        device = torch.device("cuda")
        model = model.to(device)
        print("Using GPU:", torch.cuda.get_device_name(0))
        for file in files:
            exception_files.append(transcribe(file, model, text_output_folder, temp_file_path))
    else:
        print("CUDA is not available. Using CPU instead.")
        for file in files:
            exception_files.append(transcribe(file, model, text_output_folder, temp_file_path))
        
    print(exception_files)

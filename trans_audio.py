import os

import torch
import whisper
import shutil

from tqdm import tqdm
from pydub import AudioSegment


def format_audio_files(audio_folder_param: os.PathLike, audio_file_types_param: list[str]) -> tuple:
    files = expand_folder_get_item_list(audio_folder_param)
    files = format_file_extension(files)
    files_ = []
    for file in files:
        for audio_file_type in audio_file_types_param:
            if file.endswith(f".{audio_file_type}"):
                files_.append(audio_file_type)
    files_ = sorted([file for file in files if file.endswith(f".{audio_file_type}")])
    if files:  # (exists)
        return files_
    else:
        print("No files loaded.")
        exit()


def expand_folder_get_item_list(root_folder_param: os.PathLike, item_type_is_file_param: bool=True, ignore_hidden_file_param: bool=True) -> os.PathLike:
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
        if item_type_is_file_param is True:
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


def format_file_extension(files_param: list[os.PathLike]) -> list[os.PathLike]:
    files = []
    for file in files_param:
        file_name = os.path.basename(file)
        parent_dir = os.path.dirname(file)
        new_file_name = lower_extention_name(file_name)
        new_file = os.path.join(parent_dir, new_file_name)
        os.rename(file, new_file)
        files.append(new_file)
    return files


def lower_extention_name(file_name_param: str) -> str:
    file_extention = str(file_name_param).split('.')[-1].lower()
    extention_length = len(file_extention)
    file_name_param = file_name_param[:-extention_length] + file_extention
    return file_name_param


def transcribe(model_param: whisper.Whisper, files_param: list[os.PathLike], text_output_folder_param: os.PathLike, temp_file_folder_param: os.PathLike, slice_duration_param: int, output_language_param: str) -> None:
    transcribe_status = []
    if torch.cuda.is_available():
        print('Process id:', os.getpid())
        device = torch.device("cuda")
        model = model_param.to(device)
        print("Using GPU device:", torch.cuda.get_device_name(0))
        for file in files_param:
            transcribe_status.append(_transcribe(file, model, text_output_folder_param, temp_file_folder_param, slice_duration_param, output_language_param))
    else:
        print("CUDA is not available. Using CPU instead.")
        for file in files:
            transcribe_status.append(_transcribe(file, model, text_output_folder_param, temp_file_folder_param, slice_duration_param, output_language_param))
    
    exception_files = []
    for file in transcribe_status.copy():
        if file is not None:
            exception_files.append(file)
    if len(exception_files) > 0:
        print(exception_files)


def _transcribe(file_param: os.PathLike, model_param: whisper.Whisper, output_folder_param: os.PathLike, temp_file_folder_param: os.PathLike, slice_duration_minute_param: int=1, language_param: str='en') -> os.PathLike:
    try:
        shutil.rmtree(temp_file_folder_param, True)
        os.makedirs(temp_file_folder_param, exist_ok=True)

        text_total = ''
        file_name = os.path.basename(file_param)
        temp_file_list = slice_audio(file_param, temp_file_folder_param, slice_duration_minute_param)
        
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


def slice_audio(file_param: os.PathLike, temp_file_folder_param: os.PathLike, duration_minute_param: int=1, export_format_param: str='mp3') -> list[os.PathLike]:
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


def second_to_duration(seconds_param: int) -> str:
    hours, remainder = divmod(seconds_param, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours}.{minutes}.{seconds}'


def save_to_txt(string_param: str, file_param: os.PathLike) -> None:
    with open(file_param, 'w', encoding='utf-8') as file:
        file.write(string_param)


if __name__ == "__main__":
    model_type = "medium"
    audio_file_types = ["m4a"]
    temp_file_folder = r".\temporary_file"
    audio_folder = r".\audio"
    text_output_folder = r".\text"
    slice_duration = 1
    output_language = "zh"

    model = whisper.load_model(model_type)
    files = format_audio_files(audio_folder, audio_file_types)
    transcribe(model, files, text_output_folder, temp_file_folder, slice_duration, output_language)

import os
import ffmpeg


def format_date(date_param):
    if len(str(date_param).split('-')) > 1:
        if len(str(date_param).split('-')[1]) < 2:
            date_param = date_param[:5] + '0' + date_param[5:]
        return ' '.join([split_date for split_date in date_param.split(' ') if split_date != ''])
    return date_param


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


def expand_folder_get_item_list(root_folder_param, file_item_type_param=True, ignore_hidden_file_param=True):
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


def extract_audio(video_path, audio_output_path):
    video_name = os.path.basename(video_path)    
    _audio_output_path = os.path.join(audio_output_path, video_name[:-4] + '.aac')
    (
         ffmpeg
         .input(video_path)
         .output(_audio_output_path, acodec='copy')
         .run()
    )


def deduplicate_path(path_list_param):
    # 创建一个字典来存储文件名和路径
    unique_files = {}
    for path in path_list_param:
        # 获取文件名
        filename = os.path.basename(path)
        # 如果文件名还未在字典中，添加路径
        if filename not in unique_files:
            unique_files[filename] = path
    # 获取去重后的路径列表
    return list(unique_files.values())


if __name__ == "__main__":
    def format_file_name(files_param):
        files = []
        for file in files_param:
            file_name = os.path.basename(file)
            parent_dir = os.path.dirname(file)
            new_file_name = format_date(file_name)
            new_file = os.path.join(parent_dir, new_file_name)
            os.rename(file, new_file)
            files.append(new_file)
        return files
    
    def select_video_files(files_param, extension_name_list_param=['mov', 'mp4']):
        files = []
        for file in files_param:
            for extension_name in extension_name_list_param:
                if file.endswith(f'.{extension_name}'):
                    files.append(file)
        return files
    

    file_types = ['mov', 'mp4']
    # 指定源文件夹和目标文件夹路径
    source_folder = r"H:\增添\tempVideo"
    audio_folder = r'H:\增添\tempAudio'
    # 遍历源文件夹中的所有文件和子文件夹
    exception_files = []
    files = expand_folder_get_item_list(source_folder)
    files = format_file_extension(files)
    files = format_file_name(files)
    files = select_video_files(files, file_types)
    # 按文件名去重
    files = deduplicate_path(files)

    for file in files:
        try:
            extract_audio(file, audio_folder)
        except Exception:
            exception_files.append(file)

    print(exception_files)


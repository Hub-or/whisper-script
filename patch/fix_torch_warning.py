"""
D:\Software\Anaconda\envs\python3.9\lib\site-packages\whisper\__init__.py:150:
FutureWarning: You are using `torch.load` with `weights_only=False` (the current default value), 
which uses the default pickle module implicitly. 
It is possible to construct malicious pickle data which will execute arbitrary code during unpickling 
(See https://github.com/pytorch/pytorch/blob/main/SECURITY.md#untrusted-models for more details). 
In a future release, the default value for `weights_only` will be flipped to `True`. 
This limits the functions that could be executed during unpickling. 
Arbitrary objects will no longer be allowed to be loaded via this mode unless they are explicitly allowlisted by the user via `torch.serialization.add_safe_globals`. 
We recommend you start setting `weights_only=True` for any use case where you don't have full control of the loaded file. 
Please open an issue on GitHub for any issues related to this experimental feature.
  checkpoint = torch.load(fp, map_location=device)
"""

import os
import sys

python_location = sys.executable
python_environment_location = os.path.dirname(python_location)
warning_code_file = python_environment_location+r'\lib\site-packages\whisper\__init__.py'
file_content = None
with open(warning_code_file, 'r', encoding='utf-8') as file:
    file_content = file.read()
    file_content_split_by_newline = file_content.split('\n')
    if file_content_split_by_newline[149] != "        checkpoint = torch.load(fp, map_location=device)":
        exit()
    file_content_split_by_newline[149] = "        checkpoint = torch.load(fp, map_location=device, weights_only=True)"
    file_content = '\n'.join(file_content_split_by_newline)
with open(warning_code_file, 'w', encoding='utf-8') as file:
    file.write(file_content)

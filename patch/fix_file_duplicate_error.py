"""
OMP: Error #15: Initializing libiomp5md.dll, but found libiomp5md.dll already initialized.
OMP: Hint This means that multiple copies of the OpenMP runtime have been linked into the program. 
That is dangerous, since it can degrade performance or cause incorrect results. 
The best thing to do is to ensure that only a single OpenMP runtime is linked into the process, 
e.g. by avoiding static linking of the OpenMP runtime in any library. 
As an unsafe, unsupported, undocumented workaround you can set the environment variable KMP_DUPLICATE_LIB_OK=TRUE to allow the program to continue to execute, 
but that may cause crashes or silently produce incorrect results. 
For more information, please see http://www.intel.com/software/products/support/.
"""

import os
import sys
import shutil

# 记录“文件重复”问题范围
python_location = sys.executable
python_environment_location = os.path.dirname(python_location)
duplicate_file_location = [
    [python_environment_location+r'\Library\bin\libiompstubs5md.dll', 
    python_environment_location+r'\Lib\site-packages\torch\lib\libiompstubs5md.dll',],
    [python_environment_location+r'\Library\bin\libiomp5md.dll', 
    python_environment_location+r'\Lib\site-packages\torch\lib\libiomp5md.dll',]]

# 检查问题的存在，标记问题
problem_pair_index_list = []
for pair_inx, duplicate_pair in enumerate(duplicate_file_location):
    bug_exist = os.path.exists(duplicate_pair[0]) and os.path.exists(duplicate_pair[1])
    if bug_exist:
        problem_pair_index_list.append(pair_inx)

# 修正问题：移除原生库中文件
patch_bug = False
file_storage_folder = os.path.dirname(os.path.abspath(__file__))
if len(problem_pair_index_list) > 0:
    patch_bug = True
    for bug_pair in problem_pair_index_list:
        shutil.move(duplicate_file_location[bug_pair][0], file_storage_folder)

# 验证修正操作的执行
if patch_bug:
    print("Bug patched.")

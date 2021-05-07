import os 
import subprocess
import json
import shutil
from typing import Union, Optional, List, Dict, Callable, Any, Tuple
from types import ModuleType

import tqdm

class Vars: 
    default_config_path = os.path.join(".","tmp_many_pynb_config.json")
    default_output_dir = os.path.join(".","many_pynb_output")

    def __init__(self):
        pass

def setup(target_path: str, 
          config_paths : List[str], 
          output_dir : str = None, 
          output_file_names : Optional[List[str]] = None,
          ) -> Vars:
    """Set up config paths:
    """
    obj = Vars()
    obj.target_path = target_path
    obj.target_file = os.path.basename(target_path)
    obj.target_ext = os.path.splitext(target_path)[1]
    if obj.target_ext != ".ipynb":
        raise Exception("Set a file with .ipynb extension")

    obj.config_paths = config_paths

    if output_dir is None:
        output_dir = obj.default_output_dir
    obj.output_dir = output_dir

    if output_file_names is None:
        output_file_names = [obj.target_file[:-6]  + f"_{i}.html" for i in range(len(obj.config_paths)) ]
    else:
        if len(obj.config_paths) != len(output_file_names):
            raise Exception("Length of config_paths and output_file_names are not matched.")
    obj.output_file_names = output_file_names
    obj.output_file_paths = [ os.path.join(obj.output_dir, name) for name in obj.output_file_names]

    print_out_settings(obj)
    return(obj)

def run(obj : Vars, 
        exclude_code_block : bool = False, 
        leave_tmp_config : bool = True
        ) -> None:
    if "config_paths" not in dir(obj):
        raise Exception("Pass object returned by many_pynb.setup")

    if not os.path.exists(obj.target_path):
        raise Exception(f"{obj.target_path} does not exist.")

    if not os.path.exists(obj.output_dir):
        os.mkdir(obj.output_dir)

    n = len(obj.config_paths)
    for i in tqdm.tqdm(range(n)): 
        config = obj.config_paths[i]
        output = obj.output_file_paths[i]
        shutil.copyfile(config, Vars.default_config_path)

        execute_jupyter_notebook(obj.target_file)
        output_jupyter_notebook(obj.target_file, obj.output_dir, exclude_input = exclude_code_block )
        tmp = os.path.join(obj.output_dir, obj.target_file[:-6] + ".html")
        os.rename( tmp, output)

    if not leave_tmp_config:
        os.remove(Vars.default_config_path)

def read_config() -> dict:
    """Read config. This should be set in output notebook.
    """
    with open(Vars.default_config_path, "r") as f:
        config = json.load(f)
    return(config)

def print_out_settings(obj : Vars) -> None:
    """Print out settings.
    """
    print("# many_pynb settings")
    print(f"- target file : {obj.target_file}")
    print(f"- config files :")
    for conf in obj.config_paths:
        print("    " + conf)
    print(f"- output files:")
    for path in obj.output_file_paths:
        print("    " + path )

def execute_jupyter_notebook(file_ : str) -> None:
    """Execute one jupyter notebook and replace it.
    """
    cmd = ["papermill", file_, file_]
    subprocess.check_call(cmd)

def output_jupyter_notebook(file_: str,
                           output_dir: Optional[str] = None,
                           exclude_input: bool = True) -> None:
    """Output jupyternotebook.

    Args:
        file_ : file name.
        output_dir : Output directory.
            If not specified, the output dir is the current
            working directory.
        exclude_input: If True, the code blocks are excluded.
    """
    cmd = ["jupyter","nbconvert",file_, "--to", "html"]
    if exclude_input:
        cmd.append("--TemplateExporter.exclude_input=True")
    if output_dir:
        cmd.append(f"--output-dir={output_dir}")

    subprocess.check_call(cmd)


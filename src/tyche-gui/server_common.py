from types import SimpleNamespace
from pathlib import Path
import os

this_script_path   = os.path.realpath(__file__)
this_script_dir    = os.path.abspath(os.path.dirname(this_script_path))
tech_database_path = os.path.abspath(os.path.join(this_script_dir, "technologies.json"))

parent_dir       = os.path.abspath(os.path.join(this_script_dir, os.pardir))
technology_path  = Path(os.path.abspath(os.path.join(parent_dir, "technology")))

def to_object(d):
    """
    Convert a dictionary to a python object
    """
    if isinstance(d, dict):
        ns = SimpleNamespace()
        for k,v in d.items():
            setattr(ns, k, to_object(v))
        return ns
    elif isinstance(d, list):
        return [to_object(v) for v in d]
    else:
        return d

def to_dict(obj):
    """
    Convert a python object to a dict
    """
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    elif isinstance(obj, dict):
        return {key: to_dict(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [to_dict(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return {key: to_dict(value) for key, value in vars(obj).items()}
    else:
        raise ValueError(f"Unsupported type: {type(obj)}")
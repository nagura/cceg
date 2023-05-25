import os

import opt.config as cfg

def rule_json():
    fname = _load_config('rule_json')
    return "opt/rule.json" if fname is None else fname

def c_compiler():
    compiler = _load_config('c_compiler')
    return "gcc" if compiler is None else compiler

def debug_mode():
    return True if _load_config('debug_mode') == "True" else False

def display_err():
    return True if _load_config('display_err') == "True" else False

def _load_config(name):
    _chk_config(name)
    return None if not hasattr(cfg, name) or getattr(cfg, name) is None else getattr(cfg, name)

def _chk_config(name):
    if not hasattr(cfg, name) or getattr(cfg, name) is None:
        cfg.load_config()

def escape_str(str):
    """
    Returns string for regexp with escaped charactors.

    Returns:
        str
    """
    # must set the character \ as first element
    charactors = ['\\', '(', ')', '[', ']', '{', '}', '?', '|', '*', '+', '$', '^', '.']

    for c in charactors:
        str = str.replace(c, '\\' + c)
    return str

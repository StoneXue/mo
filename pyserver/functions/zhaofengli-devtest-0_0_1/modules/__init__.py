import os
import sys
import json
from importlib import import_module


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout


def module_general(module_id, action, *args, **kwargs):
    [user_ID, module_name, version] = module_id.split('/')
    version = '_'.join(version.split('.'))
    main_module = import_module(
        f'modules.{user_ID}.{module_name}.{version}.src.main')
    cls = getattr(main_module, module_name)()
    return getattr(cls, action)(*args, **kwargs)


def json_parser(json_obj):
    return json.loads(json_obj)
    # return {arg.get('name'): arg.get('value')
    #                          or arg.get('values')
    #                          or arg.get('default')
    #         for arg in args}


class Client:

    def __init__(self, api_key, silent=False):
        self.silent = silent

    def run(self, module_id, *args, **kwargs):
        if self.silent:
            with HiddenPrints():
                return module_general(module_id, 'run', *args, **kwargs)
        return module_general(module_id, 'run', *args, **kwargs)

    def train(self, module_id, *args, **kwargs):
        if self.silent:
            with HiddenPrints():
                return module_general(module_id, 'train', *args, **kwargs)
        return module_general(module_id, 'train', *args, **kwargs)

    def predict(self, module_id, *args, **kwargs):
        if self.silent:
            with HiddenPrints():
                return module_general(module_id, 'predict', *args, **kwargs)
        return module_general(module_id, 'predict', *args, **kwargs)

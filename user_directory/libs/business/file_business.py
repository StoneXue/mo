# -*- coding: UTF-8 -*-
import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append('../../')

from datetime import datetime
from ..entity.file import File
from ..repository.file_repo import FileRepo

file_repo = FileRepo(File)


def add(file_name, file_size, url, uri, description):
    file_obj = File(name=file_name, size=file_size, url=url, uri=uri,
                    upload_time=datetime.utcnow(), description=description)
    return file_repo.create(file_obj)


def get_by_user(user_obj):
    return file_repo.read_by_unique_field('user', user_obj)


def get_by_id(file_id):
    return file_repo.read_by_id(file_id)


def remove_by_id(file_id):
    return file_repo.delete_by_id(file_id)



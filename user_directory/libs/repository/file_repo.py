# -*- coding: UTF-8 -*-
from datetime import datetime

from ..repository.general_repo import Repo


class FileRepo(Repo):
    def __init__(self, instance):
        Repo.__init__(self, instance)


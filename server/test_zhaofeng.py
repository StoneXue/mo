# # -*- coding: UTF-8 -*-
from bson import ObjectId
from service import data_service

data_service.import_data_from_file_object_id(ObjectId(
    "59250e97df86b2fe3b8991b4"), 'dsdsds', 'ds_descriptionds_description',
    'test_user', True)
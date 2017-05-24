# -*- coding: UTF-8 -*-

from mongoengine import connect
from entity.project import Project
from business import project_business
from repository import config
from entity.data import Data
from entity.data_set import DataSet
from service import staging_data_service
from utility import json_utility



connect(
    db=config.get_mongo_db(),
    username=config.get_mongo_user(),
    password=config.get_mongo_pass(),
    host=config.get_mongo_host(),
)

# project_service.create_project("testasdfasdf", "adsfafd",
#    'test_user', True)

#print project_service.get_projects_by_user_ID('test_user')
#(sds_name, sds_description, project_id,data_objs):

# data = json_utility.convert_to_json(data)
staging_data_service.run()
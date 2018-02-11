from mongoengine import CASCADE
from mongoengine import NULLIFY

from server3.entity.staging_data_set import StagingDataSet
from server3.entity.toolkit import Toolkit
from server3.entity.model import Model
from server3.entity.data_set import DataSet
from server3.entity.served_model import ServedModel
from server3.entity.job import Job
from server3.entity.result import Result
from server3.entity.project import Project
from server3.entity.file import File
from server3.entity.user import User
from server3.entity.data import Data
from server3.entity.ownership import Ownership
from server3.entity.user_request import UserRequest
from server3.entity.user_request_comments import UserRequestComments
from server3.entity.request_answer import RequestAnswer

# ——————————————————————————————————————————————————————— external delete rules
#                                            Defined here to avoid import loops
Project.register_delete_rule(Job, 'project', CASCADE)
DataSet.register_delete_rule(File, 'data_set', CASCADE)
File.register_delete_rule(DataSet, 'file', NULLIFY)

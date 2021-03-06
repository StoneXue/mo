# -*- coding: UTF-8 -*-
import os
import sys
import subprocess
import shutil
from copy import deepcopy

from bson import Code
import numpy as np
import pandas as pd
from mongoengine import DoesNotExist
from sklearn.model_selection import train_test_split

from server3.business import staging_data_set_business
from server3.business import staging_data_business
from server3.business import data_business
from server3.business import data_set_business
from server3.business import project_business
from server3.business import ownership_business
from server3.service import data_service
from server3.utility import data_utility
from server3.utility import json_utility
from server3.constants import USER_DIR

DEFAULT_RATIO = 0.5


def get_by_query_str(staging_data_set_id, **kwargs):
    # query_str = dict(query_str_in_mongodb_form)
    # query_str['staging_data_set'] = staging_data_set_id
    kwargs['staging_data_set'] = staging_data_set_id
    return staging_data_business.get_by_query_str(**kwargs)


def get_first_one_by_staging_data_set_id(staging_data_set_id):
    return staging_data_business.get_first_one_by_staging_data_set_id(
        staging_data_set_id)


def list_staging_data_sets_by_project_id(project_id, without_result=False):
    """
    Get the list of staging_data_set by project id

    :param project_id:
    :param without_result:
    :return: list of staging_data_set objects
    """
    sds_objects = staging_data_set_business.get_by_project_id(
        project_id, without_result)
    return sds_objects


def add_staging_data_set_by_data_set_id(sds_name, sds_description, project_id,
                                        data_set_id):
    """
    Create staging_data_set and copy to staging_data by original data_set id

    :param sds_name: str
    :param sds_description: str
    :param project_id: ObjectId
    :param data_set_id: ObjectId
    :return: new staging_data_set object
    """
    # get project object
    # project = project_business.get_by_id(project_id)

    # create new staging data set
    ds_obj = data_set_business.get_by_id(data_set_id)
    ds = ds_obj.to_mongo()
    ds.pop('name')
    ds.pop('description')
    sds = staging_data_set_business.add(sds_name, sds_description, project_id,
                                        **ds)

    # update project info
    # note: related_field in data set become related_fields here
    project_business.update_items_to_list_field(
        project_id, tags=ds.get('tags', []),
        related_tasks=ds.get('related_tasks', []),
        related_fields=ds.get('related_field', []))

    # generate the project volume path
    project = project_business.get_by_id(project_id)
    user_ID = ownership_business.get_owner(project, 'project').user_ID
    volume_dir = os.path.join(USER_DIR, user_ID, project.name, 'volume/')
    if not os.path.exists(volume_dir):
        os.makedirs(volume_dir)

    # copy data from data(raw) to staging data
    # get all data objects by data_set id
    try:
        # copy the file instance to project volume
        if hasattr(ds_obj, 'file') and ds_obj.file:
            file = ds_obj.file
            if os.path.isdir(file.uri):
                dst = os.path.join(volume_dir, os.path.dirname(file.uri))
                # if dir exists, remove it and copytree, cause copytree will
                #  create the dir
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(file.uri, dst)
            else:
                shutil.copy(file.uri, volume_dir)

        data_objects = data_business.get_by_data_set(data_set_id)
        # convert mongoengine objects to dicts
        data_objects = json_utility.me_obj_list_to_dict_list(data_objects)

        # remove data set id when import to sds
        for d in data_objects:
            d.pop('data_set')

        if data_objects:
            staging_data_business.add_many(sds, data_objects)
        return sds
    except Exception as e:
        # remove staging_data_set and staging_data
        staging_data_business.remove_by_staging_data_set_id(sds.id)
        staging_data_set_business.remove_by_id(sds.id)
        raise e


def update_staging_data_set_by_data_set_id(sds_id, sds_name, sds_desc, sds_tags,
                                           sds_field):

    sds_tags = [x.strip() for x in sds_tags.split(',')]
    result = staging_data_set_business.update(
        sds_id, name=sds_name, description=sds_desc, tags=sds_tags,
        related_field=sds_field
    )
    return result



def convert_fields_type(sds_id, f_t_arrays):
    """
    convert field types of staging data set
    :param sds_id: ObjectId
    :param f_t_arrays: array: [['name', 'str'],['age', 'int'], ['salary',
    'float']]
    :return: new staging_data_set object
    """
    # get project object
    # project = project_business.get_by_id(project_id)

    # create new staging data set
    sds = staging_data_set_business.get_by_id(sds_id)
    # copy data from data(raw) to staging data
    # get all data objects by data_set id

    data_objects = staging_data_business. \
        get_by_staging_data_set_id(sds['id'])
    # convert mongoengine objects to dicts
    data_objects = json_utility.me_obj_list_to_dict_list(data_objects)
    # convert types of values in dicts
    result = data_utility.convert_data_array_by_fields(data_objects,
                                                       f_t_arrays)
    data_objects = result['result']

    # update all rows
    for data_obj in data_objects:
        staging_data_business.update_by_id(data_obj['_id'], data_obj)

    if 'failure_count' in result:
        failure_count = result['failure_count']
        return {'result': sds, 'failure_count': failure_count}
    return {'result': sds}


def get_fields_with_types(staging_data_set_id):
    """
    Get the fields and its types of one staging_data_set by map/reduce function.
    :param staging_data_set_id:
    :return: [field_name, [type1, type2, ...]]
    """
    mapper, reducer = data_service.field_mapper_reducer()
    result = staging_data_business. \
        get_fields_by_map_reduce(staging_data_set_id, mapper, reducer)
    return [[mr_doc.key, list(mr_doc.value.keys())] for mr_doc in result]


def _get_fields_with_types(staging_data_set_id):
    """
    Get the fields and its types of one staging_data_set

    :param staging_data_set_id:
    :return: the list of field name and value type
    """
    # sds_object = staging_data_set_business.get_by_id(staging_data_set_id)
    # sd_object = staging_data_business.get_first_one_by_staging_data_set(
    #              sds_object)
    sd_object = staging_data_business.get_first_one_by_staging_data_set_id(
        staging_data_set_id)

    if sd_object:
        transformed_sb_object = sd_object.to_mongo().to_dict()
        return [[k, type(v).__name__] for k, v
                in transformed_sb_object.items()]
    else:
        raise RuntimeError("No matched data")


def check_integrity(staging_data_set_id):
    """
    check_integrity
    :param staging_data_set_id:
    :return:
    """
    data_objects = staging_data_business. \
        get_by_staging_data_set_id(staging_data_set_id)
    # convert mongoengine objects to dicts
    data_objects = json_utility.me_obj_list_to_json_list(data_objects)
    data_fields = get_fields_with_types(staging_data_set_id)
    return data_service.check_data_integrity(data_objects, data_fields)


def update_data(update):
    """
    update data row by row
    :param update:
    :return:
    """
    for oid in update.keys():
        query = {}
        for q in update[oid]:
            query.update(q)
        staging_data_business.update_by_id(oid, query)


# 新增加一个栏位用来加字段，字段的value在array里面
def add_new_key_value(sds_id, key, array):
    """
        update data row by row
        :param update:
        :return:
    """
    # get staging data的所有id
    ids = staging_data_business.get_by_staging_data_set_id(sds_id)
    for oid in ids:
        query = {key: array.copy().pop(0)}
        staging_data_business.update_by_id(oid.id, query)


# 新增多个栏位用来加字段，字段的value和key在dict里面
def add_new_keys_value(sds_id, lst_dicts):
    """
        update data row by row
        :param update
        :return:
    """
    # get staging data的所有id
    ids = staging_data_business.get_by_staging_data_set_id(sds_id)
    for oid in ids:
        staging_data_business.update_by_id(oid.id, lst_dicts.pop(0))


def update_many_with_new_fields(raw_data, index, fields, name, sds_id):
    ids = staging_data_business.get_by_staging_data_set_id(sds_id)
    ids = list(ids)
    inn = 0
    while inn in index:
        inn += 1

    list_dicts = []
    # 判断是否为一维数组
    if not isinstance(raw_data[inn], list):
        str_name = fields[0] + name if len(fields) == 1 else name
        for i in range(len(ids)):
            list_dicts.append({'_id': ids[i].id, str_name: raw_data[i]})
    else:
        length1 = len(raw_data[inn])
        length2 = len(fields)
        # 判断是不是一对多还是多对多
        if length1 == length2:
            name_list = [item + '_' + name for item in fields]
        elif length2 == 1:
            name_list = [fields[0] + '_' + name + str(i) for i in
                         range(length1)]
        else:
            name_list = [name + str(i) for i in range(length1)]

        # for i in range(len(raw_data)):
        for i in range(len(raw_data)):
            arr = raw_data[i]
            if arr != arr:
                rows = [arr] * length1
                obj = dict(zip(name_list, rows))
            else:
                obj = dict(zip(name_list, arr))
            obj.update({'_id': ids[i].id})
            list_dicts.append(obj)

    print("list_dicts", list_dicts)
    # 把list_dicts存到数据库
    staging_data_business.update_many_with_new_fields(list_dicts)


def get_row_col_info(sds_id):
    """
    get_row_col_info
    :param sds_id:
    :return:
    """
    sds = staging_data_business.get_by_staging_data_set_id(sds_id)
    row_n = len(sds)
    col_n = len(get_fields_with_types(sds_id))
    return {'row': row_n, 'col': col_n}


def remove_staging_data_set_by_id(sds_id):
    """
    remove_staging_data_set_by_id
    :param sds_id:
    :return:
    """
    staging_data_business.remove_by_staging_data_set_id(sds_id)
    return staging_data_set_business.remove_by_id(sds_id)


def mongo_to_array(cursor, fields):
    """
    mongo data to ndarray
    :param cursor:
    :param fields:
    :return:
    """
    arrays = convert_array(cursor, fields)
    arrays = np.array(arrays)
    return arrays


def convert_array(data, columns):
    data_array = []
    for item in data:
        temp = [data_utility.convert_string_to_number_with_poss(item[i])
                for i in columns
                if item[i] != '_id' and item[i] != 'staging_data_set']
        data_array.append(temp)
    return data_array


def mongo_to_df(cursor):
    """
    mongo data to data frame
    :param cursor:
    :return:
    """
    cursor = json_utility.me_obj_list_to_dict_list(cursor)
    return pd.DataFrame.from_records(cursor)


def split_x_y(sds_id, x_fields, y_fields):
    """
    split data to x and y

    :param sds_id:
    :param x_fields:
    :param y_fields:
    :return:
    """
    data = staging_data_business.get_by_staging_data_set_and_fields(sds_id,
                                           x_fields + y_fields,
                                           allow_nan=False)
    x = mongo_to_array(data, x_fields)
    y = mongo_to_array(data, y_fields)
    return {'x': x, 'y': y}


def split_test_train(x_y_obj, schema='cv', **kwargs):
    """
    split data to test and train
    :param x_y_obj:
    :param schema:
    :return:
    """
    x = x_y_obj.pop('x', np.array([]))
    y = x_y_obj.pop('y', np.array([]))
    ratio = kwargs.get('ratio')
    divide_row = kwargs.get('divide_row')
    if schema == 'cv':
        ratio = ratio or DEFAULT_RATIO
        x_tr, x_te, y_tr, y_te = \
            data_utility.k_fold_cross_validation(x, y, float(ratio))
        return {'x_tr': x_tr, 'y_tr': y_tr, 'x_te': x_te, 'y_te': y_te}
    if schema == 'seq':
        length = x.shape[0]
        if not divide_row and ratio:
            ratio = float(ratio)
            divide_row = length * ratio
        else:
            divide_row = divide_row or length * DEFAULT_RATIO
        divide_row = int(divide_row)
        if isinstance(x, pd.DataFrame):
            return {'x_tr': x.iloc[:divide_row, :],
                    'y_tr': y.iloc[:divide_row, :],
                    'x_te': x.iloc[divide_row:, :],
                    'y_te': y.iloc[divide_row:, :]}
        return {'x_tr': x[:divide_row, :], 'y_tr': y[:divide_row, :],
                'x_te': x[divide_row:, :], 'y_te': y[divide_row:, :]}
    if schema == 'rand':
        ratio = ratio or DEFAULT_RATIO
        if (isinstance(y, pd.DataFrame) and y.empty) or \
                (isinstance(y, np.ndarray) and y.size == 0):
                X_train, X_test = train_test_split(
                    x,
                    test_size=1 - ratio,
                    random_state=42)
                y_train = []
                y_test = []
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                x, y,
                test_size=1 - ratio,
                random_state=42)
        if isinstance(x, pd.DataFrame):
            return {'x_tr': pd.DataFrame(X_train),
                    'y_tr': pd.DataFrame(y_train),
                    'x_te': pd.DataFrame(X_test),
                    'y_te': pd.DataFrame(y_test)}
        else:
            return {'x_tr': X_train,
                    'y_tr': y_train,
                    'x_te': X_test,
                    'y_te': y_test}


def copy_staging_data_set(sds, belonged_project, **kwargs):
    """
    copy_staging_data_set
    :param sds:
    :param belonged_project:
    :return:
    """
    try:
        staging_data_set_business.get_by_name_and_project(
            sds.name, belonged_project)
    except DoesNotExist:
        belonged_job = None
        if 'belonged_job' in kwargs:
            belonged_job = kwargs.pop('belonged_job')
        if kwargs:
            raise TypeError('Unrecognized keyword arguments: ' + str(kwargs))
        sds_cp = staging_data_set_business.copy_staging_data_set(
            sds, belonged_project, belonged_job)
        staging_data_business.copy_staging_data_by_staging_data_set_id(sds_cp)
        return sds_cp


def update_staging_data_set_by_job_id(job_id):
    sds_obj = staging_data_set_business.get_by_job_id(job_id)
    sds_obj.type = 'save'
    return sds_obj.save()



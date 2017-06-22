# -*- coding: UTF-8 -*-
"""
Blueprint for project

Author: Zhaofeng Li
Date: 2017.05.25
"""
from bson import ObjectId
from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import request

from business import staging_data_business
from service import staging_data_service
from service import toolkit_service
from utility import json_utility

PREFIX = '/staging_data'

staging_data_app = Blueprint("staging_data_app", __name__, url_prefix=PREFIX)


@staging_data_app.route('/get_by_staging_data_set_and_fields', methods=['POST'])
def get_by_staging_data_set_and_fields():
    data = request.get_json()
    fields = data.get('fields')
    staging_data_set_id = data.get('staging_data_set_id')
    toolkit_id = data.get('toolkit_id')
    project_id = data.get('project_id')
    # 初始值为0
    k = data.get('k')
    if k is not None:
        k = int(k)

    try:
        data = staging_data_business.get_by_staging_data_set_and_fields(
            ObjectId(staging_data_set_id), fields)
        data = [d.to_mongo().to_dict() for d in data]
        result = toolkit_service.convert_json_and_calculate(project_id,
                                                            staging_data_set_id,
                                                            toolkit_id, fields, data,
                                                            k)
    except Exception as e:
        return make_response(jsonify({'response': '%s: %s' % (str(
            Exception), e.args)}), 400)
    return make_response(jsonify({'response':
                         json_utility.convert_to_json(result)}),
                         200)


@staging_data_app.route('/get_fields_with_types', methods=['GET'])
def get_fields_with_types():
    staging_data_set_id = request.args.get('staging_data_set_id')
    try:
        data = staging_data_service.get_fields_with_types(
            ObjectId(staging_data_set_id))
    except Exception as e:
        return make_response(jsonify({'response': '%s: %s' % (str(
            Exception), e.args)}), 400)
    return make_response(jsonify({'response': data}),
                         200)


@staging_data_app.route('/list_staging_data_sets_by_project_id', methods=['GET'])
def list_staging_data_sets_by_project_id():
    project_id = request.args.get('project_id')
    try:
        data = staging_data_service.list_staging_data_sets_by_project_id(
            ObjectId(project_id))
        data = [d.to_mongo() for d in data]
        data = json_utility.convert_to_json(data)
    except Exception as e:
        return make_response(jsonify({'response': '%s: %s' % (str(
            Exception), e.args)}), 400)
    return make_response(jsonify({'response': data}),
                         200)


@staging_data_app.route('/add_staging_data_set_by_data_set_id', methods=[
    'POST'])
def add_staging_data_set_by_data_set_id():
    # sds_name, sds_description, project_id, data_set_id
    data = request.get_json()

    project_id = data['project_id']
    staging_data_set_name = data['staging_data_set_name']
    staging_data_set_description = data['staging_data_set_description']
    data_set_id = data['data_set_id']
    f_t_arrays = data['f_t_arrays']

    try:
        result = staging_data_service.add_staging_data_set_by_data_set_id(
            staging_data_set_name, staging_data_set_description,
            ObjectId(project_id), ObjectId(data_set_id), f_t_arrays)
        saved_sds = result['result']
        sds_json = json_utility.convert_to_json(saved_sds.to_mongo())
    except Exception as e:
        return make_response(jsonify({'response': '%s: %s' % (str(
            Exception), e.args)}), 400)
    if 'failure_count' in result:
        failure_count = result['failure_count']
        return make_response(jsonify({'response': sds_json,
                                      'failure_count': failure_count}), 200)
    return make_response(jsonify({'response': sds_json}), 200)
# -*- coding: UTF-8 -*-
import requests
import json

from server3.service.project_service import ProjectService
from server3.business.module_business import ModuleBusiness
from server3.business.app_business import AppBusiness
from server3.business.user_business import UserBusiness
from server3.business.statistics_business import StatisticsBusiness


class AppService(ProjectService):
    business = AppBusiness

    @classmethod
    def add_used_module(cls, app_id, used_modules, func):
        used_modules = [ModuleBusiness.get_by_id(mid) for mid in used_modules]
        for module in used_modules:
            module.args, module.output = ModuleBusiness.load_module_params(
                module)
        return AppBusiness.add_used_module(app_id, used_modules, func)

    @classmethod
    def run_app(cls, app_id, input_json, user_ID):
        app = AppBusiness.get_by_id(project_id=app_id)
        url = app.user.user_ID+"-"+app.name
        domin = "http://192.168.31.23:8080/function/"
        url = domin+url
        payload = json.dumps(input_json)
        headers = {
            'content-type': "application/json",
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        output_json = response.json()
        # 成功调用后 在新的collection存一笔
        user_obj = UserBusiness.get_by_user_ID(user_ID=user_ID)
        StatisticsBusiness.use_app(
            user_obj=user_obj, app_obj=app,
            input_json=input_json, output_json=output_json)
        return output_json

    # @classmethod
    # def add_used_app(cls, user_ID, app_id):
    #     user = UserBusiness.get_by_user_ID(user_ID=user_ID)
    #     app = cls.business.get_by_id(app_id)
    #     user.used_apis.append(app)
    #     user_result = user.save()
    #     if user_result:
    #         return {
    #             "user": user_result.to_mongo(),
    #         }

# def test_create_app():
#     data = {
#         "name": "预测航班延误",
#         "description": "预测航班延误信息",
#     }
#     AppService.create_project(name="预测航班延误", description="description")

if __name__ == '__main__':
    pass

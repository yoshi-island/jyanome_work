#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 楽天のホテル情報を取ってくる

import requests
import json
import time


def get_hotels(app_id, code_list):
    query_base = \
    "https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20131024?format=json&applicationId={app_id}".format(app_id=app_id)

    if code_list[0] == "":
      return "error"

    q_largeclasscode = "largeClassCode=%s" % code_list[0]
    q_middleclasscode = "middleClassCode=%s" % code_list[1]
    query_base = "%s&%s&%s" % (query_base, q_largeclasscode, q_middleclasscode)

    result=list()
    q_smallclasscode = "smallClassCode=%s" % code_list[2]
    query_str = "%s&%s" % (query_base, q_smallclasscode)

    # detail class codeがあれば追記してクエリを投げる
    _dict = None
    if len(code_list) > 3:
        q_detailclasscode = "detailClassCode=%s" % code_list[3]
        query_detail = "%s&%s" % (query_str, q_detailclasscode)
        res = requests.get(query_detail)
        _dict = json.loads(res.content.decode('utf-8'))
    else:
        # print(query_str)
        res = requests.get(query_str)
        _dict = json.loads(res.content.decode('utf-8'))


    hotels_list = _dict['hotels']
    for hotelinfodic in hotels_list:
        _ave_1 = 0
        _ave_2 = 0
        _divide_num = 2
        if not 'serviceAverage' in hotelinfodic['hotel'][1]['hotelRatingInfo'] \
                or not 'locationAverage' in hotelinfodic['hotel'][1]['hotelRatingInfo']:
            _divide_num = 1
        if 'serviceAverage' in hotelinfodic['hotel'][1]['hotelRatingInfo']:
            _ave_1 = hotelinfodic['hotel'][1]['hotelRatingInfo']['serviceAverage']
            if not _ave_1:
                _ave_1 = 0
        if 'locationAverage' in hotelinfodic['hotel'][1]['hotelRatingInfo']:
            _ave_2 = hotelinfodic['hotel'][1]['hotelRatingInfo']['locationAverage']
            if not _ave_2:
                _ave_2 = 0
        _average = float(_ave_1 + _ave_2) / _divide_num

        if _average >= 3.5:
            if _divide_num == 1:
                print("this hotel has only one item for reputation.")
            # print(hotelinfodic['hotel'][0]['hotelBasicInfo']['hotelName'])
            # print(str(hotelinfodic['hotel'][0]['hotelBasicInfo']['hotelInformationUrl']))
            # print("average=%f" % _average)
            # print(str(hotelinfodic['hotel'][1]['hotelRatingInfo']))
            result.append(hotelinfodic)
    time.sleep(1)
    return result

#!/usr/env python
# -*- coding:utf-8 -*-
# 出力整形するファイル

import requests
import json
import get_tweets_search
import rakuten_search_hotels
import sys
import password_list

app_id = password_list.app_id

# mecabでとった値の整形
tweets_info = get_tweets_search.get_tweets()
user = tweets_info[0] #tweet user
n = tweets_info[1] #tweetの多い地名何番目まで取り出しているか
place_list = tweets_info[2] #地名リストとtweet数

def greeting():
    print("「%s」のtweetしたトップ「%d位」の地名は以下" % (user, n))
    if len(place_list) == 0:
        print("そんなユーザーいないね、、、")
        exit()

    c = 1
    for l in place_list:
        print("%i: %s" % (c, place_list[c-1][0]))
        c = c + 1

    print("どれにする？[1/2/3/4/5]")
    keyword = int(sys.stdin.readline())-1
    word = place_list[keyword][0]
    print("キーワードは「%s」" % word)
    print("+++++++++++++++++++++++++++++++++++++++")
    return word


# 楽天トラベルで提供している地域のリストを取得する
def get_area_code_list():
    res = requests.get(
        'https://app.rakuten.co.jp/services/api/Travel/GetAreaClass/20131024?format=json&applicationId={app_id}'.format(app_id=app_id))
    if res.status_code == 200:
        res_str = res.content.decode('utf-8')
        dict = json.loads(res_str)

        large_classes = dict['areaClasses']['largeClasses'][0]['largeClass']
        large_class = large_classes[0]
        large_class_name = large_class['largeClassName']
        large_class_code = large_class['largeClassCode']
        # print('%s / %s' % (large_class_code, large_class_name))

        middle_classes = large_classes[1]['middleClasses']

        result = list()
        for middle_class in middle_classes:
            m = middle_class['middleClass']
            middle_class_elem = m[0]
            small_classes = m[1]['smallClasses']

            middle_class_code = middle_class_elem['middleClassCode']
            middle_class_name = middle_class_elem['middleClassName']

            # print('%s / %s' % (middle_class_code, middle_class_name))

            item_list = list() #空のリストを作る
            item_list.append(large_class_code)
            item_list.append((middle_class_name, middle_class_code))
            small_list = []
            for small_class in small_classes:
                small_class_elems = small_class['smallClass']
                small_class_elem = small_class_elems[0]

                small_class_name = small_class_elem['smallClassName']
                small_class_code = small_class_elem['smallClassCode']

                # print('  %s / %s' % (small_class_name, small_class_code))

                small_items = list()
                small_items.append((small_class_name, small_class_code))
                if len(small_class_elems) > 1:
                    detail_classes = small_class_elems[1]['detailClasses']

                    detail_items = list()
                    for detail_class in detail_classes:
                        detail_class_elem = detail_class['detailClass']
                        detail_class_name = detail_class_elem['detailClassName']
                        detail_class_code = detail_class_elem['detailClassCode']

                        # print('    %s / %s' % (detail_class_name, detail_class_code))

                        small_items.append((detail_class_name, detail_class_code))
                small_list.append(small_items)
            item_list.append(small_list)
            result.append(item_list)

    else:
        print('リクエストの送信に失敗しました')

    area_code_list = result
    return area_code_list


# wordが属するエリアリストをarea_code_listから取り出す
def get_area_list(word, area_code_list):
    result = list()
    #word = word.decode('utf-8')
    # ひとつひとつの要素はtupleになっており、1番目が名前、2番目がコード
    for area_code_item in area_code_list:
        large_class_code = area_code_item[0]
        middle_class_code = area_code_item[1]
        small_and_detail_class_code_list = area_code_item[2]

        def create_item(_small_class_code, detail_class_code=None):
            if detail_class_code is not None:
                return large_class_code, middle_class_code[1], _small_class_code[1], detail_class_code[1]
            else:
                return large_class_code, middle_class_code[1], _small_class_code[1]

        if word in middle_class_code[0]:
            for small_and_detail_class_code in small_and_detail_class_code_list:
                small_class_code = small_and_detail_class_code[0]
                if len(small_and_detail_class_code) > 1:
                    result += map(lambda x: create_item(small_class_code, x), small_and_detail_class_code[1:])
                    #for detail_class_code in small_class_code[1:]:
                    #    result.append(create_item(small_class_code, detail_class_code))
                else:
                    result.append(create_item(small_class_code))
        else:
            for small_and_detail_class_code in small_and_detail_class_code_list:
                small_class_code = small_and_detail_class_code[0]
                if len(small_and_detail_class_code) > 1:
                    if word in small_class_code[0]:
                        result += map(lambda x: create_item(small_class_code, x), small_and_detail_class_code[1:])
                        #for detail_class_code in small_class_code[1:]:
                        #    result.append(create_item(small_class_code, detail_class_code))
                    else:
                        items = map(lambda x: (create_item(small_class_code, x) if word in x[0] else None), small_and_detail_class_code[1:])
                        result += filter(lambda x: x is not None, items)
                        #for detail_class_code in small_class_code[1:]:
                        #    if word in detail_class_code[0]:
                        #        result.append(create_item(small_class_code, detail_class_code))
                else:
                    if word in small_class_code[0]:
                        result.append(create_item(small_class_code))


    #print(result) # [('japan', 'hokkaido', 'sapporo', 'A'), ('japan', 'hokkaido', 'sapporo', 'B'), ('japan', 'hokkaido', 'sapporo', 'C')]

    area_list = result
    return area_list



def list_up(area_list):
        print("「%s」にある「%s」にオススメの4.5以上のホテルたち↓" % (word, user))
        print("+++++++++++++++++++++++++++++++++++++++")
        print("=====================")

        # [('japan', 'kumamoto', 'kumamoto'), ('japan', 'kumamoto', 'kikuchi'), ('japan', 'kumamoto', 'aso'), ('japan', 'kumamoto', 'yatsushiro'), ('japan', 'kumamoto', 'kuma'), ('japan', 'kumamoto', 'amakusa'), ('japan', 'kumamoto', 'kurokawa')]みたいになっているが、リストになっていないので、リスト化する。
        area_list = area_list[2:-2]
        area_list = area_list.replace("'", "")
        area_list = area_list.replace(" ", "")
        area_list = area_list.split("),(")
        area_list_tmp = []
        for l in area_list:
          area_list_tmp.append(tuple(l.split(",")))
        area_list = []
        area_list = area_list_tmp

        # 複数ヒットした場合は、一旦一つ目を検索するようにする。
        # [('japan', 'kanagawa', 'shonan')]を普通のリスト['japan', 'kanagawa', 'shonan']に整形
        area_list_tmp = []
        area_list_tmp = list(area_list[0])
        area_list = []
        area_list = area_list_tmp

        hotel_list = []
#        for location in area_list:
        hotels = rakuten_search_hotels.get_hotels(app_id, area_list)
        if hotels == "error":
          print("この地名では検索不可、、、")
          exit()

        for hotel in hotels:
            hotel_ave = hotel['hotel'][0]['hotelBasicInfo']['reviewAverage']
            if hotel_ave > 4.5:
                hotel_name = hotel['hotel'][0]['hotelBasicInfo']['hotelName']
                hotel_address = hotel['hotel'][0]['hotelBasicInfo']['address2']
                hotel_info = hotel['hotel'][0]['hotelBasicInfo']['hotelInformationUrl']

                print(hotel_name)
                print(hotel_address)
                print(hotel_info)
                print(hotel_ave)
                print("=====================")

                hotel_list.append(hotel_name)

        if len(hotel_list) == 0:
            print("該当するホテルなし、、、")
            print("=====================")



#def men_women_list_up():
    # これから書く


### Execute
if __name__ == "__main__":

    # 最初の処理、検索対象の地域名取得
    word = greeting()

    # 全国のarea_code_listを出す
    area_code_list = get_area_code_list()

    # 特定の地域のエリアリストを出す
    area_list = get_area_list(word, area_code_list)

    # 最後の処理
    list_up(str(area_list))

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# tweetをMeCabで解析する

from requests_oauthlib import OAuth1Session
import json
import MeCab
import collections
import password_list
import sys

oath_key_dict = password_list.oath_key_dict

def get_tweets():
    print("解析したいtwitterアカウントを入れてね[@hogehoge]")
    user = sys.stdin.readline().rstrip()

    n = 5 #多い順にいくつ地名を取るか
    tweet_list = tweet_search(user, oath_key_dict)
    text = ""
    for dic in tweet_list:
        text += dic['text'] + "\n"

    mecab = MeCab.Tagger("-Ochasen")
    #text = text.encode('utf-8')
    #print(text)
    mecab_parsed = mecab.parse(text)

    lines = mecab_parsed.split("\n")
    #print(lines)

    l = []
    for line in lines:
        items = line.split("\t")
        if len(items)>4:
            if items[3].find("地域") > -1:
                #print(items[0]+" "+items[3] )
                #print(items[0])
                l.append(items[0])

    count_dict = collections.Counter(l)
    place_list = count_dict.most_common(n)

    return user, n, place_list

def create_oath_session(oath_key_dict):
    oath = OAuth1Session(
    oath_key_dict["consumer_key"],
    oath_key_dict["consumer_secret"],
    oath_key_dict["access_token"],
    oath_key_dict["access_token_secret"]
    )
    return oath

def tweet_search(user, oath_key_dict):
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json?"
    params = {
        "screen_name": user,
        "count": "100"
        }
    oath = create_oath_session(oath_key_dict)
    responce = oath.get(url, params = params)
    if responce.status_code != 200:
        print("Error code: %d" %(responce.status_code))
        return None
    tweets = json.loads(responce.text)
    return tweets

## Execute
#if __name__ == "__main__":
##    main()
#    create_oath_session(oath_key_dict)
#    tweet_search(user, oath_key_dict)
#    get_tweets(user)

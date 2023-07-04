import os
import re
import sys
import json
import tweepy
import requests


def twitter_authentication():
    # auth = tweepy.OAuth1UserHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
    # auth.set_access_token(os.environ['ACCESS_TOKEN'], os.environ['ACCESS_TOKEN_SECRET'])
    # return tweepy.API(auth)
    # return tweepy.Client(
    #     consumer_key=os.environ["CONSUMER_KEY"],
    #     consumer_secret=os.environ["CONSUMER_SECRET"],
    #     access_token=os.environ["ACCESS_TOKEN"],
    #     access_token_secret=os.environ["ACCESS_TOKEN_SECRET"],
    # )

    auth = tweepy.OAuth2BearerHandler(os.environ['BEARER_TOKEN'])
    return tweepy.API(auth)


def tweet(api, data):
    for d in data:
        categories = " ".join(
            ["#" + category.replace("-", "") for category in d["categories"]]
        )
        api.create_tweet("{}.\n{}\n{}".format(d["title"], categories, d["link"]))


def compare_data(oldData, newData):
    twitter_data = []
    last_pub_date = oldData[-1]["pubDate"]
    for nD in newData:
        if nD["pubDate"] > last_pub_date:
            twitter_data.insert(
                0,
                {
                    "title": nD["title"],
                    "link": nD["link"],
                    "pubDate": nD["pubDate"],
                    "categories": nD["categories"],
                },
            )
        else:
            break
    return twitter_data


def read_json_file(filename):
    jsonFile = open(filename, "r")
    data = json.load(jsonFile)
    jsonFile.close()
    return data


def modify_json_file(filename, data):
    if len(data) != 0:
        jsonFile = open(filename, "w+")
        jsonFile.write(json.dumps(data, indent=4))
        jsonFile.close()


def fetch_blog_posts(link):
    result = []
    response = requests.get(link)
    if response.status_code == 200:
        posts = json.loads(response.text)["items"]
        for post in posts:
            # skip the comments
            if len(post["categories"]) != 0:
                result.append(post)
    elif response.status_code == 404:
        print("Not Found: ") + link
    return result


if __name__ == "__main__":
    filename = "blog_links.json"
    username = "@lifeparticle"
    blog_link = (
        "https://api.rss2json.com/v1/api.json?rss_url=https://medium.com/feed/"
        + username
    )

    newData = fetch_blog_posts(blog_link)
    oldData = read_json_file(filename)
    twitter_data = compare_data(oldData, newData)
    api = twitter_authentication()
    tweet(api, twitter_data)
    modify_json_file(filename, twitter_data)

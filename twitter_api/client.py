from twitter_api.exception import TooManyRequests, TwitterServerError, HTTPException
from twitter_dumper.app.config import TwitterConfig
from datetime import datetime, timezone, timedelta
from requests_oauthlib import OAuth1
import twitter_api.const as const
import requests
import time
import re
import oauth2 as oauth
from twitter_dumper.app import utils


class BaseClient:
    _base_url_v1: str = "https://api.twitter.com/1.1"
    _base_url_v2: str = "https://api.twitter.com/2"

    def __init__(self, config: TwitterConfig):
        self.config = config
        # 2377312943
        consumer = oauth.Consumer(key=config.customer_key, secret=config.customer_secret)
        access_token = oauth.Token(key=config.access_token, secret=config.token_secret)
        self.client = oauth.Client(consumer, access_token)

    def _bearer_oauth(self, request):
        request.headers["Authorization"] = f"Bearer {self.config.bearer_token}"
        return request

    def _oauth_1(self):
        return OAuth1(self.config.customer_key, self.config.customer_secret,
                      self.config.access_token, self.config.token_secret)

    @staticmethod
    def is_rate_limit(response):
        regex = "^x-rate-limit-[a-z]+"
        return bool([v for k, v in response.headers.items() if re.match(regex, k)])

    def _connect_to_endpoint(self, method, url, params=None, json=None, stream=False):
        response = requests.request(
            method=method, url=url, auth=self._bearer_oauth,
            params=params, json=json, stream=stream)
        if not str(response.status_code).startswith("2"):
            # Too many requests error
            if response.status_code == 429:
                time_to_wait = 1
                if self.is_rate_limit(response):
                    rate_limit_reset = datetime.fromtimestamp(int(response.headers["x-rate-limit-reset"]))
                    time_to_wait = (rate_limit_reset - datetime.now()).total_seconds()
                    print("To many request. \t Time to wait : {:0.2f} s \t Rate limit reset : {}"
                          .format(time_to_wait, rate_limit_reset))
                time.sleep(time_to_wait)
                raise TooManyRequests(response)
            # Twitter internal server error
            elif str(response.status_code).startswith("5"):
                print("Internal server error. Time to wait : {:0.2f}".format(2))
                time.sleep(2)
                raise TwitterServerError(response)
            else:
                raise HTTPException("Request returned an error: {} {}"
                                    .format(response.status_code, response.text))
        return response


class Client(BaseClient):

    def get_subscribed_users(self, screen_name: str):
        users_stored: list = []
        search_url: str = f"{self._base_url_v1}/followers/ids.json"
        query_params: dict = {"screen_name": screen_name, "count": 5000}
        cursor = None
        try:
            while True:
                if cursor:
                    query_params['cursor'] = cursor
                start = time.time()
                try:
                    json_response = self._connect_to_endpoint("GET", search_url, query_params).json()
                except (TooManyRequests, TwitterServerError):
                    continue
                cursor = json_response["next_cursor"]
                if cursor == 0:
                    break
                users_ids = json_response["ids"]
                current_users_stored = self.get_users_by_ids(users_ids)
                users_stored.extend(current_users_stored)
                duration = time.time() - start
                print("... users stored : {} \t duration : {:0.2f} s".format(len(users_stored), duration))
                # if duration < 60:
                #     time_to_sleep = 60 - duration
                #     print("... sleep for {:0.2f} s".format(time_to_sleep))
                #     time.sleep(60 - duration)
            return users_stored
        except Exception as ex:
            print(ex)

    def get_users_by_ids(self, users_ids: list):
        users_stored: list = []
        search_url: str = f"{self._base_url_v2}/users"
        query_params: dict = {"user.fields": ",".join(const.user_fields)}
        try:
            ids_split_in_100 = [users_ids[i:i + 100] for i in range(0, len(users_ids), 100)]
            for ids in ids_split_in_100:
                query_params['ids'] = ",".join(str(elt) for elt in ids)
                json_response = self._connect_to_endpoint("GET", search_url, query_params).json()
                if "data" not in json_response:
                    continue
                users_stored.extend(
                    list(dict(("_id", v) if k == "id" else (k, v) for k, v in _.items())
                         for _ in json_response['data']))
            return users_stored
        except Exception as ex:
            print(ex)

    def get_all_tweets(self, query, tweets_number, start_time, end_time=None) -> tuple:
        next_token = None
        if not end_time:
            end_time = datetime.now(timezone.utc).replace(tzinfo=None)
        tweets_stored = []
        includes_tweets = []
        includes_users = []
        includes_places = []
        includes_medias = []
        search_url = f"{self._base_url_v2}/tweets/search/all"
        try:
            while start_time < end_time and len(tweets_stored) < tweets_number:
                query_params = {
                    'query': query,
                    'start_time': (start_time + timedelta(seconds=1)).strftime(const.iso_time_format),
                    'end_time': (end_time - timedelta(seconds=15)).strftime(const.iso_time_format),
                    'tweet.fields': ",".join(const.tweet_fields),
                    'user.fields': ",".join(const.user_fields),
                    'place.fields': ",".join(const.place_fields),
                    'media.fields': ",".join(const.media_fields),
                    'expansions': ",".join(const.expansions),
                    'max_results': 500
                }
                if next_token:
                    query_params['pagination_token'] = next_token

                try:
                    json_response = self._connect_to_endpoint("GET", search_url, query_params).json()
                except (TooManyRequests, TwitterServerError):
                    continue
                if json_response['meta']['result_count'] == 0:
                    print("... no data")
                    break
                # tweets
                tweets_stored.extend(utils.change_list_dict_key("id", "_id", json_response["data"]))
                # includes tweets
                if "tweets" in json_response["includes"]:
                    includes_tweets.extend(utils.change_list_dict_key("id", "_id", json_response["includes"]["tweets"]))
                # includes users
                if "users" in json_response["includes"]:
                    includes_users.extend(utils.change_list_dict_key("id", "_id", json_response["includes"]["users"]))
                # includes media
                if "media" in json_response["includes"]:
                    includes_medias.extend(
                        utils.change_list_dict_key("media_key", "_id", json_response["includes"]["media"]))
                # includes places
                if "places" in json_response["includes"]:
                    includes_places.extend(utils.change_list_dict_key("id", "_id", json_response["includes"]["places"]))
                iso_time = tweets_stored[len(tweets_stored) - 1]["created_at"]
                end_time = datetime.strptime(iso_time, const.iso_time_format)
                print("... date : {} \t tweets : {} \t includes users : {} \t includes tweets : {} \t includes media : {} \t includes places : {}"
                      .format(iso_time, len(tweets_stored), len(includes_users), len(includes_tweets), len(includes_medias), len(includes_places)))
                try:
                    next_token = json_response["meta"]["next_token"]
                except KeyError:
                    break
                time.sleep(1)
            # remove duplicates values
            tweets_stored = {i['_id']: i for i in reversed(tweets_stored)}.values()
            includes_tweets = {i['_id']: i for i in reversed(includes_tweets)}.values()
            includes_users = {i['_id']: i for i in reversed(includes_users)}.values()
            includes_medias = {i['_id']: i for i in reversed(includes_medias)}.values()
            includes_places = {i['_id']: i for i in reversed(includes_places)}.values()
            return tweets_stored, includes_tweets, includes_users, includes_medias, includes_places
        except Exception as ex:
            print(ex)

    def get_user(self, username):
        try:
            search_url = f"{self._base_url_v2}/users/by/username/{username}"
            query_params = {'user.fields': ",".join(const.user_fields)}
            json_response = self._connect_to_endpoint("GET", search_url, query_params).json()
            return json_response["data"]
        except Exception as ex:
            print(ex)

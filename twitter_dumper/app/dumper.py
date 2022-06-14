import pymongo
import twitter_api
from dataclasses import dataclass
from twitter_dumper.app.config import Config
from twitter_dumper.app.mongodb_cluster import MongoDbCluster


@dataclass
class Dumper:
    _mongodb_cluster: MongoDbCluster
    _config: Config
    _twitter_client: twitter_api.Client
    _twitter_streaming_client: twitter_api.StreamingClient

    def __init__(self, config: Config):
        self._twitter_client = twitter_api.Client(config.twitter)
        self._twitter_streaming_client = twitter_api.StreamingClient(config.twitter)
        self._config = config
        self._mongodb_cluster = MongoDbCluster(config.mongo_db)

    def start(self):
        try:
            # print("[ dump user followers ]")
            # self._dump_users_followers()
            # print("[ dump user tweets ]")
            # self._dump_user_tweets()
            print("[ dump search tweets ]")
            self._dump_search_tweets()
        except Exception as ex:
            print(ex)

    def _user_tweets_query(self):
        username = self._config.dumper.username
        return f"from:{username} -is:retweet"

    def _search_tweets_query(self):
        username = self._config.dumper.username
        return f"@{username} -from:{username} -is:retweet"

    def _dump_users_followers(self):
        username = self._config.dumper.username
        subscribed_users = self._twitter_client.get_subscribed_users(username)
        self._mongodb_cluster.save_subscribed_users(subscribed_users)

    def _dump_user_tweets(self):
        # start_time = self._mongodb_cluster.get_tweet_created_at("user_tweets", pymongo.DESCENDING)
        start_time = self._config.dumper.user_tweets.start_time
        user_tweets, includes_tweets, includes_users, includes_medias, includes_places = \
            self._twitter_client.get_all_tweets(self._user_tweets_query(), 7000, start_time)
        self._mongodb_cluster.save_user_tweets(user_tweets)
        self._mongodb_cluster.save_includes_users(includes_users)
        self._mongodb_cluster.save_includes_tweets(includes_tweets)
        self._mongodb_cluster.save_includes_medias(includes_medias)
        self._mongodb_cluster.save_includes_places(includes_places)

    def _dump_search_tweets(self):
        end_time = self._mongodb_cluster.get_tweet_created_at("search_tweets", pymongo.ASCENDING)
        start_time = self._config.dumper.search_tweets.start_time
        search_tweets, includes_tweets, includes_users, includes_medias, includes_places = \
            self._twitter_client.get_all_tweets(self._search_tweets_query(), 5000, start_time, end_time)
        self._mongodb_cluster.save_search_tweets(search_tweets)
        self._mongodb_cluster.save_includes_users(includes_users)
        self._mongodb_cluster.save_includes_tweets(includes_tweets)
        self._mongodb_cluster.save_includes_medias(includes_medias)
        self._mongodb_cluster.save_includes_places(includes_places)

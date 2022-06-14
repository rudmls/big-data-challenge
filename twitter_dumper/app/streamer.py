import json

from pykafka import KafkaClient

from twitter_dumper.app import Dumper


class Streamer(Dumper):

    @staticmethod
    def get_kafka_client():
        return KafkaClient(hosts='127.0.0.1:9092')

    def start(self):
        rules = [{"value": self._search_tweets_query(), "tag": self._config.dumper.username}]
        stored_rules = self._twitter_streaming_client.get_rules()
        delete = self._twitter_streaming_client.delete_all_rules(stored_rules)
        print(delete)
        create = self._twitter_streaming_client.set_rules(rules)
        print(create)
        response = self._twitter_streaming_client.get_stream()
        for response_line in response.iter_lines():
            if response_line:
                json_response = json.loads(response_line)
                json_response_str = json.dumps(json_response["data"]["text"], indent=4, ensure_ascii=False)
                print(json_response_str)
                # kafka
                client = self.get_kafka_client()
                topic = client.topics[b'search_tweets']
                producer = topic.get_sync_producer()
                producer.produce(str.encode(json_response_str))
                # # tweets
                # tweets = dict(("_id", v) if k == "id" else (k, v) for k, v in json_response["data"].items())
                # self._mongodb_cluster.save_search_tweets(list(tweets))
                # if "tweets" in json_response["includes"]:
                #     includes_tweets = utils.change_list_dict_key("id", "_id", json_response["includes"]["tweets"])
                #     self._mongodb_cluster.save_includes_tweets(includes_tweets)
                # # includes users
                # if "users" in json_response["includes"]:
                #     includes_users = utils.change_list_dict_key("id", "_id", json_response["includes"]["users"])
                #     self._mongodb_cluster.save_includes_users(includes_users)
                # # includes media
                # if "media" in json_response["includes"]:
                #     includes_medias = utils.change_list_dict_key("media_key", "_id", json_response["includes"]["media"])
                #     self._mongodb_cluster.save_includes_medias(includes_medias)
                # # includes places
                # if "places" in json_response["includes"]:
                #     includes_places = utils.change_list_dict_key("id", "_id", json_response["includes"]["places"])
                #     self._mongodb_cluster.save_includes_places(includes_places)
                # self._mongo_client[Database.stream_data][Collection.stream_search_tweets].insert_one(json_response)
                # print(json.dumps(json_response, indent=4, ensure_ascii=False))
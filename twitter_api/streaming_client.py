from twitter_api import const
from twitter_api.client import BaseClient


class StreamingClient(BaseClient):

    def get_rules(self):
        search_url = f"{self._base_url_v2}/tweets/search/stream/rules"
        json_response = self._connect_to_endpoint("GET", search_url).json()
        if "data" in json_response:
            return json_response["data"]

    def delete_all_rules(self, rules):
        if rules is None:
            return None
        search_url = f"{self._base_url_v2}/tweets/search/stream/rules"
        ids = list(map(lambda rule: rule["id"], rules))
        payload = {"delete": {"ids": ids}}
        json_response = self._connect_to_endpoint(method="POST", url=search_url, json=payload).json()
        return json_response["meta"]

    def set_rules(self, rules):
        search_url = f"{self._base_url_v2}/tweets/search/stream/rules"
        payload = {"add": rules}
        json_response = self._connect_to_endpoint(method="POST", url=search_url, json=payload).json()
        return json_response["data"]

    def get_stream(self):
        search_url = f"{self._base_url_v2}/tweets/search/stream"
        query_params = {
            "place.fields": ",".join(const.place_fields),
            "poll.fields": ",".join(const.poll_fields),
            'tweet.fields': ",".join(const.tweet_fields),
            'user.fields': ",".join(const.user_fields),
            "expansions": ",".join(const.expansions)}
        response = self._connect_to_endpoint(method="GET", url=search_url, params=query_params, stream=True)
        return response

import json
import requests

BATCH_SIZE = 1000

class TwitterStream:
    def __init__(self, s3_client, bucket, twitter_bearer_token, prefix):
        self.bucket = bucket
        self.s3_client = s3_client
        self.twitter_bearer_token = twitter_bearer_token
        self.prefix = prefix

    def run(self):
        rules = self._get_rules()
        delete = self._delete_all_rules(rules)
        rules = self._set_rules(delete)
        self._get_stream(rules)

    def _twitter_bearer_token(self, r):
        r.headers["Authorization"] = f"Bearer {self.twitter_bearer_token}"
        r.headers["User-Agent"] = "v2FilteredStreamPython"
        return r

    def _get_rules(self):
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream/rules", auth=self._twitter_bearer_token
        )
        if response.status_code != 200:
            raise Exception(
                "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
            )
        print(json.dumps(response.json()))
        return response.json()


    def _delete_all_rules(self, rules):
        if rules is None or "data" not in rules:
            return None

        ids = list(map(lambda rule: rule["id"], rules["data"]))
        payload = {"delete": {"ids": ids}}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=self._twitter_bearer_token,
            json=payload
        )
        if response.status_code != 200:
            raise Exception(
                "Cannot delete rules (HTTP {}): {}".format(
                    response.status_code, response.text
                )
            )
        print(json.dumps(response.json()))


    def _set_rules(self, delete):
        # You can adjust the rules if needed
        ETH_search_rules = [
            {
                "value": "#ETH OR #ethereum OR #eth is:retweet"
            },
        ]
        payload = {"add": ETH_search_rules}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=self._twitter_bearer_token,
            json=payload,
        )
        if response.status_code != 201:
            raise Exception(
                "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
            )
        print(json.dumps(response.json()))

    def _get_stream(self, set):
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream?tweet.fields=public_metrics", auth=self._twitter_bearer_token, stream=True,
        )
        print(response)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(
                "Cannot get stream (HTTP {}): {}".format(
                    response.status_code, response.text
                )
            )
        batch = []
        print(f"collecting tweets...")
        for response_line in response.iter_lines():
            if response_line:
                response = json.loads(response_line)
                batch.append(response)
                if len(batch) >= BATCH_SIZE:
                    file_name = f"{self.prefix}{datetime.now().time().isoformat()}.json"
                    formatted = json.dumps(batch, indent=4, sort_keys=True)
                    print(f"saving {len(batch)} tweets as {file_name}")
                    self.s3_client.put_object(bucket, f"{file_name}", io.BytesIO(bytes(formatted, "utf-8")), len(formatted))
                    print(f"saved {file_name}")
                    i = i + 1
                    batch = []
                    print(f"collecting tweets...")


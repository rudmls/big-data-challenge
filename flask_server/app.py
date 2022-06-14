from flask import Flask, render_template, Response
from pykafka import KafkaClient

app = Flask(__name__)


def get_kafka_client():
    return KafkaClient(hosts='127.0.0.1:9092')


@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html")


@app.route('/topic/<topic_name>')
def get_messages(topic_name):
    kafka_client = get_kafka_client()
    server_topics = kafka_client.topics

    def events():
        if str.encode(topic_name) in server_topics:
            for i in kafka_client.topics[topic_name].get_simple_consumer():
                yield 'data:{0}\n\n'.format(i.value.decode())

    return Response(events(), mimetype="text/event-stream")


if __name__ == '__main__':
    app.run()

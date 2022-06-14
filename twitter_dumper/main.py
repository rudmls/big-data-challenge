import sys
import dataconf

from app.config import Config
from app.dumper import Dumper
from twitter_dumper.app.streamer import Streamer


def read_arguments(arguments):
    try:
        if len(arguments) > 1:
            config_file = arguments[1]
            config = dataconf.load(config_file, Config)
            return config
        else:
            raise Exception("json configuration file is required")
    except Exception as ex:
        print(ex)


def main():
    try:
        config = read_arguments(sys.argv)
        dumper = Dumper(config)
        streamer = Streamer(config)
        streamer.start()
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    main()

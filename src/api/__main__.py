#!/usr/bin/env python3

from api import app
import config


def main():
    config.load_logging_config()
    app.run(port=8080)


if __name__ == '__main__':
    main()

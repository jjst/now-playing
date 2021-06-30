#!/usr/bin/env python3

from api import create_app
import base.config as config


def main():
    config.load_logging_config()
    app = create_app()
    app.run(port=8080)


if __name__ == '__main__':
    main()

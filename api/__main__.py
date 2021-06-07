#!/usr/bin/env python3

from api import app
import logging

logging.basicConfig(level='DEBUG')


def main():
    app.run(port=8080)


if __name__ == '__main__':
    main()

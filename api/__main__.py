#!/usr/bin/env python3

from api import app
import logging

# FIXME configure via config file instead
logging.basicConfig(level='DEBUG', force=True)


def main():
    app.run(port=8080)


if __name__ == '__main__':
    main()

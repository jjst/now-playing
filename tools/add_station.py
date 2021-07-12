# -*- coding: utf-8 -*-
import questionary


def main():
    print("Want to add a new radio station? Let me help you out!")
    station_name = questionary.text("What is the station name?").ask()
    print(station_name)


if __name__ == '__main__':
    main()

import bs4
import requests
import signal
from sys import exit
from notifypy import Notify
from bs4 import BeautifulSoup


def find_class_in_table(table_root: bs4.element.Tag, string: str):
    for tr_tag in table_root.find_all('tr'):
        for td_tag in tr_tag.find_all('td'):
            if string in td_tag.get_text():
                return td_tag
    return None


def find_in_sibling(tag, search_string):
    for sibling in tag.find_next_siblings():
        if search_string in sibling.getText():
            return True
    return False


def handler(signum, frame):
    res = input("Ctrl-C was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        exit(1)


def main():
    signal.signal(signal.SIGINT, handler)

    page: requests.Response
    soup: BeautifulSoup
    classcode: str
    URL = "https://resources.msoe.edu/sched/courses/all"

    classExists = False
    classIsOpen = False

    while not classExists:
        print("Enter Classcode")
        classcode = '  '.join(input().strip(' ').split(" ", 1))

        soup = BeautifulSoup(requests.get(URL).content, "html.parser")
        table: bs4.element.Tag = soup.find(class_="course-table").find("tbody")

        tag: bs4.element.Tag = find_class_in_table(table, classcode)
        if tag is not None:
            siblings = tag.find_next_siblings()
            print("Ok, found " + classcode + ": " + siblings[0].getText() + " with " + siblings[2].getText())
            print("This class is currently " + siblings[1].getText())
            classExists = True

            if "Open" in siblings[1].getText():
                print("Class is currently open! Go Register")
                classIsOpen = True
            else:
                print("Monitoring Class for open seats")

        else:
            print("Error: Class not found")

    while not classIsOpen:
        soup = BeautifulSoup(requests.get(URL).content, "html.parser")
        table = soup.find(class_="course-table").find("tbody")

        correct_tag = find_class_in_table(table, classcode)
        status = find_in_sibling(correct_tag, "Open")

        if status:
            notification = Notify()
            notification.title = "ALERT: CLASS IS OPEN"
            notification.message = classcode + ' is now open'
            notification.send()
            classIsOpen = True


if __name__ == "__main__":
    main()

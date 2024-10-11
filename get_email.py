import datetime as dt
import email
from email import policy
from email.header import decode_header
from email.message import EmailMessage
import imaplib
from itertools import islice
# import base64
# from bs4 import BeautifulSoup
# import re

from config import EMAIL_DATA, NUMBER_OF_LETTERS


def get_mail(server, username, password, number_of_letters):
    imap = imaplib.IMAP4_SSL(server)
    imap.login(username, password)
    imap.select("INBOX")
    print(f'Последние {number_of_letters} писем учетной записи: {username}')
    unseen_msgs = imap.uid('search', 'UNSEEN', 'ALL')[1][0].split()
    all_msg = (imap.uid('search', 'ALL')[1][0].split())
    for idx in islice(reversed(all_msg), number_of_letters):
        _, raw_msg = imap.uid('fetch', idx, '(RFC822)')
        msg: EmailMessage = email.message_from_bytes(raw_msg[0][1], policy=policy.default)
        letter_date = dt.datetime(*email.utils.parsedate_tz(msg["Date"])[:5])
        if type(decode_header(msg['From'])[0][0]) is bytes:
            letter_from = decode_header(msg['From'])[0][0].decode()
        else:
            letter_from = msg['From']
        content = msg.get_body().get_content()
        letter_ret_path = msg['Return-path']
        header = decode_header(msg["Subject"])[0][0]
        print(
            f'Время письма: {letter_date.strftime("%d.%m.%Y %H:%M:%S")}, '
            f'Получено от {letter_from}, Обратный адрес: {letter_ret_path}, '
            f'Тема: {header}'
        )
        if idx in unseen_msgs:
            imap.uid('STORE', idx, '-FLAGS', '(\Seen)')  # W605
        # read_mesage = input('Вывести текст письма? 1 - да')
        # if read_mesage == '1':
        #     payload = msg.get_payload()


def main():
    number_of_letters: int = NUMBER_OF_LETTERS
    for box in EMAIL_DATA:
        server = box['server']
        username = box['username']
        password = box['password']
        get_mail(server, username, password, number_of_letters)


if __name__ == '__main__':
    main()

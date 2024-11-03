from bs4 import BeautifulSoup
import datetime as dt
import email
from email import policy
from email.header import decode_header
from email.message import EmailMessage
import imaplib
from itertools import islice
from prettytable import PrettyTable, HRuleStyle

from accounts import EMAIL_DATA
from config import (
    NUMBER_OF_LETTERS,
    TABLE_MAX_WIGHT,
    FIELD_MIN_WIGHT,
    FIELD_MAX_WIGHT,
    INCLUDE_TEXT
)


def get_mail(server, username, password, number_of_letters):
    imap = imaplib.IMAP4_SSL(server)
    imap.login(username, password)
    imap.select("INBOX")
    print(f'Последние {number_of_letters} писем учетной записи: {username}')
    unseen_msgs = imap.uid('search', 'UNSEEN', 'ALL')[1][0].split()
    all_msg = (imap.uid('search', 'ALL')[1][0].split())
    table = PrettyTable()
    field_names = [
        'Время письма', 'Получено от', 'Обратный адрес', 'Тема'
    ]
    if INCLUDE_TEXT:
        field_names.append('Текст')
    table.field_names = field_names
    table.max_table_width = TABLE_MAX_WIGHT
    table.min_width = FIELD_MIN_WIGHT
    table.max_width = FIELD_MAX_WIGHT
    table.hrules = HRuleStyle.ALL
    for idx in islice(reversed(all_msg), number_of_letters):
        _, raw_msg = imap.uid('fetch', idx, '(RFC822)')
        msg: EmailMessage = email.message_from_bytes(
            raw_msg[0][1], policy=policy.default
        )
        letter_date = dt.datetime(*email.utils.parsedate_tz(msg["Date"])[:5])
        if type(decode_header(msg['From'])[0][0]) is bytes:
            letter_from = decode_header(msg['From'])[0][0].decode()
        else:
            letter_from = msg['From']
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                # text = TEXT_MAKER.handle(part.get_content())
                soup = BeautifulSoup(part.get_content(), 'html.parser')
                text = soup.get_text()
            elif part.get_content_type() == 'text/plain':
                text = part.get_content()
                break
        text = text.replace('\n', ' ').replace(
            '\r', ' ').replace('\t', ' ').replace('   ', ' ')
        letter_ret_path = msg['Return-path']
        header = decode_header(msg["Subject"])[0][0]
        row = [
            letter_date.strftime("%d.%m.%Y %H:%M:%S"),
            letter_from,
            letter_ret_path,
            header,
        ]
        if INCLUDE_TEXT:
            row.append(text)
        table.add_row(row)
        if idx in unseen_msgs:
            imap.uid('STORE', idx, '-FLAGS', '(\Seen)')  # W605
    print(table)
    print('')


def main():
    print('')
    choice = ''
    while choice != '0':
        number_of_letters: int = NUMBER_OF_LETTERS
        for box in EMAIL_DATA:
            server = box['server']
            username = box['username']
            password = box['password']
            get_mail(server, username, password, number_of_letters)
        choice = input(
            'Для повторной проверки нажмите Enter. Для выхода из программы - '
            '0 и Enter:'
            )


if __name__ == '__main__':
    main()

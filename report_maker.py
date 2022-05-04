import os
from datetime import datetime
import shelve
import api
from settings import *


def get_report_datetime(username: str) -> str | None:
    try:
        with shelve.open(r'metadata\reports_datetime') as dbm:
            datetime_str = dbm[username]
        return datetime_str
    except OSError:
        print('Ошибка при получении метаданных отчёта.')
        return None


def save_report_datetime(username: str) -> None:
    if not os.path.exists('metadata'):
        os.mkdir('metadata')
    with shelve.open(r'metadata\reports_datetime') as dbm:
        dbm[username] = datetime.now().strftime('%Y-%m-%dT%H-%M')


def get_report_text(user: dict) -> str:
    completed_todos_text = '\n'.join(user['completed_todos'])
    uncompleted_todos_text = '\n'.join(user['uncompleted_todos'])
    report = (
        f'Отчёт для {user["company"]["name"]}.\n'
        f'{user["name"]} <{user["email"]}> {datetime.now().strftime("%d.%m.%Y %H:%M")}\n'
        f'Всего задач: {len(user["completed_todos"]) + len(user["uncompleted_todos"])}\n\n'
        f'Завершенные задачи ({len(user["completed_todos"])}):\n'
        f'{completed_todos_text}\n\n'
        f'Оставшиеся задачи ({len(user["uncompleted_todos"])}):\n'
        f'{uncompleted_todos_text}\n\n'
    )
    return report


def write_report(user: dict) -> None:
    try:
        report_text = get_report_text(user)
        with open(f'{user["username"]}.txt', 'w', encoding='utf-8') as file:
            file.write(report_text)
        save_report_datetime(user['username'])
    except OSError:
        print('Ошибка при создании файла отчёта.')


def rename_report(username: str) -> None:
    date_time = get_report_datetime(username)
    if date_time and not os.path.isfile(f'old_{username}_{date_time}.txt'):
        os.rename(f'{username}.txt', f'old_{username}_{date_time}.txt')


def make_report(user: dict) -> None:
    if os.path.isfile(f'{user["username"]}.txt'):
        rename_report(user['username'])
    write_report(user)


def get_users() -> dict[dict] | None:
    try:
        users = {}
        for user in api.get_users():
            if 'id' in user:
                users[user['id']] = user | {'completed_todos': [], 'uncompleted_todos': []}

        for todo in api.get_todos():
            if 'title' in todo:
                title = todo['title']
                title = f'{title[:MAX_TITLE_LENGTH]}...' if len(title) > MAX_TITLE_LENGTH else title
            else:
                title = None

            if 'userId' in todo and todo['completed']:
                users[todo['userId']]['completed_todos'].append(title)
            elif 'userId' in todo and not todo['completed']:
                users[todo['userId']]['uncompleted_todos'].append(title)
    except TypeError:
        print('Ошибка при обработке данных пользователей')
        users = None
    return users


def switch_to_working_directory() -> None:
    try:
        if not os.path.exists(WORKING_DIRECTORY_NAME):
            os.mkdir(WORKING_DIRECTORY_NAME)
        os.chdir(WORKING_DIRECTORY_NAME)
    except OSError:
        print('Ошибка при создании рабочей папки')


def make_reports() -> None:
    switch_to_working_directory()
    if os.path.basename(os.getcwd()) == WORKING_DIRECTORY_NAME:
        users = get_users()
        if users:
            for user in users.values():
                make_report(user)

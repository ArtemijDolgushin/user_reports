from settings import *
import requests


def fetch(url: str) -> list[dict] | None:
    try:
        request = requests.get(url)
        return request.json()
    except requests.exceptions.RequestException:
        print('Ошибка при получении данных с сервера.')
        return None


def get_users() -> list[dict] | None:
    users = fetch(USERS_URL)
    return users


def get_todos() -> list[dict] | None:
    todos = fetch(TODOS_URL)
    return todos

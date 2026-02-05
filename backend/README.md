![example workflow](https://github.com/viva-lavita/foodgram-project-react/actions/workflows/main.yml/badge.svg)

[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com)
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru)

# drf-jwt_template

Шаблон для нового проекта Django с JWT аутентификацией. Django 5 версии.
Для использования этого шаблона в собственном проекте используйте кнопку `Use this template` в правом верхнем углу экрана.

> Важно. У вас должен быть установлен пакетный менеджер uv. [Документация](https://docs.astral.sh/uv/getting-started/installation/#pypi).
> Nginx и docker-compose настроены под next.js.

## Технологии

1. Реализована аутентификация на основании токенов JWT (библиотека [djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html)).
2. Эндпоинты юзера и аутентификации реализованы с помощью библиотеки [djoser](https://djoser.readthedocs.io/en/latest/getting_started.html).
3. Подключен Swagger (OpenAPI 3.0, использован [drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/), готовая статика для добавлена через [drf-spectacular-sidecar](https://drf-spectacular.readthedocs.io/en/latest/readme.html)).
4. Подключен [ruff](https://docs.astral.sh/ruff/), настройки в pyproject.toml (dev зависимость).
5. Подключены [django-filters](https://django-filter.readthedocs.io/en/main/).
6. В dev зависимости добавлены и настроены [pre-commit](https://pre-commit.com/) и [django-debug-toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/installation.html).
7. Добавлены файлы [docker](https://docs.docker.com/build/) и [docker-compose](https://docs.docker.com/compose/) (dev и prod версии под next.js).
8. Настроен [Nginx](https://docs.nginx.com/), конфигурационный файл nginx.conf в папке infra.
9. Настроен CI/CD в .git/workflows/deploy.yml. На сервер .env переменные передаются из secrets GitHub, необходимо ознакомиться со списком и добавить их в настройки вашего репозитория.

## Настройки

- Добавлен тротлинг запросов, настойка в settings.py -> REST_FRAMEWORK.
- Доступ до дефолту - IsAuthenticatedOrReadOnly.
- Прописан шаблон кастомного обработчика ошибок (404), добавление новых в api/exceptions.py.
- Пагинация по дефолту - PageNumberPagination. Также в api/paginations.py дописана кастомная пагинация с запрашиваемым размером выдачи.
- Переопределен AbstractUser, добавлены поля created_at и updated_at, поле email сделано обязательным. Поле username упразднено, авторизация происходит по полю email.

### ENV

В репозитории добавлен файл `.env.example`, вы можете воспользоваться этим шаблоном для формирования собственного файла `.env`.
Для генерации SECRET_KEY вы можете выполнить следующую команду:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### pre-commit

В репозитории перед пушем изменений настроена автоматическая проверка линтерами (полный список см конфиг .pre-commit-config.yaml), чтобы эта утилита запустилась, один раз после копирования репозитория, находясь в корне проекта или глубже, в терминале запустите команду:

```bash
pre-commit install
```

Теперь если при попытке создания коммита в коде были ошибки стилистики - они будут исправлены. Добавьте изменения и создайте коммит еще раз.

### OpenAPI

Настроено автоматическое документирование api.
С помощью нее вы можете протестировать конечные точки на корректность выполнения.
Документация доступна по адресу `/schema/swagger-ui/`.

Чтобы создать авторизованного пользователя, необходимо:

1. Создание пользователя в БД - POST запрос на эндпоинт `api/v1/users`
2. Получение токена - POST запрос на эндпоинт `api/v1/jwt/create/`
3. Передача токена при каждом запросе - из ответа этапа 2 скопируйте значение ключа "access", без скобок. Далее нажмите на кнопку Authorize (правый верхний угол экрана от начала страницы) и в поле модального окна вставьте скопированный токен.

Также можно логиниться не в целом на все эндпоинты, а только на некоторые, для этого над каждой конечной точкой есть иконка замка, нажмите ее, и вставьте токен в поле ввода появившегося модального окна.

### docker-compose

В проекте два docker-compose файла -  для дев и прод версий.

Команда пересборки dev-контейнеров:

```bash
docker compose -f docker-compose.dev.yml up --build
```

Команда для прод сборки:

```bash
docker compose up
```

Обратите внимание, если для локальной разработке в контейнерах вы захотите сделать двухстороннюю синхронизацию, чтобы изменения в коде сразу прогружались в контейнер и наоборот, с текущей версией у вас ничего не получится, так как для образа используется uv, который создает виртуальную среду внутри контейнера, что создает коллизии (попытка перезаписать существующий в локальной версии .venv) и виртуальная среда не распознается.
Если вам нужен данный функционал, можно воспользоваться советами из [этого обсуждения](https://github.com/astral-sh/uv/issues/9423).

### CI/CD

Настроен алгоритм непрерывной развертки, скрипт находится в .git/workflows/deploy.yml.

Обратите внимание, .env файл на сервере создается заново, после каждого деплоя. Значение переменных для файла берется из Secrets репозитория. Необходимо ознакомиться со списком необходимых переменных в скрипте и создать эти переменные в Settings -> Secrets and variables -> Actions -> New repository secret.

### Перевод

Использование:

```python
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=254,
        unique=True,
        help_text=_(
            "Required. 254 characters or fewer. "
            "Letters, digits and @/./+/-/_ only."
        ),
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
```

Для формирования файла перевода на русском используйте [команду](https://docs.djangoproject.com/en/5.2/ref/django-admin/#django-admin-makemessages):

```bash
django-admin makemessages --locale=ru
```

В файле backend/locale/ru/LC_MESSAGES/django.po пропишите переводы помеченных фраз и скомпилируйте итоговый .mo файл:

```bash
python manage.py compilemessages -l ru
```

Локаль меняется в settings.py в разделе INTERNATIONALIZATION. [Документация](https://docs.djangoproject.com/en/4.2/topics/i18n/)

Данный функционал добавлен только для однообразности отображения модели юзера в админке, т.к. часть полей этой модели определено самим django именно в таком стиле.

# Порядок запуска

## Запуск проекта локально

1. Создайте репозиторий используя этот шаблон (кнопка `Use this template` в правом верхнем углу экрана) и клонируйте репозиторий.
2. Перейдите в каталог `backend`, создайте и активируйте виртуальное окружение, загрузите зависимости:

    ```bash
    cd backend
    uv sync
    source .venv/Scripts/activate
    ```

3. Создайте в корне проекта файл `.env` использовав переменные из .env.example. Сгенерируйте и заполните SECRET_KEY.
4. Создаем и проводим миграции:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. Собираем статику:

    ```bash
    python manage.py collectstatic
    ```

6. Создаем суперюзера:

    ```bash
    python manage.py createsuperuser
    ```

7. Компилируем файл перевода:

    ```bash
    python manage.py compilemessages -l ru
    ```

Проект готов к старту!

Запуск сервера:

```bash
python manage.py runserver
```

## Запуск проекта в контейнерах docker

1. Создайте репозиторий используя этот шаблон (кнопка `Use this template` в правом верхнем углу экрана).
2. Клонируйте репозиторий.
3. Создайте в корне проекта файл `.env`.
4. Запустите контейнеры:

    ```bash
    docker compose -f docker-compose.dev.yml up --build
    ```

## Запуск в продакшн

В репозитории настроен workflow, который сбилдит docker-образ, отправит его на докерхаб, подключится к продакшен серверу, обновит файл .env, остановит старые контейнеры, удалит образа, загрузит свежий и запустит новые контейнеры.
Ознакомьтесь с списком полей .env файла, создайте secrets в github с этими значениями и дополните, при необходимости.
Также при пуллреквесте и пуше в workflow добавлена проверка линтером папки backend. Можно расширить фронт частью, либо удалить совсем.

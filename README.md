Описание
Фудграм - сервис, на котором пользователи могут:

Публиковать рецепты

Добавлять рецепты в избранное

Подписываться на авторов

Использовать "Список покупок" (скачивание списка ингредиентов)

Использованные технологии
```
Python 3.11.2
Django
Django REST Framework
Docker, Docker Compose, Docker Hub
GitHub Actions (CI/CD)
Gunicorn
Nginx
PostgreSQL
```
Запуск проекта локально

Клонировать репозиторий:
```
bash
git clone git@github.com:Dmitriev-Igor/foodgram.git
cd foodgram
```

Настроить окружение:
```
bash
cp .env.example .env
# Заполнить .env своими значениями
```

Запустить контейнеры:
```
bash
sudo docker compose up --build
```

Настроить бэкенд:
```
bash
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic
sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
sudo docker compose exec backend python manage.py createsuperuser
Запуск бэкенда локально (без Docker)
```

Установить зависимости:
```
bash
python -m venv venv
source venv/Scripts/activate  # Для Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Запустить сервер:
```
bash
python manage.py migrate
python manage.py runserver
```

Пример файла .env
```
env
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=foodgram_db
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,foodgram25.duckdns.org
```

Развернутый проект
Проект доступен по адресу:
🔗 https://foodgram25.duckdns.org
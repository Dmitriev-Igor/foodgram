Описание
Фудграм - сервис, на котором пользователи могут публиковать свои инструкции по приготовлению (рецепты), добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям доступен сервис «Список покупок», он позволяет создать и скачать в виде файла список продуктов, которые нужно купить для приготовления добавленных в «Список покупок» блюд.

Использованные технологии
Python 
Django 
Django REST Framework
Контейнеризация: Docker, Docker Compose, Docker Hub
CI/CD: GitHub Actions
Gunicorn
Nginx
PostgreSQL

Запуск проекта локально
Клонировать репозиторий:

git clone git@github.com:Dmitriev-Igor/foodgram.git

Перейти в директорию проекта:

cd foodgram
Создать в директории проекта и заполнить файл .env собственными cекретами по примеру файла .env.example:

POSTGRES_USER=<имя_пользователя_БД>
POSTGRES_PASSWORD=<пароль_БД>
POSTGRES_DB=<имя_БД>
DB_HOST=db
DB_PORT=5432
SECRET_KEY=<секретный_ключ_Django>
DEBUG=<False>
ALLOWED_HOSTS=<перечислить через запятую доменные имена и IP-адреса>


Запустить из директории проекта, где лежит файл docker-compose.yml контейнеры:
sudo docker compose up --build

В контейнере бэкенда применить миграции, собрать статику и скопировать ее в директорию, подключенную к volume, создать суперпользователя:

sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic
sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
sudo docker compose exec backend python manage.py createsuperuser


Запуск бэкенда локально
Клонировать репозиторий:

git clone git@github.com:Dmitriev-Igor/foodgram.git

Перейти в директорию:

cd foodgram/backend

Создать и активировать виртуальное окружение:

python -m venv venv
source venv/Scripts/activate

Установить зависимости и выполнить миграции:

pip install -r requirements.txt
python manage.py migrate

Запустить сервер разработки:

python manage.py runserver
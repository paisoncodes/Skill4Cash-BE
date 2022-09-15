release: python manage.py makemigrations authentication, services
release: python manage.py migrate
web: gunicorn src.wsgi --log-file -
dropdb test
createdb test
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser --username admin --email sipakov.v@rambler.ru
python3 manage.py runserver 0.0.0.0:8000
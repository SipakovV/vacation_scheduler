dropdb test
createdb test
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser --username admin --email sipakov.v@rambler.ru

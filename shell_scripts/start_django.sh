# Migrate created migrations to database
python manage.py makemigrations --noinput --check --verbosity 2 || exit 1
python manage.py check || exit 1
python manage.py migrate
python manage.py init_data

# Start gunicorn server at port 8000 and keep an eye for app code changes
# If changes occur, kill worker and start a new one
#gunicorn --reload project.wsgi:application -b 0.0.0.0:8000
python manage.py runserver  0.0.0.0:8000

web: python manage.py collectstatic --noinput; python manage.py migrate --noinput; gunicorn crm_usecap.wsgi:application --bind 0.0.0.0:$PORT

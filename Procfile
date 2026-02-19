web: python manage.py collectstatic --noinput; python manage.py migrate --noinput; python manage.py normalize_data; gunicorn crm_usecap.wsgi:application --bind 0.0.0.0:$PORT

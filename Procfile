web: gunicorn stockhelper/stockhelper.wsgi
release: python3 stockhelper/manage.py migrate
release: python3 stockhelper/manage.py loaddata cards.json

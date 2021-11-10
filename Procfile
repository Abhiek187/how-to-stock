web: cd stockhelper && gunicorn stockhelper.wsgi
release: python3 stockhelper/manage.py migrate; python3 stockhelper/manage.py loaddata cards.json

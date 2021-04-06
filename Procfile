web: gunicorn 'server.run:create_app()'
worker: celery --app server.app.CELERY_APP worker --events --beat --loglevel info

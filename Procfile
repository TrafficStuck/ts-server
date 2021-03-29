web: gunicorn 'server.run:create_app()'
celery: celery --app server.app.CELERY_APP worker --events --beat --loglevel info

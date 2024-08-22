export $(cat .env | xargs)
gunicorn --worker-class eventlet -w 1 src.app:app --reload
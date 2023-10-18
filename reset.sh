rm db.sqlite3
rm -rf communication/migrations/
rm -rf communication/__pycache__/
rm -rf omni/__pycache__/
python3 manage.py migrate --run-syncdb
python3 manage.py createsuperuser

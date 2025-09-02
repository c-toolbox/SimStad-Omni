rm db.sqlite3
rm -rf communication/migrations/
rm -rf communication/__pycache__/
rm -rf simstad/migrations/
rm -rf simstad/__pycache__/
rm -rf omni/__pycache__/
rm -rf media/
python3 manage.py makemigrations communication
python3 manage.py makemigrations simstad
python3 manage.py migrate --run-syncdb
python3 manage.py createsuperuser

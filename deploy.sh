cd /home/mange61/omni/
source .venv/bin/activate

git pull

rm -rf /var/www/static
# cp -r dist/static /var/www

python manage.py makemigrations
python manage.py migrate --run-syncdb
python manage.py collectstatic --noinput

# service omni restart

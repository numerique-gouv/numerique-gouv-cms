postdeploy: python manage.py migrate && python manage.py import_dsfr_pictograms && python manage.py import_page_templates && python manage.py update_index && collectstatic --noinput --ignore=*.sass
web: gunicorn config.wsgi --log-file -

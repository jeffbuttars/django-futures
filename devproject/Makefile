
SERVER_IP = localhost:8000
.PHONY: reset run rundbg clean

# Re-install django-tornado
reset:
	-yes y | pip uninstall --exists-action=w django-tornado
	pip install --exists-action=w --pre --no-deps ../src/

# run in production mode
run: reset
	cd dj; export DJANGO_DEBUG=''; ./manage.py collectstatic -l --noinput; ./manage.py run_tornado

# run in debug mode
rundbg: reset
	cd dj; export DJANGO_DEBUG=True; ./manage.py run_tornado $(SERVER_IP)

clean:
	find . -iname '*.pyc' | xargs rm -fv
	find . -name '__pycache__' | xargs rm -fvr

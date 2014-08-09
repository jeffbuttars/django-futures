
VENV := . .venv/bin/activate

SERVER_IP = localhost:8000
.PHONY: reset run rundbg clean

RUNDJDBG := cd dj; export DJANGO_DEBUG=True; ./manage.py run_tornado $(SERVER_IP)
RUNDJ := cd dj; export DJANGO_DEBUG=''; ./manage.py collectstatic -l --noinput; ./manage.py run_tornado

# Re-install django-futures
reset:
	-$(VENV); \
	yes y | pip uninstall --exists-action=w django-futures
	pip install --exists-action=w --pre --no-deps ../src/

resetpkg:
	-$(VENV); \
	dv=$$(cd ../src; python -c "import django_futures; print(django_futures.__version__)");\
	yes y | pip uninstall --exists-action=w django-futures;\
	pip install --exists-action=w --pre --no-deps ../src/dist/django-futures-$$dv.tar.gz

# run in production mode
run: reset
	$(RUNDJ)

runpkg: resetpkg
	$(RUNDJ)

# run in debug mode
rundbg: reset
	$(RUNDJDBG)

runpkgdbg: resetpkg
	$(RUNDJDBG)

clean:
	find . -iname '*.pyc' | xargs rm -fv
	find . -name '__pycache__' | xargs rm -fvr

"""
``django_futures.management.commands.run_tornado.py``

``run_tornado.py`` -- ``run_tornado``
===========================================

Django Futures includes in a management command for easily running the
Tornado web server with Django. Running Tornado is necessary for utilizing
the asynchronous features of Django Futures.

The ``run_tornado`` management command supports the same options as Django's
builtin
`runserver <https://docs.djangoproject.com/en/dev/ref/django-admin/#runserver-port-or-address-port>`_
command plus some Tornado specific options.

The extra options offered by ``run_tornado``:
-----------------------------------------------------

* `--gzip` Enable Tornado's gzip
* `--save_traceback` Enable Tornado's save_traceback and print a traceback
* `--static` Enable Tornado's static file handling
* `--static_hash_cache` Enable Tornado's static_hash_cache option
"""

from optparse import make_option
import socket
import re


import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
from django.conf import settings
from django.core.management.base import BaseCommand
from django_futures.core.handlers.application import DjangoApplication


def t_run(addr, port, t_app, ipv6=False, threading=False):
    """
    :param addr: IP Address the web server will listen on. Default is 8000
    :type addr: int
    :param port: Port the web server will listen on
    :type port: int
    :param t_app: DjangoApplication instance
    :type t_app: `django_futures.core.handlers.application.DjangoApplication`
    :param ipv6: Explicitly set addr as type IPv6
    :type ipv6: bool
    :param threading: Not Used
    :type threading:

    We monkey patch the built in ``run()`` with our own Tornado based version,
    ``t_run()``.
    """

    fam = socket.AF_UNSPEC
    if ipv6:
        fam = socket.AF_INET6    

    server = tornado.httpserver.HTTPServer(t_app)
    server.bind(port, address=addr, family=fam)
    server.start(t_app.settings['num_proc'])
    tornado.ioloop.IOLoop.instance().start()

import django.core.servers.basehttp
django.core.servers.basehttp.run = t_run

from django.core.management.commands.runserver import Command as RSCommand

naiveip_re = re.compile(r"""^(?:
(?P<addr>
    (?P<ipv4>\d{1,3}(?:\.\d{1,3}){3}) |         # IPv4 address
    (?P<ipv6>\[[a-fA-F0-9:]+\]) |               # IPv6 address
    (?P<fqdn>[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*) # FQDN
):)?(?P<port>\d+)$""", re.X)

DEFAULT_PORT = "8000"


# Use the builtin runserver command as our base
class Command(RSCommand):
    """
    ``run_tornado``
    """

    def get_handler(self, *args, **options):
        """
        Returns an Application instance for the Tornado server
        """

        app_kwargs = {
            'debug': settings.DEBUG,
            'autoreload': options.get('use_reloader'),
            'gzip': options.get('gzip'),
            'num_proc': options.get('num_proc'),
            'save_traceback': options.get('save_traceback'),
            'static': options.get('static'),
            'static_hash_cache': options.get('static_hash_cache'),
        }

        if settings.DEBUG and not options['static']:
            app_kwargs['staticfiles'] = True
            if app_kwargs['num_proc'] != 1:
                self.stdout.write("DEBUG is True, num_proc is always 1 with DEBUG\n")
                app_kwargs['num_proc'] = 1

        return DjangoApplication(**app_kwargs)
    # get_handler()

    help = ("Starts a Tornado server instance for development or production")
    args = '[optional port number, or ipaddr:port]'

    NUM_PROCS = 0
    if settings.DEBUG:
        NUM_PROCS = 1

    option_list = RSCommand.option_list
    option_list += (
        make_option(
            '--num_proc',
            dest='num_proc',
            default=NUM_PROCS,
            help=("The number of tornado processes to use. Default is 1 in Debug mode and 0/auto"
                  " in non-debug mode. Using a value of 0 will cause tornado to create as many"
                  " processes are there are cores."),
        ),

        make_option(
            '--gzip',
            dest='gzip',
            default=False,
            help="Enable Tornado's gzip.",
        ),

        make_option(
            '--save_traceback',
            dest='save_traceback',
            default=False,
            help="Enable Tornado's save_traceback and print a traceback",
        ),

        make_option(
            '--static',
            dest='static',
            default=False,
            help="Enable Tornado's static file handling",
        ),

        make_option(
            '--static_hash_cache',
            dest='static_hash_cache',
            default=False,
            help="Enable Tornado's static_hash_cache option",
        ),
    )
# Command

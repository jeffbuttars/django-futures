import logging
# logger = logging.getLogger('django.request')
logger = logging.getLogger('django.debug')

from django import http
from django.core.handlers import base


class TornadoRequest(http.HttpRequest):
    """Docstring for TornadoRequest """
    pass
# TornadoRequest


class TornadoHandler(base.BaseHandler):
    """Docstring for TornadoHandler """
    pass
# TornadoHandler

"""
``df.py``
==================================

`django_futures.core.handlers.tv40.df.py`
"""

import logging
# logger = logging.getLogger('django.request')
logger = logging.getLogger('django.debug')

import sys
import cgi
import codecs
import warnings
import types

from tornado.concurrent import is_future


from django import http
from django.core import signals
from django.views import debug
from django.conf import settings
from django.core import urlresolvers
from django.core.handlers import base
from django.utils import datastructures
from django.utils.functional import cached_property
from django.core.urlresolvers import set_script_prefix
from django.core.exceptions import PermissionDenied, SuspiciousOperation
try:
    from django.utils.deprecation import RemovedInDjango19Warning
except ImportError:
    class RemovedInDjango19Warning(PendingDeprecationWarning):
        pass

from django_futures.core.handlers.df import LimitedStream

from django.utils.encoding import force_text
# Do we need this? I hope not, but wsgi uses it.
# from threading import Lock


# encode() and decode() expect the charset to be a native string.
# ISO_8859_1, UTF_8 = str('iso-8859-1'), str('utf-8')


class TornadoRequest(http.HttpRequest):
    """Docstring for TornadoRequest """

    def __init__(self, t_req, handler):
        """todo: to be defined
        
        :param t_req: arg description
        :type t_req: type description
        """
        # logger.debug("TornadoRequest::__init__ request: %s", t_req)
        logger.debug("TornadoRequest::__init__ request")

        self.tornado_request = t_req
        self._handler = handler

        t_headers = t_req.headers

        script_name = get_script_name(t_req)
        # Sometimes PATH_INFO exists, but is empty (e.g. accessing
        # the SCRIPT_NAME URL without a trailing slash). We really need to
        # operate as if they'd requested '/'. Not amazingly nice to force
        # the path like this, but should be harmless.
        # path_info = get_path_info(t_req) or '/'
        path_info = t_req.path

        self.path_info = path_info
        self.path = '%s/%s' % (script_name.rstrip('/'), path_info.lstrip('/'))
        logger.debug("TornadoRequest::__init__  PATH %s", self.path)

        self.host = t_req.host

        self.META = t_headers
        # logger.debug("TornadoRequest::__init__ setting META %s", self.META)
        logger.debug("TornadoRequest::__init__ setting META ")

        self.method = t_req.method.upper()
        self.META['PATH_INFO'] = path_info
        self.META['SCRIPT_NAME'] = script_name
        host_parts = t_req.host.rsplit(':', 1)
        self.META['SERVER_NAME'] = host_parts[0]
        self.META['SERVER_PORT'] = host_parts[1]
        self.META['REQUEST_METHOD'] = self.method
        # logger.debug("TornadoRequest::__init__  META set %s", self.META)

        _, content_params = cgi.parse_header(t_headers.get('CONTENT_TYPE', ''))
        if 'charset' in content_params:
            try:
                codecs.lookup(content_params['charset'])
            except LookupError:
                pass
            else:
                self.encoding = content_params['charset']
        self._post_parse_error = False

        try:
            content_length = int(t_headers.get('CONTENT_LENGTH'), 0)
        except (ValueError, TypeError):
            content_length = 0

        self._stream = LimitedStream(t_req.body, content_length)
        self._read_started = False
        self.resolver_match = None
    # __init__()

    def _get_scheme(self):
        logger.debug("_get_scheme")
        return self.tornado_request.protocol
    # _get_scheme()

    def _get_request(self):
        warnings.warn('`request.REQUEST` is deprecated, use `request.GET` or '
                      '`request.POST` instead.', RemovedInDjango19Warning, 2)
        if not hasattr(self, '_request'):
            self._request = datastructures.MergeDict(self.POST, self.GET)
        return self._request

    @cached_property
    def GET(self):
        logger.debug("TornadoRequest GET")
        return http.QueryDict(
            self.tornado_request.query,
            encoding=self._encoding)

    def _get_post(self):
        logger.debug("TornadoRequest _get_post %s", self.tornado_request.body)
        return http.QueryDict(self.tornado_request.body, encoding=self._encoding)

    def _set_post(self, post):
        logger.debug("TornadoRequest _set_post %s ", post)
        self._post = post

    @cached_property
    def COOKIES(self):
        logger.debug("TornadoRequest COOKIES")
        # logger.debug("TornadoRequest COOKIES %s",
        #              self.tornado_request.cookies)
        # logger.debug("TornadoRequest COOKIES %s",
        #              http.parse_cookie(self.tornado_request.cookies))
        return http.parse_cookie(self.tornado_request.cookies)

    def _get_files(self):
        if not hasattr(self, '_files'):
            self._load_post_and_files()
        return self._files

    def render(self, response):
        """
        Render a Django response and finish up this request.
        You'll need to call this if the view function/method is a coroutine.
        """
        logger.debug("TornadoRequest::render")
        response = self._handler.finish_response(self, response)
        logger.debug("response: Finished")
    # render()

    def write(self, chunk):
        """
        Convenience wrapper for the Tornado request's write() method.
        """
        return self.tornado_request.write(chunk)
    # write()

    def finish(self):
        """
        Convenience wrapper for the Tornado request's finish() method.
        """
        return self.tornado_request.finish()
    # finish()

    POST = property(_get_post, _set_post)
    FILES = property(_get_files)
    REQUEST = property(_get_request)
# TornadoRequest


class TornadoHandler(base.BaseHandler):
    """
    A Django Request Handler to bridge a Tornado Request into a 
    Django Request.
    """

    # WSGI locks, Ideally, we don't run threaded, just multi process. But
    # keep this here as a note for now in case this comes up later.
    # initLock = Lock()
    request_class = TornadoRequest

    def __init__(self, t_request_handler):
        """todo: to be defined

        :param t_request_handler: arg description
        :type t_request_handler: type description
        """
        super(TornadoHandler, self).__init__()
        self._tornado_request_handler = t_request_handler

        self._response_finished = False
    # __init__()

    def __call__(self, t_req, on_finish=None):
        """todo: Docstring for __call__

        :param t_req: A tornado HTTPServerRequest instnace
        :type t_req: tornado HTTPServerRequest instnace
        :return:
        :rtype:
        """
        logger.debug("TornadoHandler __call__()")
        # logger.debug("TornadoHandler __call__ %s", t_req)
        self._when_finished = on_finish
        self.tornado_request = t_req
        self.tornado_future = None

        self.urlconf = settings.ROOT_URLCONF
        self.resolver = urlresolvers.RegexURLResolver(r'^/', self.urlconf)
        self.callback, self.callback_args, self.callback_kwargs = (None, None, None)

        # Set up middleware if needed. We couldn't do this earlier, because
        # settings weren't available.
        if self._request_middleware is None:
            # with self.initLock:
            try:
                # Check that middleware is still uninitialized.
                if self._request_middleware is None:
                    self.load_middleware()
            except:
                # Unload whatever middleware we got
                self._request_middleware = None
                raise

        set_script_prefix(get_script_name(t_req))

        signals.request_started.send(sender=self.__class__)
        try:
            request = self.request_class(t_req, self)
        except UnicodeDecodeError:
            logger.warning('Bad Request (UnicodeDecodeError)',
                           exc_info=sys.exc_info(),
                           extra={
                               'status_code': 400,
                           }
                           )
            response = http.HttpResponseBadRequest()
        else:
            # Send this DjangoRequest through the Django stack
            logger.debug("process request")
            response = self.get_response(request)

        # logger.debug("Done, returning response, _response_finished: %s", self._response_finished)
        if not self._response_finished:
            return response
    # __call__()

    def on_finish(self, response):
        logger.debug("TornadoHandler::_on_finish")
        # self._tornado_request_handler.django_finish_request(response)
    # on_finish()

    def _apply_request_middleware(self, request):
        """todo: Docstring for _apply_request_middleware
        
        :param request: arg description
        :type request: type description
        :return:
        :rtype:
        """
        # logger.debug("_apply_request_middleware request: %s", request)
        logger.debug("_apply_request_middleware request")
        urlresolvers.set_urlconf(self.urlconf)

        response = None
        # Apply request middleware
        for middleware_method in self._request_middleware:
            response = middleware_method(request)
            if response:
                break

        if response is None:
            if hasattr(request, 'urlconf'):
                # Reset url resolver with a custom urlconf.
                self.urlconf = request.urlconf
                urlresolvers.set_urlconf(self.urlconf)
                self.resolver = urlresolvers.RegexURLResolver(r'^/', self.urlconf)

            resolver_match = self.resolver.resolve(request.path_info)
            self.callback, self.callback_args, self.callback_kwargs = resolver_match
            request.resolver_match = resolver_match

        if is_future(response):
            logger.debug("TracebackFuture: %s", dir(response))
            # Dig out the original request.
            raise Exception("Holly Smokes!")

        # logger.debug("_apply_request_middleware returning: %s: %s",
        #              response, dir(response))
        logger.debug("_apply_request_middleware returning: %s: %s")
        return response
    # _apply_request_middleware()

    def _apply_view_midlleware(self, request, response):
        """todo: Docstring for _apply_view_midlleware
        
        :param request: arg description
        :type request: type description
        :return:
        :rtype:
        """
    
        logger.debug("_apply_view_midlleware request: \n%s\n%s", request, response)
        if response is None:
            # Apply view middleware
            for middleware_method in self._view_middleware:
                response = middleware_method(
                    request,
                    self.callback,
                    self.callback_args,
                    self.callback_kwargs)
                if response:
                    break

        return response
    # _apply_view_midlleware()

    def _call_view(self, request, response):
        """todo: Docstring for _call_view
        
        :param request: arg description
        :type request: type description
        :return:
        :rtype:
        """
        logger.debug("_call_view request: %s", request)

        if response is None:
            wrapped_callback = self.make_view_atomic(self.callback)
            try:
                response = wrapped_callback(request, *self.callback_args, **self.callback_kwargs)
            except Exception as e:
                # If the view raised an exception, run it through exception
                # middleware, and if the exception middleware returns a
                # response, use that. Otherwise, reraise the exception.
                for middleware_method in self._exception_middleware:
                    response = middleware_method(request, e)
                    if response:
                        break
                if response is None:
                    raise
        # Complain if the view returned None (a common error).
        if response is None:
            if isinstance(self.callback, types.FunctionType):    # FBV
                view_name = self.callback.__name__
            else:                                           # CBV
                view_name = self.callback.__class__.__name__ + '.__call__'
            raise ValueError("The view %s.%s didn't return an HttpResponse object." % (
                self.callback.__module__, view_name))

        return response
    # _call_view()

    def _apply_response_middleware(self, request, response):
        logger.debug("_apply_response_middleware response ")
        # Apply response middleware, regardless of the response
        for middleware_method in self._response_middleware:
            logger.debug("_apply_response_middleware %s", middleware_method)
            response = middleware_method(request, response)
        response = self.apply_response_fixes(request, response)

        return response
    # _apply_response_middleware()

    def _render_template(self, request, response):
        """todo: Docstring for _render_template
        
        :param request: arg description
        :type request: type description
        :param response: arg description
        :type response: type description
        :return:
        :rtype:
        """
        logger.debug("_render_template")
        # If the response supports deferred rendering, apply template
        # response middleware and then render the response
        if hasattr(response, 'render') and callable(response.render):
            for middleware_method in self._template_response_middleware:
                response = middleware_method(request, response)
            return response.render()

        return response
    # _render_template()

    def _on_finish(self, response):
        logger.debug("_on_finish")
        pass
    # _on_finish()

    def _handle_response_exception(self, request, response, e):

        if isinstance(e, http.Http404):
            logger.warning('Not Found: %s', request.path,
                           extra={
                               'status_code': 404,
                               'request': request
                           })
            if settings.DEBUG:
                response = debug.technical_404_response(request, e)
            else:
                try:
                    self.callback, param_dict = self.resolver.resolve404()
                    response = self.callback(request, **param_dict)
                except:
                    signals.got_request_exception.send(sender=self.__class__, request=request)
                    response = self.handle_uncaught_exception(
                        request, self.resolver, sys.exc_info())

        if isinstance(e, PermissionDenied):
            logger.warning(
                'Forbidden (Permission denied): %s', request.path,
                extra={
                    'status_code': 403,
                    'request': request
                })
            try:
                self.callback, param_dict = self.resolver.resolve403()
                response = self.callback(request, **param_dict)
            except:
                signals.got_request_exception.send(
                    sender=self.__class__, request=request)
                response = self.handle_uncaught_exception(request,
                                                          self.resolver, sys.exc_info())

        if isinstance(e, SuspiciousOperation):
            # The request logger receives events for any problematic request
            # The security logger receives events for all SuspiciousOperations
            security_logger = logging.getLogger('django.security.%s' %
                                                e.__class__.__name__)
            security_logger.error(force_text(e))

            try:
                self.callback, param_dict = self.resolver.resolve400()
                response = self.callback(request, **param_dict)
            except:
                signals.got_request_exception.send(
                    sender=self.__class__, request=request)
                response = self.handle_uncaught_exception(request,
                                                          self.resolver, sys.exc_info())

        if isinstance(e, SystemExit):
            # Allow sys.exit() to actually exit. See tickets #1023 and #4701
            raise

        else:  # Handle everything else.
            # Get the exception info now, in case another exception is thrown later.
            signals.got_request_exception.send(sender=self.__class__, request=request)
            response = self.handle_uncaught_exception(request, self.resolver, sys.exc_info())

        return response
    # _handle_response_exception()

    def start_response(self, request):
        """todo: Docstring for start_response
        
        :param request: arg description
        :type request: type description
        :return:
        :rtype:
        """
        logger.debug("TornadoHandler::start_response")

        response = None

        try:
            response = self._apply_request_middleware(request)
            response = self._apply_view_midlleware(request, response)
            response = self._call_view(request, response)

        except Exception as e:
            return self._handle_response_exception(request, response, e)

        return response
    # start_response()

    def finish_response(self, request, response):
        """Finish processing Django Request/Response instances

        :param request: arg description
        :type request: type description
        :param response: arg description
        :type response: type description
        :return:
        :rtype:
        """
        logger.debug("TornadoHandler::finish_response")

        try:
            response = self._render_template(request, response)
        except Exception as e:
            return self._handle_response_exception(request, response, e)

        try:
            self._apply_response_middleware(request, response)
        except:  # Any exception should be gathered and handled
            signals.got_request_exception.send(sender=self.__class__, request=request)
            response = self.handle_uncaught_exception(request, self.resolver, sys.exc_info())

        self._tornado_request_handler.django_finish_request(response)

        self._response_finished = True
        return response
    # finish_response()

    def get_response(self, request):
        "Returns an HttpResponse object for the given HttpRequest"
        # logger.debug("TornadoHandler get_response %s", request)
        logger.debug("TornadoHandler get_response ")

        response = self.start_response(request)

        # ### Handle the Future
        # Always return Futures back the IOLoop without further processing.
        if is_future(response):
            logger.debug("response is TracebackFuture, return it")
            return response

        # Not a future, finish Django response processing
        # and return it
        return self.finish_response(request, response)
    # get_response()

# TornadoHandler


def get_script_name(t_req):
    """
    Returns the equivalent of the HTTP request's SCRIPT_NAME header
    variable. If Apache mod_rewrite has been used, returns what would have been
    the script name prior to any rewriting (so it's the script name as seen
    from the client's perspective), unless the FORCE_SCRIPT_NAME setting is
    set (to anything).
    """
    if settings.FORCE_SCRIPT_NAME is not None:
        return force_text(settings.FORCE_SCRIPT_NAME)

    # If Apache's mod_rewrite had a whack at the URL, Apache set either
    # SCRIPT_URL or REDIRECT_URL to the full resource URL before applying any
    # rewrites. Unfortunately not every Web server (lighttpd!) passes this
    # information through all the time, so FORCE_SCRIPT_NAME, above, is still
    # needed.
    script_url = t_req.headers.get('SCRIPT_URL', '')
    if not script_url:
        script_url = t_req.headers.get('REDIRECT_URL', '')

    if script_url:
        path_info = t_req.headers.get('PATH_INFO', '')
        script_name = script_url[:-len(path_info)]
    else:
        script_name = t_req.headers.get('SCRIPT_NAME', '')

    # It'd be better to implement URI-to-IRI decoding, see #19508.
    # return script_name.decode(UTF_8)
    return script_name

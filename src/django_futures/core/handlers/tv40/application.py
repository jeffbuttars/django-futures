"""
``application.py``
=======================================

`django_futures.core.handlers.tv40.application.py`
"""

import logging
# logger = logging.getLogger('django.request')
logger = logging.getLogger('django.debug')

import tornado.web
from tornado.concurrent import TracebackFuture

from django.conf import settings
from django.http.response import StreamingHttpResponse

from django_futures.core.handlers.df_staticfiles import StaticFilesHandler
from django_futures.core.handlers.df import TornadoHandler


class DjangoFuturesRequestHandler(tornado.web.RequestHandler):
    """
    A Tornado Request Handler for Tornado to interface with.
    """

    def __init__(self, application, request, **kwargs):
        # logger.debug(("DjangoFuturesRequestHandler::__init__() "
        #               "application: %s, request: %s, kwargs: %s"),
        #              application, request, kwargs)
        logger.debug(("DjangoFuturesRequestHandler::__init__() "))
        super(DjangoFuturesRequestHandler, self).__init__(application, request, **kwargs)

        if application.settings['staticfiles']:
            self._dj_handler_class = StaticFilesHandler
        else:
            self._dj_handler_class = TornadoHandler

        self._dj_handler = self._dj_handler_class(self)
#     # __init__()

    def prepare(self):
        """
        We do a little funny buisiness here, we set the 
        reqeust.method to 'django_handle_request' since we've
        bipassed the url lookup. We set it back when it's called.
        Normally, this would be an HTTP method mapped to a handler
        method  like get() or post(). But we'll Django figure out 
        the method stuff, so we don't care.
        """
        logger.debug("DjangoFuturesRequestHandler::prepare() ")
        self.request.orig_method = self.request.method
        self.request.method = 'django_handle_request'
    # prepare()

    def django_handle_request(self, *args, **kwargs):
        """todo: Docstring for django_handle_request
        """

        # logger.debug(("DjangoFuturesRequestHandler::django_handle_request()"
        #               " args: %s, kwargs: %s"),
        #              args, kwargs)
        logger.debug("DjangoFuturesRequestHandler::django_handle_request()")

        # Set the method back to what it was before the call
        self.request.method = self.request.orig_method

        # Now use the Django handler to run the request through Django
        logger.debug(("DjangoFuturesRequestHandler::django_handle_request()"
                      "calling tornadoHandler"))
        response = self._dj_handler(self.request, self.django_finish_request)

        # logger.debug(("DjangoFuturesRequestHandler::django_handle_request()"
        #               "response: %s"), response)
        logger.debug(("DjangoFuturesRequestHandler::django_handle_request()"
                      "have a response: %s"), dir(response))

        if isinstance(response, TracebackFuture):
            # The request is finished being processed. Return the Future
            # to Tornado which will handle the Future until it's completed.
            logger.debug(("DjangoFuturesRequestHandler::django_handle_request()"
                          "Got a future"))
            return response

        # The _dj_handler will call django_finish_request if it finishes before
        # we return back to here..
        # Right now we're using callbacks, we should look into replacing those
        # with Futures.
        logger.debug(("DjangoFuturesRequestHandler::django_handle_request()"
                      "has a response: %s"), response is not None)
        self.django_finish_request(response)
    # django_handle_request()

    def django_finish_request(self, response):
        logger.debug("DjangoFuturesRequestHandler::django_finish_request")
        # Django has finished with the request and now we
        # need to make the response friendly for Tornado
        # and write it to the network.

        if not response:
            logger.debug(
                "DjangoFuturesRequestHandler::django_finish_request no response to process")
            self.request.finish()
            return

        response._handler_class = self._dj_handler_class

        # Update the status with the Django staus
        # logger.debug(("DjangoFuturesRequestHandler::django_finish_request()"
        #               "setting status tornadoHandler"))
        self.set_status(response.status_code, response.reason_phrase)

        # Update headers with the Django headers
        for k, v in response.items():
            logger.debug(("DjangoFuturesRequestHandler::django_finish_request()"
                          "setting header %s: %s") % (k, v))
            self.set_header(str(k), str(v))
        # end for k, v in response.items

        # Write the Django response's cookies to the tornado response
        # headers
        for c in response.cookies.values():
            self.add_header(
                str('Set-Cookie'), str(c.output(header=''))
            )

        try:
            logger.debug("DjangoFuturesRequestHandler::django_finish_request() writing content")
            # logger.debug("%s", response.content)
            self.write(response.content)
        except AttributeError:
            logger.debug("DjangoFuturesRequestHandler::django_finish_request() streaming content")
            for cont in response.streaming_content:
                self.write(cont)
                self.flush()
            # end for cont in response

        self.finish()
        logger.debug("DjangoFuturesRequestHandler::django_finish_request() finished")
    # django_finish_request()
# # DjangoFuturesRequestHandler


class _DjangoRequestDispatcher(tornado.web._RequestDispatcher):
    """Docstring for _DjangoRequestDispatcher """

    def __init__(self, application, connection):
        logger.debug(
            "_DjangoRequestDispatcher:__init__() application %s, connection %s",
            application,
            connection)
        super(_DjangoRequestDispatcher, self).__init__(
            application, connection)

    def _find_handler(self):
        """
        No need to 'find' a handler. We always call our Django
        handler. Django will map it's own URIs to it's views.
        """
        logger.debug("_DjangoRequestDispatcher:_find_handler()")
        self.handler_class = DjangoFuturesRequestHandler
        self.handler_kwargs = {}

    # def headers_received(self, start_line, headers):
    #     logger.debug("_DjangoRequestDispatcher:headers_received()")
    #     # logger.debug("_DjangoRequestDispatcher:headers_received() start_line: %s, headers: %s",
    #     #             start_line, headers)
    #     return super(_DjangoRequestDispatcher, self).headers_received(start_line, headers)

    # def set_request(self, request):
    #     # logger.debug(
    #     #     "_DjangoRequestDispatcher:set_request() request: %s", request)
    #     logger.debug("_DjangoRequestDispatcher:set_request()")
    #     super(_DjangoRequestDispatcher, self).set_request(request)

    # def data_received(self, data):
    #     # logger.debug("_DjangoRequestDispatcher:data_received() data: %s", data)
    #     logger.debug("_DjangoRequestDispatcher:data_received() ")
    #     return super(_DjangoRequestDispatcher, self).data_received(data)

    # def execute(self):
    #     """todo: Docstring for execute
    #     :return:
    #     :rtype:
    #     """
    #     logger.debug("_DjangoRequestDispatcher:execute()")
    #     return super(_DjangoRequestDispatcher, self).execute()
    # # execute()
# _DjangoRequestDispatcher


class DjangoApplication(tornado.web.Application):

    def __init__(self, *args, **kwargs):
        """todo: to be defined
        
        :param \*args: arg description
        :type \*args: type description
        :param \*\*kwargs: arg description
        :type \*\*kwargs: type description
        """
        logger.debug("args: %s, kwargs: %s",
                     args, kwargs)

        logger.debug(" static_url: %s, static_path: %s",
                     settings.STATIC_URL, settings.STATIC_ROOT)

        if kwargs.pop('static', None):
            kwargs['static_url_prefix'] = settings.STATIC_URL
            kwargs['static_path'] = settings.STATIC_ROOT

        super(DjangoApplication, self).__init__(
            [],
            *args,
            **kwargs)
    # __init__()

    def __call__(self, request):
        logger.debug("Legacy interface")
        raise NotImplementedError

    def start_request(self, connection):
        logger.debug("connection %s", connection)
        # Modern HTTPServer interface
        return _DjangoRequestDispatcher(self, connection)
# DjangoApplication

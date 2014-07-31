"""
``application.py``
=======================================

`django_futures.core.handlers.tv32.application.py`
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
        logger.debug(("DjangoFuturesRequestHandler::__init__() "
                      "application: %s, request: %s, kwargs: %s"),
                     application, request, kwargs)
        super(DjangoFuturesRequestHandler, self).__init__(application, request, **kwargs)

        if application.settings['staticfiles']:
            self._dj_handler_class = StaticFilesHandler
        else:
            self._dj_handler_class = TornadoHandler

        self._dj_handler = self._dj_handler_class(self)
    # __init__()

    def _execute_method(self):
        logger.debug("DjangoFuturesRequestHandler::_execute_method")
        if not self._finished:
            self._when_complete(self.django_handle_request(*self.path_args, **self.path_kwargs),
                                self._execute_finish)
    # def _execute_finish(self):
    #     logger.debug("DjangoFuturesRequestHandler::_execute_finish")
    #     super(DjangoFuturesRequestHandler, self)._execute_finish()
    # # _execute_finish()


    # def _execute(self, transforms, *args, **kwargs):
    #     logger.debug("DjangoFuturesRequestHandler::_execute transforms:%s, args:%s, kwargs:%s",
    #                 transforms, args, kwargs)
    #     super(DjangoFuturesRequestHandler, self)._execute(transforms, *args, **kwargs)
    # # _execute()

    # def _when_complete(self, result, callback):
    #     """Intercept the _when_complete calls
    #     """
    #     logger.debug("DjangoFuturesRequestHandler::_when_complete")
    #     super(DjangoFuturesRequestHandler, self)._when_complete(result, callback)
    # # _when_complete()

    # def _execute_finish(self):
    #     logger.debug("DjangoFuturesRequestHandler::_execute_finish")
    #     super(DjangoFuturesRequestHandler, self)._execute_finish()
    # # _execute_finish()

    # def on_finish(self):
    #     logger.debug("DjangoFuturesRequestHandler::on_finish")
    #     pass
    # # on_finish()

    # def finish(self, chunk=None):
    #     logger.debug("DjangoFuturesRequestHandler::finish")
    #     super(DjangoFuturesRequestHandler, self).finish(chunk)
    # # finish()

    def django_handle_request(self, *args, **kwargs):
        """todo: Docstring for django_handle_request

        :param \*args: arg description
        :type \*args: type description
        :param \*\*kwargs: arg description
        :type \*\*kwargs: type description
        :return:
        :rtype:
        """

        logger.debug(("DjangoFuturesRequestHandler::django_handle_request()"
                      " args: %s, kwargs: %s"),
                     args, kwargs)

        # Now use the Django handler to run the request through Django
        logger.debug(("DjangoFuturesRequestHandler::django_handle_request()"
                      "calling tornadoHandler"))
        response = self._dj_handler(self.request, self.django_finish_request)

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
        # logger.debug(("DjangoFuturesRequestHandler::django_finish_request()"
        #               "copying headers"))

        for k, v in response.items():
            logger.debug(("DjangoFuturesRequestHandler::django_finish_request()"
                          "setting header %s: %s") % (k, v))
            self.set_header(str(k), str(v))
        # end for k, v in response.items

        # Write the Django response's cookies to the tornado response
        # headers
        for c in response.cookies.values():
            # logger.debug(("DjangoFuturesRequestHandler::django_finish_request()"
            #             "adding COOKIE %s", c))
            self.add_header(
                str('Set-Cookie'), str(c.output(header=''))
            )

        try:
            logger.debug("DjangoFuturesRequestHandler::django_finish_request() writing content")
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
# DjangoFuturesRequestHandler


# Looks like we'll need our own version of the tornado web Application class
# to do this well.
# Sat Jun  7 19:36:09 2014
class DjangoApplication(tornado.web.Application):

    def __init__(self, *args, **kwargs):
        """todo: to be defined
        
        :param \*args: arg description
        :type \*args: type description
        :param \*\*kwargs: arg description
        :type \*\*kwargs: type description
        """
        logger.debug("DjangoApplication::__init__() args: %s, kwargs: %s",
                     args, kwargs)

        # Add our Django handler
        self._django_handlers = [
            (r'.*', DjangoFuturesRequestHandler),
        ]

        logger.debug("DjangoApplication::__init__() static_url: %s, static_path: %s",
                     settings.STATIC_URL, settings.STATIC_ROOT)

        if kwargs.pop('static', None):
            kwargs['static_url_prefix'] = settings.STATIC_URL
            kwargs['static_path'] = settings.STATIC_ROOT
                
        super(DjangoApplication, self).__init__(
            self._django_handlers,
            *args,
            **kwargs)
    # __init__()
# DjangoApplication

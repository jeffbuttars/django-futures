"""
``django_futures.decorators.py``

``decorators.py`` -- Simplifiy Asynchronous Code
================================================

We have the following decorators available:

* ``coroutine`` Used to create views that support asynchronous behavior
* ``ttask`` Creates function or method that will be run at a later time on the same process.
* ``ctask`` Same as ``ttask`` except the task is also a coroutine

"""

import logging
logger = logging.getLogger('django')

import functools
from tornado.ioloop import IOLoop
from tornado.gen import coroutine


class django_coroutine(object):
    """
    *Not Implemented!*

    The behavior of ``django_coroutine`` is the same as that of ``coroutine``
    with the exception that Django responses can be returned as in a normal
    Django view. For example:

    .. code-block:: python

        from django_futures.decorators import django_coroutine
        from django_futures.http_client import HttpClient
        from django.views.generic import TemplateView
        from core.views import BaseTemplateView

        class TestAsyncHttpClient(BaseTemplateView):

            template_name = "test_async_httpclient.html"

            @django_coroutine
            def get(self, request):
                # Here we make an asynchrounous web call using the asynchrounous
                # aware web client available with Django Futures

                # Go and grab a web page asynchronously
                http_client = HttpClient()

                res = yield http_client.get('http://yahoo.com')
                ctx = {
                    'web_response': res
                }

                # Build a Django response
                myres = super(TestAsyncHttpClient, self).get(request, **ctx)

                # In an asynchronous view, we must render a Django response using
                # the render() method of the request object.
                return myres
            # get()
        # TestAsyncHttpClient
    """

    def __init__(self):
        """todo: to be defined """
        raise NotImplementedError
    # __init__()

    def __call__(self, view):
        """todo: Docstring for __call__
        
        :param view: arg description
        :type view: type description
        :return:
        :rtype:
        """
        raise NotImplementedError
    # __call__()
# django_coroutine

class ttask(object):
    """
    Run a task as a tornado callback. Great for async background code.
    If tornado is not running, then things are run synchronously.

    Example:
    We define the task ``send_signup_confirmation()`` using the ``@ttask()`` decorator.
    When the task is called on line 21 the call will return imediately and the task
    will run at a later time after the view has finished.

    .. code-block:: python
        :linenos:

        from ttasks.decorators import ttask

        @ttask()
        def send_signup_confirmation(req, emsg):

            url = "https://api.myemailserver.example.com
            hc = HTTPClient()
            resp = hc.fetch(
                url,
                method='POST',
                body=tornado.escape.json_encode(emsg),
            )

            logger.debug("email result: %s", resp)


        def a_view(request):
            # Process some stuff
            ...
            # Call the task
            send_signup_confirmation(request)

            # create and return a response
            ...
            return response


    """
    __name__ = "ttask"

    def __init__(self, *args, **kwargs):
        """When this gets more advance we can use this to setup
        more complicated features such as distributting to a true
        task service.

        :param *args: arg description
        :type *args: type description
        :param deadline: always delay this task by 'deadline'. This will be given to the
        add_timeout() method on the current IOLoop.
        :type deadline: float, seconds to delay this task by.
        :param **kwargs: arg description
        :type **kwargs: type description
        """
        self._args = args
        self._kwargs = kwargs

        self._deadline = kwargs.get('deadline')
    #__init__()

    def __call__(self, func):
        """todo: Docstring for __call__

        :param *args: arg description
        :type *args: type description
        :param **kwargs: arg description
        :type **kwargs: type description
        :return:
        :rtype:
        """

        logger.debug(
            "ttask decorate, IOLoop is running? %s", IOLoop.current()._running)

        if not IOLoop.current()._running:
            logger.debug("ttask running %s sync", func)

            @functools.wraps(func)
            def sync_decorated(*args, **kwargs):
                """Run the function synchronously
                """
                return IOLoop.current().run_sync(
                    functools.partial(func, *args, **kwargs))
            #sync_decorated()

            return sync_decorated

        logger.debug("ttask running %s async", func)

        if self._deadline:
            @functools.wraps(func)
            def deadline_decorated(*args, **kwargs):
                """Schedule the task as a timeout.
                """
                return IOLoop.current().add_timeout(
                    self._deadline,
                    functools.partial(func, *args, **kwargs)
                )
            # deadline_decorated()

            return deadline_decorated

        @functools.wraps(func)
        def decorated(*args, **kwargs):
            """todo: Docstring for decorated
            """
            # logger.debug(
            #     "Adding ttask %s to callback Q, args: %s, kwargs: %s", func, args, kwargs)
            return IOLoop.current().add_callback(func, *args, **kwargs)
        # decorated()

        return decorated
    #__call__()
# ttask


class ctask(object):
    """
    Creates a :py:class:`ttask` using a method/function that is also a Tornado coroutine.

    This is a convenience decorator and is equivelant to decorting a function with
    @coroutine and @ttask()

    :py:class:`ctask` will run the coroutine on the decorated function first
    then decorate it with :py:class:`ttask`.

    For example, use this if you have a task that needs to make asynchronous http client
    calls.
    """
    __name__ = "ctask"

    def __init__(self, *args, **kwargs):
        """When this gets more advance we can use this to setup
        more complicated features such as distributting to a true
        task service.

        :param *args: arg description
        :type *args: type description
        :param **kwargs: arg description
        :type **kwargs: type description
        """
        self._args = args
        self._kwargs = kwargs
    #__init__()

    def __call__(self, func):
        tt = ttask(*self._args, **self._kwargs)
        return tt(coroutine(func))
    #__call__()
#ctask

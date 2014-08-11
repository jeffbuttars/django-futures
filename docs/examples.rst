Examples
========

Here is a simple asynchronous view that fetches a web page.

.. code-block:: python

    from tornado import gen
    from django_futures.http_client import HttpClient
    from django.views.generic import TemplateView
    from core.views import BaseTemplateView

    class TestAsyncHttpClient(BaseTemplateView):

        template_name = "test_async_httpclient.html"
        num_client_options = (1, 5, 10, 25, 50, 100)

        @gen.coroutine
        def get(self, request):
            """
            Here we make an asynchrounous web call using the asynchrounous
            aware web client available with Django Futures
            """

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
            request.render(myres)
        # get()
    # TestAsyncHttpClient

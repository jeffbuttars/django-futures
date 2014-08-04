import tornado.testing
import tornado.web


from django_futures.http_client import HttpClient


class ClientTestHandler(tornado.web.RequestHandler):

    SUPPORTED_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD']

    def get(self):
        """todo: Docstring for get

        :param request: arg description
        :type request: type description
        :return:
        :rtype:
        """

        pass
    # get()

    def post(self):
        """todo: Docstring for post
        
        :param request: arg description
        :type request: type description
        :return:
        :rtype:
        """
    
        pass
    # post()

    def delete(self):
        """todo: Docstring for delete
        
        :param request: arg description
        :type request: type description
        :return:
        :rtype:
        """
    
        pass
    # delete()

    def put(self):
        """todo: Docstring for put
        
        :param request: arg description
        :type request: type description
        :return:
        :rtype:
        """
    
        pass
    # put()

    def head(self):
        """todo: Docstring for head
        
        :param request: arg description
        :type request: type description
        :return:
        :rtype:
        """
    
        pass
    # head()
# ClientTestHandler


class TestHttpMethods(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        app = tornado.web.Appliction(
            [
            ]
        )

        return app
    # get_app()
# TestHttpMethods

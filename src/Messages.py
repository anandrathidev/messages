import json
import logging
import uuid
from wsgiref import simple_server
import datetime
import falcon
import requests
import MessLogger
import MessConnections
from sqlalchemy.sql import text

class StorageEngine(object):
    def __init__(self,logger):
        self.messConnections = MessConnections.MessConnections()
        self.dbcon = self.messConnections.sqlConnect()
        self.logger = logger
        try: 
            self.statement = text("""INSERT INTO messages(ts, ots, id, oppid, status, message,  other) VALUES(:ts, :ots,:id, :oppid, :status, :message,  :other)""") 
        except BaseException as e:
            self.logger.exception(e)
            raise e
    def get_things(self, marker, limit):
        return [{'id': str(uuid.uuid4()), 'color': 'green'}]

    def addthingO(self, ts, ots, id, oppid, status, message,  other):
        try: 
            self.logger.info("insert {}, {}, {}, {}, {}, {}, {}".format(ts, ots, id, oppid, status, message, other) )
            print("insert {}, {}, {}, {}, {}, {}, {}".format(ts, ots, id, oppid, status, message, other))
            self.dbcon.execute(self.statement, ts, ots, id, oppid, status, message, other)
        except BaseException as e:
            self.logger.exception(e)
            raise e
    def addthing(self, doc):
        try: 
            #self.logger.info("insert {}, {}, {}, {}, {}, {}, {}".format(**doc) )
            self.dbcon.execute(self.statement, **doc)
        except BaseException as e:
            self.logger.exception(e)
            raise e

class StorageError(Exception):

    @staticmethod
    def handle(ex, req, resp, params):
        description = ('Sorry, couldn\'t write your thing to the '
                       'database. It worked on my box.')

        raise falcon.HTTPError(falcon.HTTP_725,
                               'Database Error',
                               description)


class SinkAdapter(object):

    engines = {
        'ddg': 'https://duckduckgo.com',
        'y': 'https://search.yahoo.com/search',
    }

    def __call__(self, req, resp, engine):
        url = self.engines[engine]
        params = {'q': req.get_param('q', True)}
        result = requests.get(url, params=params)

        resp.status = str(result.status_code) + ' ' + result.reason
        resp.content_type = result.headers['content-type']
        resp.body = result.text


class AuthMiddleware(object):

    def process_request(self, req, resp):
        token = req.get_header('Authorization')
        account_id = req.get_header('Account-ID')

        challenges = ['Token type="Fernet"']

        if token is None:
            description = ('Please provide an auth token '
                           'as part of the request.')

            raise falcon.HTTPUnauthorized('Auth token required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

        if not self._token_is_valid(token, account_id):
            description = ('The provided auth token is not valid. '
                           'Please request a new token and try again.')

            raise falcon.HTTPUnauthorized('Authentication required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

    def _token_is_valid(self, token, account_id):
        return True  # Suuuuuure it's valid...


class RequireJSON(object):

    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                'This API only supports responses encoded as JSON.',
                href='http://docs.examples.com/api/json')

        if req.method in ('POST', 'PUT'):
            if 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    'This API only supports requests encoded as JSON.',
                    href='http://docs.examples.com/api/json')


class JSONTranslator(object):

    def process_request(self, req, resp):
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['doc'] = json.loads(body.decode('utf-8'))
            #print("message={0}".format(req.context['doc']))
        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            resp.body = json.dumps({"result":"OK"})
            return
        resp.body = json.dumps(req.context['result'])


def max_body(limit):

    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = ('The size of the request is too large. The body must not '
                   'exceed ' + str(limit) + ' bytes in length.')

            raise falcon.HTTPRequestEntityTooLarge(
                'Request body is too large', msg)

    return hook


class Messages(object):

    def __init__(self, db, logger):
        self.db = db
        self.logger = logger
    def on_get(self, req, resp, user_id):
        marker = req.get_param('marker') or ''
        limit = req.get_param_as_int('limit') or 50

        try:
            #result = self.db.get_things(marker, limit)
            pass 
        except Exception as ex:
            self.logger.error(ex)

            description = ('Aliens have attacked our base! We will '
                           'be back as soon as we fight them off. '
                           'We appreciate your patience.')

            raise falcon.HTTPServiceUnavailable(
                'Service Outage',
                description,
                30)

        # An alternative way of doing DRY serialization would be to
        # create a custom class that inherits from falcon.Request. This
        # class could, for example, have an additional 'doc' property
        # that would serialize to JSON under the covers.
        req.context['result'] = result

        resp.set_header('Powered-By', 'Falcon')
        resp.status = falcon.HTTP_200

    @falcon.before(max_body(4 * 1024))
    def on_post(self, req, resp, user_id):
        try:
            doc = req.context['doc']
            import pdb
            #pdb.set_trace()
            doc["ots"] = datetime.datetime.now() 
            self.db.addthing(doc)
        except KeyError as ex:
            print(str(ex))
            self.logger.error(ex)
            raise falcon.HTTPBadRequest(
                'Missing thing',
                'A thing must be submitted in the request body.')
        except Exception as ex:
            print(str(ex))
            self.logger.error(ex)
            raise ex
        except BaseException as ex:
            print(str(ex))
            self.logger.error(ex)
            raise ex

        resp.status = falcon.HTTP_201
        #resp.location = '/%s/things/%s' % (user_id, proper_thing['id'])
        resp.location = '/%s/messages/' % (user_id )


# Configure your WSGI server to load "things.app" (app is a WSGI callable)
app = falcon.API(middleware=[
    AuthMiddleware(),
    RequireJSON(),
    JSONTranslator(),
])

logger = MessLogger.GetLogger()
db = StorageEngine(logger)
things = Messages(db,logger)
app.add_route('/{user_id}/messages', things)

# If a responder ever raised an instance of StorageError, pass control to
# the given handler.
app.add_error_handler(StorageError, StorageError.handle)

# Proxy some things to another service; this example shows how you might
# send parts of an API off to a legacy system that hasn't been upgraded
# yet, or perhaps is a single cluster that all data centers have to share.
sink = SinkAdapter()
app.add_sink(sink, r'/search/(?P<engine>ddg|y)\Z')

# Useful for debugging problems in your API; works with pdb.set_trace(). You
# can also use Gunicorn to host your app. Gunicorn can be configured to
# auto-restart workers when it detects a code change, and it also works
# with pdb.
if __name__ == '__main__':
    httpd = simple_server.make_server('0.0.0.0', 8000, app)
    httpd.serve_forever()
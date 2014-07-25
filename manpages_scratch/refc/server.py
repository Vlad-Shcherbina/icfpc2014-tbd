import logging

import tornado
import tornado.ioloop
import tornado.web

log = logging.getLogger(__name__)

if __name__ == "__main__":
  logging.basicConfig(level=logging.WARNING)
  log.setLevel(logging.DEBUG)
  application = tornado.web.Application([ 
                  (r'/(.*)',tornado.web.StaticFileHandler,{'path':"game/"}) 
                ], debug=True)
  application.listen(62014)
  log.debug('Listening to 62014')
  tornado.ioloop.IOLoop.instance().start()

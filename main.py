#!/usr/bin/env python
# author: Jesse Shieh (jesse.shieh@gmail.com)

import logging
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

class BaseHandler(webapp.RequestHandler):
  template_values = {
    "title": "Jesse Shieh",
    "meta_description": "Stalking Jesse Shieh? Try jesseshieh.com",
    "meta_keywords": "Jesse Shieh"
    }

  def render(self, template_name):
    path = os.path.join(os.path.dirname(__file__), template_name)
    self.response.out.write(template.render(path, self.template_values))

class MainHandler(BaseHandler):
  def get(self):
    self.render("main.html")

class ResumeHandler(BaseHandler):
  def get(self):
    self.render("resume.html")

class ProjectsHandler(BaseHandler):
  def get(self):
    self.render("projects.html")

class ContactHandler(BaseHandler):
  def get(self):
    self.render("contact.html")

def main():
  logging.getLogger().setLevel(logging.DEBUG)
  application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/resume', ResumeHandler),
                                        ('/projects', ProjectsHandler),
                                        ('/contact', ContactHandler),
                                        ],
                                       debug=True)
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()

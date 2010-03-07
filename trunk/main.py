#!/usr/bin/env python
# author: Jesse Shieh (jesse.shieh@gmail.com)

import Cookie
import logging
import os
import re
from google.appengine.api import mail
from google.appengine.api.labs.taskqueue import Task
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

class BaseHandler(webapp.RequestHandler):
  template_values = {
    "title": "Jesse Shieh",
    "meta_description": "Looking for Jesse Shieh? Try jesseshieh.com",
    "meta_keywords": "Jesse Shieh, Resume, Software Engineer, Engineering Manager"
    }

  def add_template_value(self, key, value):
    """
    adds a new entry in the template dictionary
    """
    self.template_values[key] = value

  def render(self, template_name):
    """
    renders and writes the response given the template name
    """
    self.add_template_value("template_name", template_name)
    path = os.path.join(os.path.dirname(__file__), "chrome.html")
    self.response.out.write(template.render(path, self.template_values))

  def html_escape(self, text):
    """Produce entities within text."""
    html_escape_table = {
          "&": "&amp;",
          '"': "&quot;",
          "'": "&apos;",
          ">": "&gt;",
          "<": "&lt;",
          }
    return "".join(html_escape_table.get(c,c) for c in text)

  def maybe_show_flash(self):
    """
    Most get() methods will have this at the top to show the flash
    message if it exists and clear it
    """
    if self.has_flash():
      self.add_template_value("flash", self.get_flash())
      self.clear_flash()

    if self.has_error():
      self.add_template_value("error", self.get_error())
      self.clear_error()

  def add_flash(self, message):
    """
    Send a flash message that shows only once to the user
    """
    cookie = Cookie.SimpleCookie()
    cookie["flash"] = message
    cookie["flash"]["Path"] = "/"

    h = re.compile('^Set-Cookie:').sub('', cookie.output(), count=1)
    self.response.headers.add_header('Set-Cookie', str(h))

  def add_error(self, message):
    """
    Send a flash message that shows only once to the user
    """
    cookie = Cookie.SimpleCookie()
    cookie["error"] = message
    cookie["error"]["Path"] = "/"

    h = re.compile('^Set-Cookie:').sub('', cookie.output(), count=1)
    self.response.headers.add_header('Set-Cookie', str(h))

  def add_extra_data(self, message):
    """
    Send a flash message that shows only once to the user
    """
    cookie = Cookie.SimpleCookie()
    cookie["extra_data"] = message
    cookie["extra_data"]["Path"] = "/"

    h = re.compile('^Set-Cookie:').sub('', cookie.output(), count=1)
    self.response.headers.add_header('Set-Cookie', str(h))

  def clear_flash(self):
    self.add_flash("")

  def clear_error(self):
    self.add_error("")

  def clear_extra_data(self):
    self.add_extra_data("")

  def has_flash(self):
    return self.request.cookies.has_key("flash")

  def has_error(self):
    return self.request.cookies.has_key("error")

  def has_extra_data(self):
    return self.request.cookies.has_key("extra_data")

  def get_flash(self):
    if self.has_flash():
      return self.request.cookies["flash"].strip('\'"')
    else:
      return None

  def get_error(self):
    if self.has_error():
      return self.request.cookies["error"].strip('\'"')
    else:
      return None

  def get_extra_data(self):
    if self.has_extra_data():
      return self.request.cookies["extra_data"].strip('\'"')
    else:
      return None


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
    self.maybe_show_flash()
    self.render("contact.html")

  def post(self):
    name = self.request.get("name")
    email = self.request.get("email")
    message = self.request.get("message")

    logging.debug("adding message to queue from %s (%s): %s" % (name, email, message))
    task = Task(url='/tasks/email/me', params={
        'name': name,
        'email': email,
        'message': message,
        })
    task.add('email-throttle')

    self.add_flash("Thanks %s.  Message sent. I promise to reply within 24 hours." % self.html_escape(name))
    self.redirect("/contact")

class EmailMeWorker(BaseHandler):
  def post(self):
    name = self.request.get('name')
    email = self.request.get('email')
    message = self.request.get('message')

    logging.debug("sending message from %s (%s): %s" % (name, email, message))
    mail.send_mail(sender="jesse.shieh@gmail.com",
                   to="jesse.shieh@gmail.com",
                   subject="Message from %s (%s)" % (name, email),
                   body="%s (%s): %s" % (name, email, message))

def main():
  logging.getLogger().setLevel(logging.DEBUG)
  application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/resume', ResumeHandler),
                                        ('/projects', ProjectsHandler),
                                        ('/contact', ContactHandler),

                                        # taskqueue tasks
                                        ("/tasks/email/me", EmailMeWorker),
                                        ],
                                       debug=True)
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()

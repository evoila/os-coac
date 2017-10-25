import logging
import json

class ProjectTemplate(object):

  def __init__(self, name, domain, description, enable, properties = {}):
    self.name = name
    self.domain = domain
    self.description = description
    self.enable = enable
    self.properties = properties

  def __str__(self):
    return json.dumps(self.__dict__)

class UserAssignment(object):

  def __init__(self, user_domain, user_name, project_domain, project_name, role):
    self.user_domain = user_domain
    self.user_name = user_name
    self.project_domain = project_domain
    self.project_name = project_name
    self.role = role

  def __str__(self):
    return json.dumps(self.__dict__)

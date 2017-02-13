import logging
import json

from jinja2 import Template

class ProjectTemplate:

  LOG = logging.getLogger(__name__)

  def __init__(self, name, project_name, domain, description, enable, properties, users):
    self.name = name
    self.project_name = project_name
    self.domain = domain
    self.description = description
    self.enable = enable
    self.properties = properties
    self.users = users

  def generate(self, project_config):
    domain_template = Template(self.domain)
    name_template = Template(self.project_name)
    description_template = Template(self.description)

    data = {
      "domain": domain_template.render(project = project_config),
      "name": name_template.render(project = project_config),
      "description": description_template.render(project = project_config),
      "enable": project_config.enable if hasattr(project_config, 'enable') else self.enable,
      "properties": {},
      "users": [],
    }

    for property, value in self.properties.items():
      template = Template(value)
      data['properties'][property] = template.render(project = project_config)

    for user in self.users:
      data['users'].append(user.__dict__)    

    return data

class UserAssignment:

  LOG = logging.getLogger(__name__)
 
  def __init__(self, user_domain, user_name, role):
    self.user_domain = user_domain
    self.user_name = user_name
    self.role = role

  def __str__(self):
    return json.dump(self)

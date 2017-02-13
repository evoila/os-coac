import re
import yaml
import logging

from os_coac.project.model import ProjectTemplate, UserAssignment
from os_coac import ResourceManager
from oslo_config import cfg
from oslo_config import types

project_group = cfg.OptGroup(name='projects',
                             title='Project options')

project_opts = [
  cfg.StrOpt(name='resource_file',
             default='/etc/os-coac/project.yaml',
             help='Path to the file containing project configuration.'),
]

CONF = cfg.CONF
CONF.register_group(project_group)
CONF.register_opts(project_opts, group=project_group)

class ProjectResourceManager(ResourceManager):
  
  LOG = logging.getLogger(__name__)

  __project_templates = {}
  __project_configs = []
  __regex_patterns = {}

  def __init__(self):
    with open(CONF.projects.resource_file, 'r') as stream:
      self.data = yaml.load(stream)

    for name in self.data['projects']['templates']:
      user_configs = self.data['projects']['templates'][name]['users']
      users = []
      for config in user_configs:
        users.append(UserAssignment(config['user_domain'], config['user_name'], config['role']))

      self.__project_templates[name] = ProjectTemplate(
        name         = name,
        domain       = self.data['projects']['templates'][name]['domain'],
        project_name = self.data['projects']['templates'][name]['name'],
        description  = self.data['projects']['templates'][name]['description'],
        enable       = self.data['projects']['templates'][name]['enable'],
        properties   = self.data['projects']['templates'][name]['properties'],
        users        = users,
      )
      self.LOG.info('Created template: {}'.format(name))

    self.__regex_patterns = self.data['projects']['regex']
    self.__project_configs = self.data['projects']['configs']

    if not 'default' in self.__project_templates:
      raise ValueError('No project template with name "default" defined.')

    for project_template in self.__project_templates:
      self.__validate_project_template(project_template)

    for project_config in self.__project_configs:
      self.__validate_project_config(project_config)

  def __validate_project_template(self, project_template):
    pass

  def __validate_project_config(self, project_config):
    if not 'template' in project_config:
      project_config['template'] = 'default'
    elif not project_config['template'] in self.__project_templates:
      raise ValueError(
        'Project Config {}: Template {} unknown.'.format(
          project_config['name'],
          project_config['template']
        )
      )

    for field, value in project_config.items():
      if field in self.__regex_patterns:
        pattern = self.__regex_patterns[field]
        result = re.match(pattern, value)
        if not result:
          raise ValueError(
            'Project {}: Value "{}" in field "{}" does not match pattern "{}"'.format(
              project_config['name'],
              value,
              field,
              pattern
            )
          )

  def synchronize(self):
    projects = []
    for project_config in self.__project_configs:
      template = self.__project_templates[project_config['template']]  
      project = template.generate(project_config)
      projects.append(project)
      self.LOG.debug('Generated project from template "{}": {}'.format(project_config['template'], project))
    self.LOG.info('Generated projects: {}'.format(len(projects)))

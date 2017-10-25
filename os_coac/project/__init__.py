import re
import yaml
import logging

from jinja2 import Template
from os_coac.project.model import ProjectTemplate, UserAssignment
from os_coac import ResourceManager
from os_coac.hook import Hook
from oslo_config import cfg
from oslo_config import types

group = cfg.OptGroup(name='projects',
                           title='Project options')

opts = [
  cfg.StrOpt(name='resource_file',
             default='/etc/os-coac/project.yaml',
             help='Path to the file containing project configuration.'),
]

CONF = cfg.CONF
CONF.register_group(group)
CONF.register_opts(opts, group=group)

class ProjectResourceManager(ResourceManager):
  
  LOG = logging.getLogger(__name__)

  __templates = {}
  __user_assignments = {}
  __configs = []
  __regex = {}
  __hooks = {}

  def __init__(self):
    pass

  def __load(self):

    # Read resource file and parse YAML
    with open(CONF.projects.resource_file, 'r') as stream:
      self.data = yaml.load(stream)

    for name in self.data['projects']['templates']:

      # Generate ProjecteTemplate 
      template = ProjectTemplate(
        name         = self.data['projects']['templates'][name]['name'],
        domain       = self.data['projects']['templates'][name]['domain'],
        description  = self.data['projects']['templates'][name]['description'],
        enable       = self.data['projects']['templates'][name]['enable'],
        properties   = self.data['projects']['templates'][name]['properties'],
      )
      self.__templates[name] = template
      self.LOG.debug('Created template: {}'.format(name))
  
      # Generate UserAssignment objects for current ProjectTemplate
      user_configs = self.data['projects']['templates'][name]['users']
      for config in user_configs:
        user_assignment = UserAssignment(
          config['user_domain'],
	  config['user_name'],
          template.domain,
	  template.name,
          config['role']
        )
        self.__user_assignments[name] = user_assignment
        self.LOG.debug('Created user assignment for user: {}/{}'.format(user_assignment.user_domain, user_assignment.user_name))

      # Generate Hook objects for current ProjectTemplate
      hook_configs = self.data['projects']['templates'][name]['hooks']
      for config in hook_configs:
        hook = Hook.factory(config)

        if not hook:
          self.LOG.warn('Unable to create Hook fron config "{}"'.format(config))
          continue

        self.__hooks[name] = hook
        self.LOG.debug('Created hook: {}'.format(hook.name))

    # Extract regular expressions and project configuration data
    self.__regex = self.data['projects']['regex']
    self.__configs = self.data['projects']['configs']

    self.LOG.info('Loaded {} templates, {} user assignments, {} regular expressions and {} configs.'.format(
      len(self.__templates.keys()),
      len(self.__user_assignments),
      len(self.__regex),
      len(self.__configs))
    )

  def __validate(self):
    # Make sure a "default" template exists
    if not 'default' in self.__templates:
      self.LOG.warn('No "default" template defined.')
      return False
   
    for template in self.__templates:
      if not self.__validate_template(template):
        return False

    for config in self.__configs:
      if not self.__validate_config(config):
        return False

    return True

  def __validate_template(self, template):
    return True

  def __validate_config(self, config):
    if not 'template' in config:
      config['template'] = 'default'
    elif not config['template'] in self.__templates:
      self.LOG.warn('Project "{}" references unknow template "{}"'.format(project_config['name'], project_config['template']))
      return False

    for field, value in config.items():
      if field in self.__regex:
        pattern = self.__regex[field]
        result = re.match(pattern, value)
        if not result:
          self.LOG.warn('Project "{}" defines invalid value "{}" for field "{}"'.format(project_config['name'], field, value))
          return False

    return True

  def __generate_project(self, template, config):

    # Set up jinja2 templates
    domain_template = Template(template.domain)
    name_template = Template(template.name)
    description_template = Template(template.description)

    # Create dict data structure with rendered values
    data = {
      "domain": domain_template.render(project = config),
      "name": name_template.render(project = config),
      "description": description_template.render(project = config),
      "enable": config.enable if hasattr(config, 'enable') else template.enable,
      "properties": {},
    }

    # Fill data with templates properties
    for property, value in template.properties.items():
      template = Template(value)
      data['properties'][property] = template.render(project = config)

    return data

  def synchronize(self):

    # Load and validate data
    self.__load()
    success = self.__validate()

    if success:
      self.LOG.info("Projects loaded and validated.")
    else:
      self.LOG.warn("Failed to validate projects. See output for more information.")

    # Generate project definitions from templates
    projects = []
    for config in self.__configs:
      template = self.__templates[config['template']]  
      project = self.__generate_project(template, config)
      projects.append(project)
      self.LOG.debug('Generated project from template "{}": {}'.format(config['template'], project))
    self.LOG.info('Generated projects: {}'.format(len(projects)))

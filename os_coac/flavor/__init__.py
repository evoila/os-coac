import re
import yaml
import logging

from jinja2 import Template 
from os_coac.flavor.model import FlavorTemplate
from os_coac import ResourceManager
from oslo_config import cfg
from oslo_config import types

group = cfg.OptGroup(name='flavors',
                           title='Flavor options')

opts = [
  cfg.StrOpt(name='resource_file',
             default='/etc/os-coac/flavors.yaml',
             help='Path to the file containing project configuration.'),
]

CONF = cfg.CONF
CONF.register_group(group)
CONF.register_opts(opts, group=group)

class FlavorResourceManager(ResourceManager):
  
  LOG = logging.getLogger(__name__)

  __templates = {}
  __configs = []
  __regex = {}

  def __load(self):
    with open(CONF.flavors.resource_file, 'r') as stream:
      self.data = yaml.load(stream)

    # Generate FlavorTemplates
    for name in self.data['flavors']['templates']:
      template = FlavorTemplate(
        name         = self.data['flavors']['templates'][name]['name'],
        ram          = self.data['flavors']['templates'][name]['ram'],
        disk         = self.data['flavors']['templates'][name]['disk'],
        ephemeral    = self.data['flavors']['templates'][name]['ephemeral'],
        vcpus        = self.data['flavors']['templates'][name]['vcpus'],
        public       = self.data['flavors']['templates'][name]['public'],
        properties   = self.data['flavors']['templates'][name]['properties'],
      )
      self.__templates[name] = template
      self.LOG.debug('Created template: {}'.format(name))

    # Extract regular expressions and flavor configuration data
    self.__regex_patterns = self.data['flavors']['regex']
    self.__configs = self.data['flavors']['configs']

    self.LOG.info('Loaded {} templates, {} regular expressions and {} configs.'.format(
      len(self.__templates.keys()),
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
      self.LOG.warn('Flavor "{}" references unknow template "{}"'.format(config['name'], config['template']))
      return False

    for field, value in config.items():
      if field in self.__regex:
        pattern = self.__regex[field]
        result = re.match(pattern, value)
        if not result:
          self.LOG.warn('Flavor "{}" defines invalid value "{}" for field "{}"'.format(project_config['name'], field, value))
          return False

    return True

  def __generate_flavor(self, template, config):

    # Set up jinja2 templates
    name_template = Template(template.name)
    ram_template = Template(template.ram)
    disk_template = Template(template.disk)
    ephemeral_template = Template(template.ephemeral)
    vcpus_template = Template(template.vcpus)
    public_template = Template(template.public)

    # Generate dict data structure with rendered values
    data = {
      "name": name_template.render(flavor = config),
      "ram": ram_template.render(flavor = config),
      "disk": disk_template.render(flavor = config),
      "ephemeral": ephemeral_template.render(flavor = config),
      "vcpus": vcpus_template.render(flavor = config),
      "public": public_template.render(flavor = config),
      "properties": {},
    }

    # Fill data with template properties
    for property, value in template.properties.items():
      template = Template(value)
      data['properties'][property] = template.render(flavor = config)

    return data

  def synchronize(self):
    self.__load()
    success = self.__validate()

    if success:
      self.LOG.info("Flavors loaded and validated.")
    else:
      self.LOG.warn("Failed to validate. See output for more information.")

    flavors = []
    for config in self.__configs:
      template = self.__templates[config['template']]  
      flavor = self.__generate_flavor(template, config)
      flavors.append(flavor)
      self.LOG.debug('Generated flavor from template "{}": {}'.format(config['template'], flavor))
    self.LOG.info('Generated flavors: {}'.format(len(flavors)))

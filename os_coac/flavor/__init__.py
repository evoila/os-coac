import re
import yaml
import logging

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
  __regex_patterns = {}

  def __init__(self):
    with open(CONF.flavors.resource_file, 'r') as stream:
      self.data = yaml.load(stream)

    for name in self.data['flavors']['templates']:
      self.__templates[name] = FlavorTemplate(
        name         = name,
        flavor_name  = self.data['flavors']['templates'][name]['name'],
        ram          = self.data['flavors']['templates'][name]['ram'],
        disk         = self.data['flavors']['templates'][name]['disk'],
        ephemeral    = self.data['flavors']['templates'][name]['ephemeral'],
        vcpus        = self.data['flavors']['templates'][name]['vcpus'],
        public       = self.data['flavors']['templates'][name]['public'],
        properties   = self.data['flavors']['templates'][name]['properties'],
      )
      self.LOG.info('Created flavor template: {}'.format(name))

    self.__regex_patterns = self.data['flavors']['regex']
    self.__configs = self.data['flavors']['configs']

    if not 'default' in self.__templates:
      raise ValueError('No project template with name "default" defined.')

    for template in self.__templates:
      self.__validate_template(template)

    for config in self.__configs:
      self.__validate_config(config)

  def __validate_template(self, template):
    pass

  def __validate_config(self, config):
    if not 'template' in config:
      config['template'] = 'default'
    elif not config['template'] in self.__templates:
      raise ValueError(
        'Flavor Config {}: Template {} unknown.'.format(
          config['name'],
          config['template']
        )
      )

    for field, value in config.items():
      if field in self.__regex_patterns:
        pattern = self.__regex_patterns[field]
        result = re.match(pattern, value)
        if not result:
          raise ValueError(
            'Flavor {}: Value "{}" in field "{}" does not match pattern "{}"'.format(
              config['name'],
              value,
              field,
              pattern
            )
          )

  def synchronize(self):
    flavors = []
    for config in self.__configs:
      template = self.__templates[config['template']]  
      flavor = template.generate(config)
      flavors.append(flavor)
      self.LOG.debug('Generated flavor from template "{}": {}'.format(config['template'], flavor))
    self.LOG.info('Generated flavors: {}'.format(len(flavors)))

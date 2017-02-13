import logging
import json

from jinja2 import Template

class FlavorTemplate:

  LOG = logging.getLogger(__name__)

  def __init__(self, name, flavor_name, ram, disk, ephemeral, vcpus, public, properties):
    self.name = name
    self.flavor_name = flavor_name
    self.ram = ram
    self.disk = disk
    self.ephemeral = ephemeral
    self.vcpus = vcpus
    self.public = public
    self.properties = properties

  def generate(self, flavor_config):
    name_template = Template(self.flavor_name)
    ram_template = Template(self.ram)
    disk_template = Template(self.disk)
    ephemeral_template = Template(self.ephemeral)
    vcpus_template = Template(self.vcpus)
    public_template = Template(self.public)

    data = {
      "name": name_template.render(flavor = flavor_config),
      "ram": ram_template.render(flavor = flavor_config),
      "disk": disk_template.render(flavor = flavor_config),
      "ephemeral": ephemeral_template.render(flavor = flavor_config),
      "vcpus": vcpus_template.render(flavor = flavor_config),
      "public": public_template.render(flavor = flavor_config),
      "properties": {},
    }

    for property, value in self.properties.items():
      template = Template(value)
      data['properties'][property] = template.render(flavor = flavor_config)

    return data

import logging
import json

class FlavorTemplate:

  def __init__(self, name, ram, disk, ephemeral, vcpus, public = True, properties = {}):
    self.name = name
    self.ram = ram
    self.disk = disk
    self.ephemeral = ephemeral
    self.vcpus = vcpus
    self.public = public
    self.properties = properties

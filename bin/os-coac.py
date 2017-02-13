#!/usr/bin/env python

import os
import sys
import inspect
import logging

cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"..")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

import os_coac
from os_coac import config
from os_coac.project import ProjectResourceManager
from os_coac.flavor import FlavorResourceManager
from oslo_config import cfg

LOG = logging.getLogger(__name__)

def main():
  config.parse_args()

  CONF = cfg.CONF

  logging.basicConfig(level = logging.DEBUG if CONF.debug else logging.INFO)

  resource_managers = [
    FlavorResourceManager(),
    ProjectResourceManager(),
  ]

  for m in resource_managers:
    m.synchronize()

if  __name__ =='__main__':
  main()

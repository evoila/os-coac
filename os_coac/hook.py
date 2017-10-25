import logging
import subprocess
import os

from subprocess import Popen
from abc import ABC
from oslo_config import cfg
from os_coac.definitions import ROOT_DIR

opts = [
  cfg.StrOpt('hook_dir',
             default='/etc/os-coac/hooks.d',
             help='The directory that contains hook.'),
]

CONF = cfg.CONF
CONF.register_opts(opts)

class Hook(ABC):

  def __init__(self, name):
    self.name = name

  def run(self):
    pass

class SystemHook(Hook):

  LOG = logging.getLogger(__name__)

  def __init__(self, name, parameters, environment):
    super().__init__(name)
    self.parameters = parameters
    self.environment = environment

  def run(self):
    CONF = cfg.CONF

    # Handle relative hook_dir paths differently than absolute paths 
    hook_dir = CONF.hook_dir
    if not CONF.hook_dir.startswith('/'):
      hook_dir = os.path.join(ROOT_DIR, CONF.hook_dir)

    # Setup args and environment parameters
    hook = os.path.join(hook_dir, self.name)
    args = [ hook ] + self.parameters
    env = os.environ.copy()
    env.update(self.environment)

    # Execute hook, wait for it to finish and return exit code
    self.LOG.info("Running hook {} with parameters {} and environment {}".format(
	self.name, self.parameters, self.environment))

    process = Popen(args, shell=True, stdout=None, stderr=None, env=env, cwd=hook_dir)
    process.wait()

    return process.returncode

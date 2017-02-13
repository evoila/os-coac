from oslo_config import cfg
from oslo_config import types

common_opts = [
  cfg.StrOpt('project_conf',
             default='/etc/os-coac/project.yaml',
             help='Path to the file containing project configuration.'),
  cfg.BoolOpt('debug',
             default=False,
             help='Enable debug logging'),
]

CONF = cfg.CONF
CONF.register_opts(common_opts)

def parse_args(args=None, usage=None, default_config_files=None):
  CONF(args=args,
    project='os-coac',
    usage=usage,
    default_config_files=default_config_files)

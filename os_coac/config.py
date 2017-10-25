from oslo_config import cfg
from oslo_config import types

common_opts = [
  cfg.StrOpt('hook_directory',
             default='/etc/os-coac/hooks.d',
             help='The directory that contains hook scripts.'),
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

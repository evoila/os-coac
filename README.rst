OpenStack - Configuration as Code (OS-COAC)
===========================================

OS-COAC is meant for cloud operators to manage certain parts of the configuration as code. This allows changes to the environment to be stored in a way that is audit-proof and runs through the same review process as any other code. Further, it enabled operators to enforce certain compliance rules and restrictions on configurations.

The project was initiated by the need to create OpenStack projects as a result to customer service requests. By regulation, projects had to follow a certain naming convention and include multiple metadata attributes. In order to implement a standardized process for project creation that reduces the factor of human error, we decided to store Project information in a YAML file that is stored in a Git repository and could only be changed be the regular approval process. Once merged into master, a change is picked up by CI/CD which executes os-coac in order to create or update configurations where necessary.

Features
--------
- Keystone Projects
- Nova Flavors

Running
-------
OS-COAC comes with an executable file intendet for CLI usage in bin/os-coac.py. The script takes the configuration options --config-file and --config-dir. Using either way, os-coac must find the os-coac.conf file. We provided working default configurations in etc/os-coac:

.. code-block:: bash

  bin/os-coac.py --config-dir etc/os-coac

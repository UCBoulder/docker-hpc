# these options are from the coursera-labs repository

c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.port = 8888
c.NotebookApp.open_browser = False

# Run without authentication
c.NotebookApp.token = ''
# Allow requests from the proxy
c.NotebookApp.allow_origin = '*'

c.NotebookApp.nbserver_extensions = {}

c.NotebookApp.trust_xheaders = True

# Supply overrides for terminado. Currently only supports "shell_command".
c.NotebookApp.terminado_settings = {'shell_command': ['/bin/bash', '--login']}

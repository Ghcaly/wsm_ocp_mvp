#/bin/sh
cd src
export PATH="$HOME/.local/bin:$PATH"
ddtrace-run uwsgi --ini wsgi.ini --enable-threads
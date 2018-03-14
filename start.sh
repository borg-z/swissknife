#!/bin/bash
ln -fs /usr/share/zoneinfo/Etc/GMT-3 /etc/localtime
rm  -rf /etc/nginx/sites-available/default*
nginx 
source venv/bin/activate
flask rq worker &
for run in {1..10}
do
  flask rq worker &
done
gunicorn run:app


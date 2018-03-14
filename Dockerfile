FROM ubuntu:17.10
RUN mkdir /srv/app
WORKDIR /srv/app
RUN echo 'deb [trusted=yes] http://downloads.skewed.de/apt/artful artful universe' >>  /etc/apt/sources.list
RUN apt-get  update
RUN apt-get -y install python3 python3-graph-tool python3-pip python3-virtualenv build-essential
RUN apt-get -y install nginx
RUN apt-get -y install telnet
COPY flask-app.conf  /etc/nginx/sites-available/flask-app.conf
RUN ln -s /etc/nginx/sites-available/flask-app.conf /etc/nginx/sites-enabled/ 
COPY requirements ./
COPY venv.sh /srv/app
RUN ./venv.sh
COPY app /srv/app/app
COPY manage.py /srv/app/manage.py
COPY run-stable.py /srv/app/run.py
EXPOSE 80
EXPOSE 5000
EXPOSE 8000
RUN echo

COPY start.sh /srv/app
ENTRYPOINT bash start.sh

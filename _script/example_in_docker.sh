tee Dockerfile <<EOF
from centos:7

RUN yum -y install m4 git wget python cmake make gcc-c++ ncurses-devel bison zlib zlib-devel zlib-static openssl vim findutils openssl vim m4 libaio

RUN wget -O example.sh https://raw.github.com/AndriiNikitin/mariadb-environs-spider/master/_script/example.sh

RUN example.sh
EOF

docker build .


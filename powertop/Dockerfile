FROM ubuntu:latest
USER root

WORKDIR /root

ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN echo "===> INSTALLING DEPENDENCIES" && \
  apt-get -y update && \
  apt-get -y upgrade && \
  apt-get install -y git libncurses-dev libnl-3-200 libnl-genl-3-dev libtool \
  pciutils autoconf autoconf-archive pkg-config build-essential autopoint \
  gettext
# disabled because bug with ryzen cards
# RUN apt-get install powertop

RUN echo "===> CLONE POWERTOP" && \
  git clone https://github.com/fenrus75/powertop.git --branch v2.13

COPY ryzen.patch .

WORKDIR /root/powertop
RUN echo "===> BUILD POWERTOP" && \
  patch -p1 < ../ryzen.patch && \
  ./autogen.sh && \
  ./configure && \
  make && \
  ln -s /root/powertop/src/powertop /usr/bin/powertop && \
  chmod +x /usr/bin/powertop


WORKDIR /root
COPY run_powertop.sh .
RUN mkdir /root/data && \
  chmod +x run_powertop.sh

ENTRYPOINT ["bash", "/root/run_powertop.sh"]

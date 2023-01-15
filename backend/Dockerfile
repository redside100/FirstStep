FROM python:3.9.13-buster

WORKDIR /app

# Build cbc binary (https://python-mip.readthedocs.io/en/latest/install.html) (modified)
# install dependencies to build
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gfortran \
    liblapack-dev \
    libamd2 libcholmod3 \
    libmetis-dev \
    libsuitesparse-dev \
    libnauty2-dev \
    git
# directory to download and compile CBC
RUN mkdir -p ~/build; cd ~/build
# download latest version of coinbrew
RUN wget -nH https://raw.githubusercontent.com/coin-or/coinbrew/master/coinbrew
# download CBC and its dependencies with coinbrew
RUN bash coinbrew fetch Cbc@master --no-prompt
# build, replace prefix with your install directory,  add --enable-debug if necessary
RUN bash coinbrew build Cbc@master --no-prompt --prefix=/home/fs/prog/ --tests=none --enable-cbc-parallel --enable-relocatable

RUN export LD_LIBRARY_PATH="/home/fs/prog/lib"
RUN export DYLD_LIBRARY_PATH="/home/fs/prog/lib"

COPY * /app/

RUN pip3 install -r requirements.txt

CMD ["python3", "app.py"]
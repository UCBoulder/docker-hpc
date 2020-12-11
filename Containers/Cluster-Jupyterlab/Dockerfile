ARG ROOT_CONTAINER=ubuntu:focal-20200720@sha256:5d1d5407f353843ecf8b16524bc5565aa332e9e6a1297c73a92d3e754b8a636d

ARG BASE_CONTAINER=$ROOT_CONTAINER

FROM $BASE_CONTAINER 

MAINTAINER Thomas Hauser <thomas.hauser@colorado.edu>

ARG NB_USER="hpc-learner"
ARG NB_UID="1000"
ARG NB_GID="100"

ARG SLURM_VERSION=20.02.5
ARG SLURM_DOWNLOAD_MD5=3902c8a06643cf70cf6fe750971f7146
ARG SLURM_DOWNLOAD_URL=https://download.schedmd.com/slurm/slurm-20.02.5.tar.bz2

ARG SPACK_RELEASE=v0.15

ENV     DEBIAN_FRONTEND=noninteractive \
	SPACK_ROOT=/usr/local \
	FORCE_UNSAFE_CONFIGURE=1

# Fix DL4006
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

USER root

# install all packages required for the containers

RUN apt-get -q update && apt-get install -qy --no-install-recommends \
	man git wget \
	locales \
	emacs-nox vim \
	bc \
	bash-completion \
	autoconf \
	make cmake \
	build-essential \
	ca-certificates \
	coreutils \
	curl \
	gfortran \
	openssh-server \
	pkg-config \
	rsync \
	unzip \
	sudo \
	python3 \
	python3-dev \
	python3-pip \
	&& apt-get -qy autoremove && apt-get clean && rm -r /var/lib/apt/lists/*

# to provide python for slurm
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# packages for slurm

RUN apt-get -q update && apt-get install -qy --no-install-recommends \
	munge \
	libmunge-dev \
	libmunge2 \
	gosu \
	systemd \
	&& apt-get -qy autoremove && apt-get clean && rm -r /var/lib/apt/lists/*

# Configure gosu
RUN set -x && gosu nobody true

# Fix the sudo working sudo: setrlimit(RLIMIT_CORE): Operation not permitted
RUN echo "Set disable_coredump false" >> /etc/sudo.conf

# Install slurm
RUN groupadd -r slurm --gid=995 && useradd -r -g slurm --uid=995 slurm

RUN set -x \
	&& wget -O slurm.tar.bz2 "$SLURM_DOWNLOAD_URL" \
	&& echo "$SLURM_DOWNLOAD_MD5" slurm.tar.bz2 | md5sum -c - \
	&& mkdir /usr/local/src/slurm \
	&& tar jxf slurm.tar.bz2 -C /usr/local/src/slurm --strip-components=1 \
	&& rm slurm.tar.bz2 \
	&& cd /usr/local/src/slurm \
	&& ./configure --enable-multiple-slurmd --prefix=/usr --sysconfdir=/etc/slurm \
	&& make install \
	&& cd contribs/pmi && make install \
	&& cd ../pmi2 && make install \
	&& cd ../../ \
	&& install -D -m644 contribs/slurm_completion_help/slurm_completion.sh /etc/profile.d/slurm_completion.sh \
	&& cd \
	&& rm -rf /usr/local/src/slurm \
	&& mkdir -p /etc/sysconfig/slurm \
        /var/spool/slurmd \
        /var/run/slurmd \
        /var/run/slurmdbd \
        /var/lib/slurmd \
        /var/log/slurm \
        /data \
	&& touch /var/lib/slurmd/node_state \
	/var/lib/slurmd/front_end_state \
	/var/lib/slurmd/job_state \
	/var/lib/slurmd/resv_state \
        /var/lib/slurmd/trigger_state \
        /var/lib/slurmd/assoc_mgr_state \
        /var/lib/slurmd/assoc_usage \
        /var/lib/slurmd/qos_usage \
        /var/lib/slurmd/fed_mgr_state \
	&& chown -R slurm:slurm /var/*/slurm*

COPY slurm/slurm.conf /etc/slurm/slurm.conf
COPY slurm/hosts /root/slurm_hosts

RUN cat /root/slurm_hosts /etc/hosts

# ------------------------------------------------------------
# Add OpenMPI and MPICH as well as hdf5 for modules using spack
# ------------------------------------------------------------
RUN apt-get -q update && apt-get install -qy --no-install-recommends \
	libreadline-dev \
	libncursesw5 \
	libncursesw5-dev \
	tcl-dev \
	zlib1g-dev \
	libtool-bin \
	libtool \
	automake \
	libxml2 libxml2-dev \
	&& apt-get -qy autoremove && apt-get clean && rm -r /var/lib/apt/lists/*

# install and configure spack to create modules
RUN cd $SPACK_ROOT \
    && git clone https://github.com/spack/spack.git \
    && cd spack \
    && git checkout releases/v0.15 \
    && echo ". $SPACK_ROOT/spack/share/spack/setup-env.sh" > /root/101-spack.sh \
    && chmod +x /root/101-spack.sh

COPY modules.yaml packages.yaml /etc/spack/

SHELL ["/bin/bash", "-c"]
RUN . /root/101-spack.sh \
	&& spack install lmod \
	&& echo "source $(spack location --install-dir lmod)/lmod/lmod/init/bash" >> /etc/profile.d/lmod.sh \
	&& echo "module use $SPACK_ROOT/share/spack/lmod/linux-ubuntu20.04-x86_64/Core" >> /etc/profile.d/lmod.sh \
        && mkdir -p $SPACK_ROOT/share/spack/lmod/linux-ubuntu20.04-x86_64/Core

# OpenMPI + MPICH + HDF5 3 version + parallel and lapack
RUN . /root/101-spack.sh \
	&& spack install openmpi+pmi+legacylaunchers schedulers=auto \
	&& spack install mpich+slurm pmi=pmi2 \
	&& spack install hdf5~mpi \
	&& spack install hdf5+mpi+fortran+cxx ^mpich+slurm pmi=pmi2 \
	&& spack install hdf5+mpi+fortran+cxx ^openmpi+pmi+legacylaunchers schedulers=auto \
	&& spack install lapack \
	&& spack install parallel \
	&& spack module lmod refresh --delete-tree -y \
	&& spack clean -a

# unminimize the container to enable man pages
RUN apt-get update && yes | unminimize

# ------------------------------------------------------------
# create the NB user
# ------------------------------------------------------------
# Enable prompt color in the skeleton .bashrc before creating the default NB_USER
RUN sed -i 's/^#force_color_prompt=yes/force_color_prompt=yes/' /etc/skel/.bashrc

# Create NB_USER wtih name jovyan user with UID=1000 and in the 'users' group
# and make sure these dirs are writable by the `users` group.
RUN echo "auth requisite pam_deny.so" >> /etc/pam.d/su && \
	sed -i.bak -e 's/^%admin/#%admin/' /etc/sudoers && \
	sed -i.bak -e 's/^%sudo/#%sudo/' /etc/sudoers && \
	useradd -m -s /bin/bash -N -u $NB_UID $NB_USER && \
	mkdir -p /scratch/$NB_USER && \
	chown $NB_USER:$NB_GID /scratch/$NB_USER && \
	mkdir -p /projects/$NB_USER && \
	chown $NB_USER:$NB_GID /projects/$NB_USER && \
	ln -s /projects/$NB_USER /home/$NB_USER/projects && \
	ln -s /scratch/$NB_USER /home/$NB_USER/scratch && \
	echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
	sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
# SSH login fix. Otherwise user is kicked off after login
	sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

# ------------------------------------------------------------
# Install Jupyterlab and numpy
# ------------------------------------------------------------
# Install Jupyter Lab and upgrade notebook
RUN . /root/101-spack.sh \
	&& . /etc/profile.d/lmod.sh \
	&& module load mpich \
	&& apt-get install -qy --no-install-recommends python3-dev \
	&& pip3 install jupyter jupyterlab notebook numpy mpi4py dask-mpi PyYAML --upgrade

# copy the jupyter config 
COPY jupyter_notebook_config.py /usr/local/etc/jupyter

# add supervisor s6 
ADD https://github.com/just-containers/s6-overlay/releases/download/v2.0.0.1/s6-overlay-amd64.tar.gz /tmp/
RUN tar xzf /tmp/s6-overlay-amd64.tar.gz -C / --exclude='./bin' && \
	tar xzf /tmp/s6-overlay-amd64.tar.gz -C /usr ./bin

# Configure munge for s6
ADD cont-init.d/01-munge /etc/cont-init.d

# Configure slurm for s6
ADD cont-init.d/02-hosts /etc/cont-init.d
ADD cont-init.d/03-slurm /etc/cont-init.d

# fix slurm permissions
ADD slurm-permissions /etc/fix-attrs.d

# fix permission of .jupyter in hpc-learner directory
ADD jupyter-user-permissions /etc/fix-attrs.d

# Setting up juptyerlab under s6
ADD services.d/jupyterlab /etc/services.d/jupyterlab

ENTRYPOINT ["/init"]

ENV HOME /home/$NB_USER
WORKDIR $HOME



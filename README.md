# bindicator
Bin indication light controller

# Installing on FreeBSD

FreeBSD installation instructions:

    tzsetup # Set timezone if not configured
    pkg install py27-pip
    pkg install git
    adduser # Add a user named bindicator
    pip install --user pipenv
    cd /usr/local/share
    git clone https://github.com/sloe/bindicator.git
    su - bindicator
    cd /usr/local/share/bindicator
    set path=( ~/.local/bin $path )
    pipenv install -r requirements.txt
    # Test using the following
    pipenv run python bindicator.py

Example content for /usr/local/etc/rc.d/bindicator:

    #!/bin/sh

    # PROVIDE: bindicator
    # REQUIRE: DAEMON
    # KEYWORD: shutdown

    . /etc/rc.subr

    export PYTHONPATH=/home/bindicator/.local/lib/python2.7/site-packages
    export PATH="/home/bindicator/.local/bin:$PATH"
    export WORKON_HOME=/home/bindicator/.local/share/virtualenvs

    name=bindicator
    rcvar=bindicator_enable
    pidfile="/var/run/${name}.pid"
    bindicator_chdir=/usr/local/share/bindicator
    bindicator_path=$PATH
    command=/usr/sbin/daemon
    command_args="-o /var/log/bindicator.log -R 30 -P ${pidfile} -u bindicator /home/bindicator/.local/bin/pipenv run python bindicator.py"

    load_rc_config $name
    run_rc_command "$1"

Example content for /usr/local/etc/newsyslog.conf.d/bindicator:

    # logfilename          [owner:group]    mode count size when  flags [/pid_file] [sig_num]
    /var/log/bindicator.log                 600  10    100  *     JB    /var/run/bindicator.pid

Add bindicator_enable="YES" to /etc/rc.conf.local


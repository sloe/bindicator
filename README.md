# bindicator
Bin indication light controller

# Installing on FreeBSD

FreeBSD installation instructions:

  tzsetup # Set timezone if not configured
  pkg install py27-pip
  pkg install git
  adduser # Add a user named bindicator
  pip install --user pipenv
  git clone https://github.com/sloe/bindicator.git
  cd bindicator
  set path=( ~/.local/bin $path )
  pipenv install -r requirements.txt
  pipenv run python bindicator.py

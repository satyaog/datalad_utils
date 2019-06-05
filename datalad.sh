#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )"; pwd -P)"

dlcreate()
{
  name=$1
  python $DIR/datalad_brf.py create $name
}

dlinst()
{
  url=$1
  python $DIR/datalad_brf.py install $url
}

dlinstsubds()
{
  subdataset=$1
  python $DIR/datalad_brf.py install_subdatasets
}

dlpublish()
{
  python $DIR/datalad_brf.py publish
}

dlupdate()
{
  python $DIR/datalad_brf.py update
}

dlinitgithub()
{
  name=$1
  login=$2
  python $DIR/datalad_brf.py init_github $name $login
}

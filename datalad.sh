#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )"; pwd -P)"

dlcreate()
{
  name=$1
  sibling=$2
  python $DIR/datalad_brf.py create $name $sibling
}

dlinst()
{
  url=$1
  name=$2
  sibling=$3
  python $DIR/datalad_brf.py install $url $name $sibling
}

dlinstsubds()
{
  subdataset=$1
  sibling=$2
  python $DIR/datalad_brf.py install_subdatasets $sibling
}

dlpublish()
{
  path=$1
  sibling=$2
  python $DIR/datalad_brf.py publish $path $sibling
}

dlupdate()
{
  sibling=$1
  python $DIR/datalad_brf.py update $sibling
}

dlinitgithub()
{
  name=$1
  login=$2
  python $DIR/datalad_brf.py init_github $name $login
}

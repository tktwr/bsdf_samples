#!/bin/bash

addon_name=$1
pkg_dir=$2

mkdir -p $pkg_dir
zip -r $pkg_dir/${addon_name}_`date +%Y%m%d`.zip $addon_name

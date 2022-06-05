#!/bin/bash

WIN_HOME="C:/Users/$USER"
ADDONS_DIR="$WIN_HOME/AppData/Roaming/Blender Foundation/Blender/3.1/scripts/addons"
ADDON_NAME=bsdf_samples

#======================================================
# functions
#======================================================
f_upload() {
	cp -a $ADDON_NAME "$ADDONS_DIR"
}

f_diff() {
  vimdiff.sh "$ADDONS_DIR/$ADDON_NAME/__init__.py" $ADDON_NAME/__init__.py
}

f_dirdiff() {
  vimdirdiff.sh "$ADDONS_DIR/$ADDON_NAME" $ADDON_NAME
}

f_pkg() {
  mkdir -p pkg
  zip -r pkg/$ADDON_NAME-`date +%Y%m%d`.zip $ADDON_NAME
}

f_clean() {
  rm -rf pkg
}

#------------------------------------------------------
f_help() {
  echo "upload"
  echo "diff"
  echo "dirdiff"
  echo "pkg"
  echo "clean"
  echo "help"
}

f_default() {
  f_help
}

#======================================================
# main
#======================================================
func_name=${1:-"default"}
eval "f_$func_name"



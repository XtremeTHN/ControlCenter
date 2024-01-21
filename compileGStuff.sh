#!/bin/bash
APP_ID="com.github.XtremeTHN.ControlCenter"

set -e

sudo cp ./$APP_ID.gschema.xml /usr/share/glib-2.0/schemas
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

sass src/styles/main.scss src/styles/style.css

glib-compile-resources src/res/uncompiled/$APP_ID.gresource.xml
mv src/res/uncompiled/$APP_ID.gresource src/res
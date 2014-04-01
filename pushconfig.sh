#!/bin/bash

python manage.py exportenv --settings-module production_settings

heroku config:push --overwrite


#!/bin/bash

sudo rm -rf /etc/supervisor/conf.d/*
cd ~/connected-devices/
sudo cp -r supervisor/* /etc/supervisor/conf.d
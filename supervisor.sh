#!/bin/bash

sudo rm -rf /etc/supervisor/conf.d/*
cd ~/lampi-looper/
sudo cp -r supervisor/* /etc/supervisor/conf.d
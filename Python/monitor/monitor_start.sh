#!/bin/sh

screen -m -d -S Watchdog bash -c "conda activate Greenhouse; python monitor.py"
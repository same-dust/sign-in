#!/usr/bin/env bash

echo -e "\033[34m--------------------wsgi process--------------------\033[0m"

ps -ef |grep sign-in_uwsgi.ini | grep -v grep

sleep 0.5

echo -e '\n--------------------going to close--------------------'

ps -ef |grep sign-in_uwsgi.ini | grep -v grep | awk '{print $2}' | xargs kill -9

sleep 0.5

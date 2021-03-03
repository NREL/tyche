#!/usr/bin/env bash

export QUART_APP=main:app

hypercorn --bind 127.0.0.1:5000 $QUART_APP

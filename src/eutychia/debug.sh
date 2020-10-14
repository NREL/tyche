#!/usr/bin/env bash

export QUART_APP=main:app
quart run --host 127.0.0.1 --port 5000

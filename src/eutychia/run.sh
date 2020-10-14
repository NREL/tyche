#!/usr/bin/env bash

hypercorn --bind 127.0.0.1:5000 main:app

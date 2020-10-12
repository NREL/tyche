#!/usr/bin/env nix-shell
#!nix-shell -I nixpkgs=https://github.com/NixOS/nixpkgs/archive/5272327b81ed355bbed5659b8d303cf2979b6953.tar.gz
#!nix-shell --run "hypercorn --access-logfile - --error-logfile - --certfile certificate.crt --keyfile private.key --bind 0.0.0.0:5000 main:app" -- ../../shell.nix

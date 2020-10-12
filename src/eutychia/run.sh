#!/usr/bin/env nix-shell
#!nix-shell -I nixpkgs=/home/bbush/.nix-defexpr/channels/pinned-20.03
#!nix-shell --run "hypercorn -b 0.0.0.0:5000 main:app" -- ../../shell.nix

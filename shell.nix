with import <nixpkgs> {};

let

  python = python37.override {
    packageOverrides = python-self: python-super: {

      werkzeug = python-super.werkzeug.overrideAttrs (oldAttrs: {
        src = python37.pkgs.fetchPypi {
          pname = "Werkzeug";
          version = "1.0.1";
          sha256 = "0z74sa1xw5h20yin9faj0vvdbq713cgbj84klc72jr9nmpjv303c";
        };
      });

      hypercorn = python.pkgs.buildPythonPackage rec {
        pname = "Hypercorn";
        version = "0.11.1";
        src = python.pkgs.fetchPypi {
          inherit pname version;
          sha256 = "1sygkaxbivvbv39xwrdcy0w84sl3jbfzavphxfryif479bc9vil1";
        };
        propagatedBuildInputs = (with python.pkgs; [
          h2
          priority
          toml
          typing-extensions
          wsproto
        ]); 
        doCheck = false;
        meta = with lib; {
          homepage = https://pypi.org/project/Hypercorn/;
          description = "A ASGI Server based on Hyper libraries and inspired by Gunicorn.";
        };
      };

      quart = python.pkgs.buildPythonPackage rec {
        pname = "Quart";
        version = "0.13.1";
        src = python.pkgs.fetchPypi {
          inherit pname version;
          sha256 = "0mpzjxp89ns7lwmlvb5hfa62b09mb3hnsrrw00jbh8ab3r64wqww";
        };
        propagatedBuildInputs = (with python.pkgs; [
          aiofiles
          blinker
          click
          hypercorn
          jinja2
          setuptools
          toml
          werkzeug
        ]); 
        doCheck = false;
        meta = with lib; {
          homepage = https://pypi.org/project/Quart/;
          description = "Quart is a Python ASGI web microframework. It is intended to provide the easiest way to use asyncio functionality in a web context, especially with existing Flask apps.";
        };
      };

    };
  };

  env = (
    python.withPackages (ps: with ps; [
      hypercorn
      matplotlib
    # mystic
      numpy
      pandas
    # pymoo
    # pymoso
    # pyomo
      quart
      recommonmark
    # scikitlearn
      scipy
      seaborn
      sphinx
    # statsmodels
    ])
  ).env;

in
  lib.overrideDerivation env (old: {
    shellHook = ''
    '';
  })

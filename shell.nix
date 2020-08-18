with import <nixpkgs> {};

let

  python = python37;
# python = python37.override {
#   packageOverrides = python-self: python-super: {
#     scipy = python-super.scipy.overrideAttrs (oldAttrs: {
#       src = python37.pkgs.fetchPypi {
#         pname = "scipy";
#         version = "1.5.2";
#         sha256 = "1jchdymikkpqr7glr4iyipcfn4ciscl0h5cyg9bdfgzbj0ym2v06";
#       };
#     });
#   };
# };

  dill = python.pkgs.buildPythonPackage rec {
    pname = "dill";
    version = "0.3.2";
    src = fetchgit {
      url    = https://github.com/uqfoundation/dill.git;
      rev    = "afc5b2c79d242b18c97a09c8a309fdaa61a73678";
      sha256 = "0grphyws2pldcmmd7h4j77m8k0c550j110gr93v2v8rq1jamnmsv";
    };
    propagatedBuildInputs = (with python.pkgs; [
      setuptools
    ]); 
    doCheck = false;
    meta = with lib; {
      homepage = https://github.com/uqfoundation/dill;
      description = "dill extends python’s pickle module for serializing and de-serializing python objects to the majority of the built-in python types.";
    };
  };

  pox = python.pkgs.buildPythonPackage rec {
    pname = "pox";
    version = "0.2.8";
    src = fetchgit {
      url    = https://github.com/uqfoundation/pox.git;
      rev    = "bdd978f59204c6b2bb96d0eb190a93f519db4aba";
      sha256 = "1hl9cql24kmkkqm110284qv116fg1nn59k6mybmsm6z96m0fa537";
    };
    propagatedBuildInputs = (with python.pkgs; [
      setuptools
    ]); 
    doCheck = false;
    meta = with lib; {
      homepage = https://github.com/uqfoundation/pox;
      description = "pox provides a collection of utilities for navigating and manipulating filesystems.";
    };
  };

  klepto = python.pkgs.buildPythonPackage rec {
    pname = "klepto";
    version = "0.1.9";
    src = fetchgit {
      url    = https://github.com/uqfoundation/klepto.git;
      rev    = "d7fd68e22cfacdfbfc91e50ef700f76c7fc172db";
      sha256 = "07l72pagl768ay42hlxv5k5cilbm553n5wcz8rdzziad9j9fs3yi";
    };
    propagatedBuildInputs = (with python.pkgs; [
      dill
      pox
      setuptools
    ]); 
    doCheck = false;
    meta = with lib; {
      homepage = https://github.com/uqfoundation/klepto;
      description = "klepto extends python's lru_cache to utilize different keymaps and alternate caching algorithms, such as lfu_cache and mru_cache.";
    };
  };

  mystic = python.pkgs.buildPythonPackage rec {
    pname = "mystic";
    version = "0.3.6";
    src = fetchgit {
      url    = https://github.com/uqfoundation/mystic.git;
      rev    = "e0b007b593eb9ff5054aaa88cb5a66d5c0d09941";
      sha256 = "06cqa4kwm1cxyzv8iafbh1dr649abdjiag01gmh3sdsr67qfp97q";
    };
    propagatedBuildInputs = (with python.pkgs; [
      dill
      klepto
      matplotlib
      mpmath
      numpy
    # pathos
    # pyina
      scipy
      sympy
      setuptools
    ]); 
    doCheck = false;
    meta = with lib; {
      homepage = https://pypi.org/project/mystic;
      description = "The mystic framework provides a collection of optimization algorithms and tools that allows the user to more robustly (and easily) solve hard optimization problems.";
    };
  };

  pymoo = python.pkgs.buildPythonPackage rec {
    pname = "pymoo";
    version = "0.4.1";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "1hxwj8c0l2awr3jh6ah3dyp1yvldyrsk0z779kcx8ilj9f63rhd1";
    };
    propagatedBuildInputs = (with python.pkgs; [
      setuptools
    ]); 
    doCheck = false;
    meta = with lib; {
      homepage = https://pymoo.org/;
      description = "Our framework offers state of the art single- and multi-objective algorithms and many more features related to multi-objective optimization such as visualization and decision making.";
    };
  };

  pymoso = python.pkgs.buildPythonPackage rec {
    pname = "pymoso";
    version = "1.0.8";
    src = python.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "0d762wd1jsqg06p6j4mlq9x47pi73ph6h8v4fdr70m6gijzdnd70";
    };
    propagatedBuildInputs = (with python.pkgs; [
      docopt
      setuptools
    ]); 
    doCheck = false;
    meta = with lib; {
      homepage = https://github.com/pymoso/PyMOSO;
      description = "PyMOSO is software for solving multi-objective simulation optimization (MOSO) problems and for creating, comparing, and testing MOSO algorithms.";
    };
  };

  env = (
    python.withPackages (ps: with ps; [
      matplotlib
    # mystic
      numpy
      pandas
    # pymoo
    # pymoso
    # pyomo
    # scikitlearn
      scipy
      seaborn
    # statsmodels
    ])
  ).env;

in
  lib.overrideDerivation env (old: {
    shellHook = ''
    '';
  })

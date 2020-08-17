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
      numpy
      pandas
    # pymoo
      pymoso
      pyomo
      scikitlearn
      scipy
      seaborn
      statsmodels
    ])
  ).env;

in
  lib.overrideDerivation env (old: {
    shellHook = ''
    '';
  })

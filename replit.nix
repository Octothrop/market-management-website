{ pkgs }: {
    deps = [
      pkgs.python39Packages.conda
      pkgs.inetutils
      pkgs.mailutils
      pkgs.python39Packages.werkzeug
      pkgs.python39Packages.jsons
      pkgs.python39Packages.pymysql
      pkgs.python39Packages.sqlalchemy
      pkgs.python39Packages.flask
      pkgs.python39Packages.flask_mail
      pkgs.python39Packages.poetry
      pkgs.python39Packages.pip
      pkgs.cowsay  
      pkgs.python39Packages.oauth
    ];
}
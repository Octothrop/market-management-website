{ pkgs }: {
    deps = [
      pkgs.mailutils
      pkgs.python39Packages.werkzeug
      pkgs.python39Packages.jsons
      pkgs.python39Packages.pymysql
      pkgs.python39Packages.sqlalchemy
      pkgs.python39Packages.flask
      pkgs.python39Packages.poetry
      pkgs.python39Packages.pip
      pkgs.cowsay
    ];
}
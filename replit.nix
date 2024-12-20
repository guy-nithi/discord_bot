{ pkgs }: {
    deps = [
        pkgs.python3Full
        pkgs.python39Packages.flask
        pkgs.replitPackages.prybar-python3
    ];
}

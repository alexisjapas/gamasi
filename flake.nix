{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    systems.url = "github:nix-systems/default";
    devenv.url = "github:cachix/devenv";
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = { self, nixpkgs, devenv, systems, ... } @ inputs:
    let
      forEachSystem = nixpkgs.lib.genAttrs (import systems);
    in
    {
      devShells = forEachSystem
        (system:
          let
            pkgs = nixpkgs.legacyPackages.${system};
          in
          {
            default = devenv.lib.mkShell {
              inherit inputs pkgs;
              modules = [
                {
                  # https://devenv.sh/reference/options/
                  packages = with pkgs; [
                    (python3.withPackages (ps: (with ps; [
                      jupyter
                      notebook
                      ipython
                      black
                      pylint
                      tqdm
                      matplotlib
                      numpy
                      pandas
                      seaborn
                      tifffile
                      pyvis
                      imageio  # GIF rendering
                      godot_4
                    ])))
                    libsForQt5.qt5.qtwayland
                  ];

                  enterShell = ''
                    pv=`python --version`
                    echo "Welcome to gamasi, using $pv"
                  '';
                }
              ];
            };
          });
    };
}

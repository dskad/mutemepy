{
  description = "Python lybrary to control the MuteMe button";
  nixConfig.bash-prompt = "[nix(MuteME)]";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux.pkgs;

    in {
      devShells.x86_64-linux.default = pkgs.mkShell {
        name = "mutemepy dev environment";
        buildInputs = with pkgs; [
          python312
          python312Packages.pip
          python312Packages.hidapi
          python312Packages.pylint
          ruff
          isort
        ];
      };
    };
}

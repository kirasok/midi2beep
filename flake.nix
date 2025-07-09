{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };
  outputs =
    inputs@{ self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
      };
      dependencies = with pkgs.python3Packages; [ mido ];
    in
    {
      packages."${system}".default = pkgs.writers.writePython3Bin "midi2beep" {
        libraries = dependencies;
        flakeIgnore = [
          "F541"
          "E501"
        ];
      } ./midi2beep.py;
      overlays."${system}".default = final: prev: {
        midi2beep = self.packages."${system}".default;
      };
      devShells."${system}".default = pkgs.mkShell {
        buildInputs =
          dependencies
          ++ (with pkgs; [
            ruff
            basedpyright
            nixd
            nixfmt-rfc-style
          ]);
      };
    };
}

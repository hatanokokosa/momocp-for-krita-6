{
  description = "Momo Color Picker for Krita 6";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system:
        f (import nixpkgs { inherit system; }));
    in {
      packages = forAllSystems (pkgs:
        let
          python = pkgs.python3;
          pythonEnv = python.withPackages (ps: [ ps.numpy ]);
          source = pkgs.lib.cleanSourceWith {
            src = pkgs.lib.cleanSource ./.;
            filter = path: type:
              let relative = pkgs.lib.removePrefix "${toString ./.}/" (toString path);
              in !(pkgs.lib.hasPrefix "pykrita/hsv_picker/vendor" relative
                || pkgs.lib.hasPrefix "pykrita/hsv_picker/_python_dependencies" relative);
          };
          plugin = pkgs.stdenvNoCC.mkDerivation {
            pname = "momo-color-picker-plugin";
            version = "1.1.0";
            src = source;
            dontUnpack = true;
            installPhase = ''
              mkdir -p "$out/share/krita/pykrita" "$out/share/krita/actions"
              cp -r --no-preserve=mode "$src/pykrita/hsv_picker" "$out/share/krita/pykrita/"
              cp "$src/pykrita/hsv_picker.desktop" "$out/share/krita/pykrita/"
              cp "$src/LICENSE" "$out/share/krita/pykrita/hsv_picker/"
              cp "$src/pykrita/hsv_picker/actions/hsv_picker.action" "$out/share/krita/actions/"
              ln -s "${pythonEnv}/${python.sitePackages}" "$out/share/krita/pykrita/hsv_picker/_python_dependencies"
              find "$out" -type d -name __pycache__ -prune -exec rm -rf {} +
            '';
          };
          installer = pkgs.writeShellApplication {
            name = "install-momo-color-picker";
            runtimeInputs = [ python pkgs.nix ];
            text = ''exec ${python}/bin/python ${./tools/install_plugin.py} "${plugin}" "$@"'';
          };
        in {
          default = plugin;
          plugin = plugin;
          install-plugin = installer;
        });

      apps = forAllSystems (pkgs: {
        default = {
          type = "app";
          program = "${self.packages.${pkgs.system}.install-plugin}/bin/install-momo-color-picker";
        };
        install-plugin = {
          type = "app";
          program = "${self.packages.${pkgs.system}.install-plugin}/bin/install-momo-color-picker";
        };
      });

      devShells = forAllSystems (pkgs:
        let
          python = pkgs.python3;
          pythonEnv = python.withPackages (ps: [ ps.numpy ps.pyqt6 ]);
        in {
          default = pkgs.mkShell {
            packages = [ pkgs.krita pythonEnv ];
            shellHook = ''
              echo "Momo Color Picker development shell"
              echo "Use ordinary Krita after installing with nix run .#install-plugin."
            '';
          };
        });
    };
}

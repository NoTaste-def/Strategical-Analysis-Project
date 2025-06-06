import os
import yaml
import importlib

# macOS에 맞게 수정함.
# \\ 가 경로 구분자로 동작하지 않으므로 os.path.join()으로 수정함.

class ScenarioManager:
    def __init__(self, abs_path, sce_name="", apath="", dpath=""):
        attack_path = f"attack{apath}.model.torpedo"
        apkg = importlib.import_module(attack_path)

        defense_path = f"defense{dpath}.model.surfaceship"
        dpkg = importlib.import_module(defense_path)
        
        ship_cls = getattr(dpkg, 'SurfaceShip')
        torpedo_cls = getattr(apkg, 'Torpedo')

        # Read YAML file
        attack_yaml_path = os.path.join(abs_path, f"attack{apath}", "scenario", sce_name)
        with open(attack_yaml_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
            self.torpedoes = [torpedo_cls(f"red_torpedo_{idx}", d) for idx, d in enumerate(yaml_data['Torpedo'])]

        defense_yaml_path = os.path.join(abs_path, f"defense{dpath}", "scenario", sce_name)
        with open(defense_yaml_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
            self.surface_ships = [ship_cls(f"blue_ship_{idx}", d) for idx, d in enumerate(yaml_data['SurfaceShip'])]

    def get_surface_ships(self):
        return self.surface_ships

    def get_torpedoes(self):
        return self.torpedoes
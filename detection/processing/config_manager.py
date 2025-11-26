import json
import os
import shutil

CONFIG_PATH = "app/config/guardcar.json"

class ConfigManager:
    def __init__(self, path=CONFIG_PATH):
        self.path = path
        self.data = self.load()

    def load(self):
        with open(self.path, "r") as f:
            return json.load(f)

    def save(self):
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.data, f, indent=2)
        shutil.move(tmp, self.path)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def get_providers(self):
        return self.data.get("providers", {})

    def add_provider(self, name: str, provider_data: dict):
        providers = self.data.get("providers", {})
        providers[name] = provider_data
        self.data["providers"] = providers
        self.save()

    def remove_provider(self, name: str):
        providers = self.data.get("providers", {})
        if name in providers:
            del providers[name]
            self.data["providers"] = providers
            self.save()

    def set_active_provider(self, name: str):
        providers = self.data.get("providers", {})
        for p in providers:
            providers[p]["active"] = (p == name)
        self.data["providers"] = providers
        self.save()
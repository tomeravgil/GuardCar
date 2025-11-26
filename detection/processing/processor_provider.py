from detection.processing.processors.processor import Processor
import logging

logger = logging.getLogger(__name__)

class ProcessorProvider:

    def __init__(self):
        self.providers = {}
        self.selected_provider = None

    def register(self, name, provider: Processor):
        self.providers[name] = provider
        if self.selected_provider is None:
            self.selected_provider = provider

    def change_main_provider(self, name):
        try:
            self.selected_provider = self.providers[name]
            return True
        except KeyError:
            return False

    def find_next_cloud_provider(self, name):
        for provider in self.providers.keys():
            if provider != "local" and provider != name:
                return provider
        return "local"

    def get_selected_provider(self) -> Processor:
        return self.selected_provider

    async def remove_provider(self,name):
        try:
            provider = self.providers.pop(name)
            if hasattr(provider, "stop"):
                await provider.stop()
        except KeyError:
            logger.error(f"No provider named {name}")

from detection.processing.processors.processor import Processor


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

    def get_selected_provider(self) -> Processor:
        return self.selected_provider

    def remove_provider(self,name):
        del self.providers[name]

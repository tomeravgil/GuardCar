from detection.processing.processors.processor import Processor


class ProcessorProvider:

    def __init__(self):
        self.providers = {}

    def register(self, name, provider: Processor):
        self.providers[name] = provider

    def get_provider(self, name):
        return self.providers[name]

    def remove_provider(self,name):
        del self.providers[name]

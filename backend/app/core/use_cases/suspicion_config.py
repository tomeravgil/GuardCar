from pydantic import BaseModel
from rabbitMQ.consumer.connection_manager import Producer
from rabbitMQ.dtos.dto import SuspicionConfigMessage

class SuspicionConfigurationRequest(BaseModel):
    suspicion_level: int

class SuspicionConfigurationUseCase:
    def __init__(self, suspicion_config_producer: Producer):
        self.suspicion_config_producer = suspicion_config_producer

    def execute(self, request: SuspicionConfigurationRequest):
        self.suspicion_config_producer.publish(SuspicionConfigMessage(threshold=request.suspicion_level,
                                                                      class_weights=dict()))

from pydantic import BaseModel
from rabbitMQ.consumer.connection_manager import Producer
from rabbitMQ.dtos.dto import CloudProviderConfigMessage

class CloudConfigurationRequest(BaseModel):
    provider_name: str
    connection_ip: str
    server_certification: str


class CloudConfigurationDeleteRequest(BaseModel):
    provider_name: str


class CloudConfigurationConfigurationUseCase:
    def __init__(self, cloud_config_producer: Producer):
        self.cloud_config_producer = cloud_config_producer

    def create(self, request: CloudConfigurationRequest):
        cloud_config_message = CloudProviderConfigMessage(provider_name=request.provider_name,
                                                   connection_ip=request.connection_ip,
                                                   server_certification=request.server_certification,
                                                   delete=False)
        self.cloud_config_producer.publish(cloud_config_message)

    def delete(self,request: CloudConfigurationDeleteRequest):
        cloud_config_message = CloudProviderConfigMessage(provider_name=request.provider_name,
                                                          connection_ip="",
                                                          server_certification="",
                                                          delete=True)
        self.cloud_config_producer.publish(cloud_config_message)

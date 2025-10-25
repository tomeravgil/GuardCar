from abc import ABC, abstractmethod

class IServerSideEventsService(ABC):
    
    @abstractmethod
    def send_event(self, event: str, data: dict) -> None:
        pass

    @abstractmethod
    async def stream_events(self) -> None:
        pass
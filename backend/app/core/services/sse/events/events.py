from abc import abstractmethod
from dataclasses import dataclass
import json


@dataclass
class SSEEvent:
    """
    Represents a Server-Sent Event (SSE) with an event type and associated data.
    Extend this class to create specific event types as needed.
    """
    event: str

    # The payload of the event
    data: dict

    def to_sse_format(self) -> str:
        """
        Convert the event to a Server-Sent Events (SSE) formatted string.
        """
        data_str = json.dumps(self.data)
        return f"event: {self.event}\ndata: {data_str}\n\n"
    
    @abstractmethod
    def validate_event(self) -> bool:
        """
        Validate the event data.
        This method should be implemented by subclasses to ensure the event data is valid.
        """
        pass
    
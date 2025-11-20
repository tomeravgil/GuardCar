from abc import abstractmethod
from app.core.entities.suspicion import SuspicionLevel
class ISuspicionService:

    @abstractmethod
    def evaluate(self, score: int) -> SuspicionLevel:
        pass

class SuspicionService(ISuspicionService):

    def evaluate(self, score: int) -> SuspicionLevel:
        if score >= 20:
            return SuspicionLevel("danger", "your car is in danger")
        else:
            return SuspicionLevel("safe", "you're in the clear, buddy")
    

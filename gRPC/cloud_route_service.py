from gRPC.CloudRoute_pb2 import DetectionRequest, DetectionResult, Detection
from gRPC.CloudRoute_pb2_grpc import CloudRouteServicer
from detection.model.detection_service import DetectionService as InternalDetectionService
from detection.dto.detection_types import DetectionResult as InternalDetectionResult

class CloudRouteService(CloudRouteServicer):

    def __init__(self, cloud_model: InternalDetectionService):
        self.cloud_model = cloud_model

    def CloudRoute(self, request: DetectionRequest, context):
        return self.__convert_internal_dr_to_rpc_dr(self.cloud_model.detect(request.frame), request.frame_id)

    def CloudRouteStream(self, request_iterator, context):
        
        for request in request_iterator:
            yield self.__convert_internal_dr_to_rpc_dr(self.cloud_model.detect(request.frame), request.frame_id)

    def __convert_internal_dr_to_rpc_dr(self, detection_result: InternalDetectionResult, frame_id: int) -> DetectionResult:
        detections = []
        for detection in detection_result.detections:
            new_detection = Detection(class_id=detection.class_id, 
                                        class_name=detection.class_name, 
                                        confidence=detection.confidence, 
                                        x1=detection.bbox[0], 
                                        y1=detection.bbox[1], 
                                        x2=detection.bbox[2], 
                                        y2=detection.bbox[3])
            detections.append(new_detection)
        return DetectionResult(detections=detections, frame_id=frame_id)
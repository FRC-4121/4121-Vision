from camera.base import CameraBase
from typing import Optional
import numpy as np


# Show a single frame, pretending to be a camera
# If a frame is not given, use a black one
class SingleFrame(CameraBase):
    def __init__(
        self, name: str, timestamp: str, *, frame: Optional[np.ndarray] = None
    ):
        super().__init__(name, timestamp)
        self.frame = (
            frame if frame is not None else np.zeros((self.width, self.height, 3))
        )

    def read_frame_raw(self) -> (bool, np.ndarray):
        return True, self.frame

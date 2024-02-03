from vision.base import *
from threads import get_tls
import pyapriltags


def cvt_res(
    r: pyapriltags.Detection, cameraWidth: int, cameraHeight: int, cameraFOV: float
) -> FoundObject:
    xs = sorted([c[0] for c in r.corners])
    ys = sorted([c[1] for c in r.corners])
    w = int(xs[-1] - xs[0])
    h = int(ys[-1] - ys[0])
    x = int(r.center[0] - w // 2)
    y = int(r.center[1] - h // 2)

    return populate_obj(FoundObject(
        "TAG",
        x,
        y,
        w=w,
        h=h,
        ident=r.tag_id,
    ), 6.5, cameraWidth, cameraHeight, cameraFOV)


class AprilTagVisionLibrary(VisionBase):
    # Define class initialization
    def __init__(self):
        super()
        self.name = "APRIL"

    # Locates the cubes and cones in the game (2023)
    # returns a tuple containing (cubes, cones)
    def find_objects(
        self, imgRaw: np.ndarray, cameraWidth: int, cameraHeight: int, cameraFOV: int
    ) -> List[FoundObject]:
        detector = get_tls(
            "at_detect", lambda: pyapriltags.Detector(families="tag36h11")
        )
        gray = cv.cvtColor(imgRaw, cv.COLOR_BGR2GRAY)
        results = detector.detect(gray)

        return [cvt_res(r, cameraWidth, cameraHeight, cameraFOV) for r in results]

from vision.base import *
import pyapriltags

detector = pyapriltags.Detector(families="tag36h11")


def cvt_res(
    r: pyapriltags.Detection, cameraWidth: int, cameraHeight: int, cameraFOV: float
) -> FoundObject:
    xs = sorted([c[0] for c in r.corners])
    ys = sorted([c[1] for c in r.corners])
    w = int(xs[-1] - xs[0])
    h = int(ys[-1] - ys[0])
    x = int(r.center[0] - w // 2)
    y = int(r.center[1] - h // 2)
    inches_per_pixel = 6.5 / w  # set up a general conversion factor
    distanceToTargetPlane = inches_per_pixel * (
        cameraWidth / (2 * math.tan(math.radians(cameraFOV)))
    )
    offsetInInches = inches_per_pixel * ((x + (w / 2)) - (cameraWidth / 2))
    angleToObject = -1 * math.degrees(
        math.atan((offsetInInches / distanceToTargetPlane))
    )
    distanceToObject = math.cos(math.radians(angleToObject)) * distanceToTargetPlane
    screenPercent = w * h / (cameraWidth * cameraHeight)
    offset = -offsetInInches

    return FoundObject(
        "TAG",
        x,
        y,
        w=w,
        h=h,
        distance=distanceToObject,
        angle=angleToObject,
        offset=offset,
        percent=screenPercent,
        ident=r.tag_id,
    )


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
        gray = cv.cvtColor(imgRaw, cv.COLOR_BGR2GRAY)
        results = detector.detect(gray)

        return [cvt_res(r, cameraWidth, cameraHeight, cameraFOV) for r in results]

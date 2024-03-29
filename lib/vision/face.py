from vision.base import *


def calc_offset(x, w, width):
    return -(x + (w / 2)) * width / w


class FaceVisionLibrary(VisionBase):
    def __init__(self, path: str = "config/faces.xml"):
        self.haar = cv.CascadeClassifier(path)

    def find_objects(
        self, imgRaw: np.ndarray, cameraWidth: int, cameraHeight: int, cameraFOV: int
    ) -> List[FoundObject]:
        gray = cv.cvtColor(imgRaw, cv.COLOR_BGR2GRAY)
        faces = self.haar.detectMultiScale(
            gray,
            scaleFactor=self.cfg("SCALE", 1.1, float),
            minNeighbors=self.cfg("NEIGHBORS", 5, int),
            miSize=(self.cfg("MINWIDTH", 30, int), self.cfg("MINHEIGHT", 30, int)),
        )
        width = self.cfg("WIDTH", datatype=float)
        return [
            FoundObject("FACE", x=x, y=y, w=w, h=h, offset=calc_offset(x, w, width))
            for x, y, w, h in faces
        ]

from vision.base import VisionBase
from vision.rect import *

CubeVisionLibrary = lambda: RectVisionLibrary("CUBE")
ConeVisionLibrary = lambda: RectVisionLibrary("CONE")
TapeVisionLibrary = lambda: RectVisionLibrary("TAPE")
TapeRectVisionLibrary = TapeVisionLibrary
from vision.base import *

class RectVisionLibrary(VisionBase):

    # Define class initialization
    def __init__(self, name):
        self.name = name
        super()
    

    # Locates the cubes and cones in the game (2023)
    # returns a tuple containing (cubes, cones)
    def find_objects(self, imgRaw: np.ndarray, cameraWidth: int, cameraHeight: int, cameraFOV: int) -> List[FoundObject]:

        # Read configuration values from dictionary and make tuples
        HSVMin    = (self.cfg('HMIN',   0, int), self.cfg('SMIN',   0, int), self.cfg('VMIN',   0, int))
        HSVMax    = (self.cfg('HMAX', 255, int), self.cfg('SMAX', 255, int), self.cfg('VMAX', 255, int))
        minArea   = self.cfg('MINAREA', 0, int)
        tolerance = self.cfg('TOLERANCE', 10.0, float)
        minAspect = self.cfg('MINASPECT', 0.0, float, False)
        minVis    = self.cfg('MINVIS', 0.0, float, False)
        width     = self.cfg('WIDTH', None, float)
        height    = self.cfg('HEIGHT', None, float)
        recip     = self.cfg('RECIPROCAL', False, bool, False)
        aspect    = height / width
        
        # Initialize variables
        data = []

        # Find contours in the mask and clean up the return style from OpenCV
        contours = self.process_image_contours(imgRaw, HSVMin, HSVMax, False, False)
        if len(contours) > 0:

            contours.sort(key=cv.contourArea, reverse=True)
            for contour in contours:
                x, y, w, h = cv.boundingRect(contour)
                
                if w * h < minArea: # in pixel units
                    break
                
                if (
                    h / w < minAspect or 
                        (
                            abs(h / w / aspect - 1.0) > tolerance or 
                            (recip and abs(w / h / aspect - 1.0) > tolerance)
                        )
                    ):
                    continue
                if cv.contourArea(contour) / (w * h) < minVis:
                    continue
                # Calculate metrics
                inches_per_pixel = float(width) / w # set up a general conversion factor
                distanceToTargetPlane = inches_per_pixel * (cameraWidth / (2 * math.tan(math.radians(cameraFOV))))
                offsetInInches = inches_per_pixel * ((x + (w / 2)) - (cameraWidth / 2))
                angleToObject = -1 * math.degrees(math.atan((offsetInInches / distanceToTargetPlane)))
                distanceToObject = math.cos(math.radians(angleToObject)) * distanceToTargetPlane
                screenPercent = w * h / (cameraWidth * cameraHeight)
                offset = -offsetInInches
                
                data.append(FoundObject(self.name, x, y,
                    w=w,
                    h=h,
                    distance=distanceToObject,
                    angle=angleToObject,
                    offset=offset,
                    percent=screenPercent
                ))
        
        return data

CubeVisionLibrary = lambda: RectVisionLibrary("CUBE")
ConeVisionLibrary = lambda: RectVisionLibrary("CONE")
TapeVisionLibrary = lambda: RectVisionLibrary("TAPE")
TapeRectVisionLibrary = TapeVisionLibrary

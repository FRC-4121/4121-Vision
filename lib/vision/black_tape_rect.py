from vision.base import *

class BlackTapeRectVisionLibrary(VisionBase):

    # Define class initialization
    def __init__(self, cameraFocalLength, cameraMountHeight):
        
        self.cameraFocalLength = cameraFocalLength
        self.cameraMountHeight = cameraMountHeight

    # Locates the cubes and cones in the game (2023)
    # returns a tuple containing (cubes, cones)
    def find_objects(self, imgRaw, imageWidth, imageHeight, cameraFOV):
        
        # Read HSV values from dictionary and make tupples
        hMin = int(VisionBase.config["TAPE"]['HMIN'])
        hMax = int(VisionBase.config["TAPE"]['HMAX'])
        sMin = int(VisionBase.config["TAPE"]['SMIN'])
        sMax = int(VisionBase.config["TAPE"]['SMAX'])
        vMin = int(VisionBase.config["TAPE"]['VMIN'])
        vMax = int(VisionBase.config["TAPE"]['VMAX'])
        tapeHSVMin = (hMin, sMin, vMin)
        tapeHSVMax = (hMax, sMax, vMax)

        # Initialize processing values
        targetX = 1000 
        targetY = 1000
        targetW = 1000
        targetH = 1000
        aspectRatio = 0
        centerOffset = 0
        cameraAngle = 0
        actualVertAngle = 0
        botAngle = 0
        apparentTapeWidth = 0
        distanceArg = 0
        straightLineDistance = 1000
        distanceToTape = 1000
        distanceToWall = 1000
        horizAngleToTape = 0
        vertAngleToTape = 0
        inchesPerPixel = 0
        horizOffsetPixels = 0
        horizOffsetInInches = 0
        vertOffsetPixels = 0
        vertOffsetInInches = 0
        rect = None
        box = None

        # Initialize flags
        foundTape = False
        targetLock = False

        goalHeight = 98.0

        # Return dictionary
        tapeCameraValues = {}
        tapeRealWorldValues = {}
        
        # Find alignment tape in image
        tapeContours = self.process_image_contours(imgRaw, tapeHSVMin, tapeHSVMax, False, True)
  
        # Continue with processing if alignment tape found
        if len(tapeContours) > 0:

            # Find the largest contour and check it against the mininum tape area
            largestContour = max(tapeContours, key=cv.contourArea)
                        
            if cv.contourArea(largestContour) > int(VisionBase.config["TAPE"]['MINAREA']):
                
                # Find horizontal rectangle
                targetX, targetY, targetW, targetH = cv.boundingRect(largestContour)

                # Calculate aspect ratio
                aspectRatio = targetW / targetH

                # Find angled rectangle
                rect = cv.minAreaRect(largestContour)#((x, y), (h, w), angle)
                box = cv.boxPoints(rect)
                box = np.int0(box)

                # Find angle of bot to target
                angle = rect[2]
                if abs(angle) < 45:
                    cameraAngle = abs(angle)
                else:
                    cameraAngle = 90 - abs(angle)
                botAngle = 2 * cameraAngle

                # Set flag
                foundTape = True
                
            # Calculate real world values of found tape
            if foundTape:
                
                # Adjust tape size for robot angle
                apparentTapeWidth = float(VisionBase.config["TAPE"]['TAPEWIDTH']) * math.cos(math.radians(botAngle))
                
                # Calculate inches per pixel conversion factor
                inchesPerPixel = apparentTapeWidth / targetW

                # Find tape offsets
                horizOffsetPixels = (targetX + targetW/2) - imageWidth / 2
                horizOffsetInInches = inchesPerPixel * horizOffsetPixels
                vertOffsetPixels = (imageHeight / 2) - (targetY - targetH/2)
                vertOffsetInInches = inchesPerPixel * vertOffsetPixels
                centerOffset = -horizOffsetInInches
                
                # Calculate distance to tape
                straightLineDistance = apparentTapeWidth * self.cameraFocalLength / targetW
                distanceArg = math.pow(straightLineDistance, 2) - math.pow((float(VisionBase.config["TAPE"]['GOALHEIGHT']) - self.cameraMountHeight),2)
                if (distanceArg > 0):
                    distanceToTape = math.sqrt(distanceArg)
                distanceToWall = distanceToTape / math.cos(math.radians(botAngle))                

                # Find tape offsets
                horizAngleToTape = math.degrees(math.atan((horizOffsetInInches / distanceToTape)))
                vertAngleToTape = math.degrees(math.atan((vertOffsetInInches / distanceToTape)))

                # Determine if we have target lock
                if abs(horizOffsetInInches) <= float(VisionBase.config["TAPE"]['LOCKTOLERANCE']):
                    targetLock = True


        return ({
            'TargetX': targetX,
            'TargetY': targetY,
            'TargetW': targetW,
            'TargetH': targetH,
            'IPP': inchesPerPixel,
            'Offset': horizOffsetPixels
        },
        {
            'AspectRatio': aspectRatio,
            'CenterOffset': centerOffset,
            'StraightDistance': straightLineDistance,
            'TapeDistance': distanceToTape,
            'WallDistance': distanceToWall,
            'HAngle': horizAngleToTape,
            'VAngle': vertAngleToTape,
            'TargetRotation': cameraAngle,
            'BotAngle': botAngle,
            'ApparentWidth': apparentTapeWidth,
            'VertOffset': vertOffsetInInches
        }, foundTape, targetLock, rect, box)
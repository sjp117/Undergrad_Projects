# LiveTrack-PsychoPy-Calibration.py
# version 1.0
# 05/2018 JT
# 09/2018 edits Britt
# 09/2019 edit SJP

import LiveTrack
import numpy as np
import math
import time
from psychopy import visual, core, monitors, misc


if __name__ == '__main__':
    nPtsX = 5
    nPtsY = 4

    #replace hardcoded monitor name

    calibTargRad = 1.0

    mon = monitors.Monitor('crtFP2141SB')
    if mon.getWidth() is not None:
        #means that there was a file that read in something
        sX,sY = mon.getSizePix()
        print((sX,sY))
        minX = misc.pix2deg(-1 * round(sX/2.0) + misc.deg2pix(calibTargRad,mon),mon)
        print(minX)
        maxX = -1 * minX
        minY = misc.pix2deg(-1 * round(sY/2.0) + misc.deg2pix(calibTargRad,mon),mon)
        print(minY)
        maxY = -1 * minY
        targetsDeg = np.array([[x,y] for x in np.linspace(minX,maxX,nPtsX) for y in np.linspace(minY,maxY,nPtsY)])
        print(targetsDeg)
        screenRes = [sX,sY]
        screenSize = [10*mon.getWidth(),230];#need to hardcode height
        print(screenSize)
        viewDist = 10.0*mon.getDistance()
        print(viewDist)
        #core.quit()
    else:
        targetsDeg = np.array([[-5,-5],[0,-5],[5,-5],[-5,0],[0,0],[5,0],[-5,5],[0,5],[5,5]])
        screenRes = [1360,768]
        screenSize = [410,230]
        viewDist = 830 # viewing distance in mm



    # This script calibrated LiveTrack using PsychoPy. After Calibration the results1
    # will be in screen pixels with origin at the centre of the screen
    # %% User Input

    useVideo = False # set to True to show video while calibrating (to allow camera alignment)


    # Define the default location of the the fixation targets in degrees
    # (origin at the centre, x-positive=right, y-positive=down)

    # Time before getting data from fixation (to ignore initial saccade)
    setupDelay = 1000.0 # duration in mS

    # Define the minimum amount of time required for each fixation (in mS) -
    # decrease to make calibration "easier"/faster
    minDur = 1200 # fixation duration in mS

    # Time limit for aquiring fixation - if a fixation has not been aquired
    # within this time, the fixation point will be skipped.
    fixTimeout = 5  # timeout duration in seconds

    # Fixation threshold in camera pixels (all samples taken wihtin the "minDur"
    # time must be within this threshold) - increase this to make the
    # calibration "easier" (e.g. for subjects with difficulties making precise
    # eye fixations)
    fixThreshold = 3.1

    # Define the diameter of the fixation points (in degrees of visual angle)
    fixDotInDeg = calibTargRad#0.3 # inner circle
    fixDotOutDeg = 2.0*calibTargRad#0.6 # outer circle

    # Randomize the order of the targets:
    s = np.shape(targetsDeg)
    order = np.arange(s[0])
    np.random.shuffle(order)
    targetsDeg2 = targetsDeg.astype(float)
    for x in range(0,s[0]):
        targetsDeg2[x] = targetsDeg[order[x]]

    # Calculate pixel size (in mm) assuming square pixels
    pixSize = float(screenSize[0])/float(screenRes[0])

    # Caliculate millimetres per degree (NB. Only accurate for small eye angles)
    MMperDeg = math.tan(1/(180/math.pi))*viewDist

    # Calculate pixels per degree
    pixPerDeg = MMperDeg/pixSize

    # Target locations in screen pixel coordinates
    cnrTarget = [0,0]
    tgtLocs = targetsDeg2.astype(float)
    tgtLocs[:,0] = np.round(targetsDeg2[:,0]*pixPerDeg+cnrTarget[0])
    tgtLocs[:,1] = np.round(targetsDeg2[:,1]*pixPerDeg+cnrTarget[1])

    # Calculate the diameter of the fixation points (in pixels on the monitor)
    fixDotInPix = fixDotInDeg*pixPerDeg
    fixDotOutPix = fixDotOutDeg*pixPerDeg


    # %% Setup LiveTrack
    if useVideo:
        print('Please align camera')
        import LiveTrackGS
        LiveTrackGS.VideoInit(0)
        result= LiveTrackGS.VideoStart()
        time.sleep(5)

    # Start LiveTrack raw data streaming
    LiveTrack.SetResultsTypeRaw()

    # Get an estimate of the sample rate
    [ width, height, sampleRate, offsetX, offsetY ] = LiveTrack.GetCaptureConfig()

    # Calculate how many data samples the fixation duration (fixDur) contains
    fixDurSamples = round((float(minDur)/1000)*float(sampleRate))

    # Find out which eye to get fixation data from
    [trackLeftEye, trackRightEye] = LiveTrack.GetTracking()

    # %%

    win = visual.Window(monitor=mon, size = (sX,sY), units="pix", fullscr=True, screen=0)

    VectXL = [None] * s[0]
    VectYL = [None] * s[0]
    GlintXL = [None] * s[0]
    GlintYL = [None] * s[0]
    VectXR = [None] * s[0]
    VectYR = [None] * s[0]
    GlintXR = [None] * s[0]
    GlintYR = [None] * s[0]

    for i in range(0,s[0]):
        # plot a circle at the fixation position.
        dot = visual.Circle(win,units='pix',radius=fixDotOutPix/2,fillColor=[-1] * 3,lineColor=[-1] * 3,pos=[tgtLocs[i,0],tgtLocs[i,1]]) # outer circle
        dot.draw()
        dot = visual.Circle(win,units='pix',radius=fixDotInPix/2,fillColor=[1] * 3,lineColor=[-1] * 3,pos=[tgtLocs[i,0],tgtLocs[i,1]]) # inner circle
        dot.draw()
        win.flip()

        # This flag will be set to true when a valid fixation has been acquired
        gotFixLeft = 0;
        gotFixRight = 0;

        t0 = time.time() # reset fixation timer

        # Loop until fixation data has been aquired for this dot (or timed out)
        while 1:
            d = LiveTrack.GetBufferedEyePositions(0,fixDurSamples,0)
            VectX = LiveTrack.GetFieldAsList(d,'VectX')
            VectY = LiveTrack.GetFieldAsList(d,'VectY')
            GlintX = LiveTrack.GetFieldAsList(d,'GlintX')
            GlintY = LiveTrack.GetFieldAsList(d,'GlintY')
            Tracked = LiveTrack.GetFieldAsList(d,'Tracked')
            VectXRight = LiveTrack.GetFieldAsList(d,'VectXRight')
            VectYRight = LiveTrack.GetFieldAsList(d,'VectYRight')
            GlintXRight = LiveTrack.GetFieldAsList(d,'GlintXRight')
            GlintYRight = LiveTrack.GetFieldAsList(d,'GlintYRight')
            TrackedRight = LiveTrack.GetFieldAsList(d,'TrackedRight')

            # Calculate the maximum difference in the pupil-to-glint
            # vectors for the samples in the buffer, for left eye
            pgDistL = max([max(VectX)-min(VectX),max(VectY)-min(VectY)])

            # and for the right eye
            pgDistR = max([max(VectXRight)-min(VectXRight),max(VectYRight)-min(VectYRight)])

            # Check if the maximum vector difference is within the defined
            # limit for a fixation (fixWindow) and all samples are tracked, and
            # the time to wait for fixations (waitTimeForFix) has passed, for
            # the left eye
            if pgDistL<=fixThreshold and np.all(Tracked) and (time.time()-t0)>setupDelay/1000:
                # Check if there are enough samples in the buffer for the
                # defined duration (fixDurSamples)
                if len(d)>=fixDurSamples and gotFixLeft==0:
                    # save the data for this fixation
                    VectXL[i] = np.median(VectX)
                    VectYL[i] = np.median(VectY)
                    GlintXL[i] = np.median(GlintX)
                    GlintYL[i] = np.median(GlintY)
                    print('Fixation #',str(i+1),': Found valid fixation for left eye')
                    gotFixLeft = 1 # good fixation aquired

            # and for the right eye
            if pgDistR<=fixThreshold and np.all(TrackedRight) and (time.time()-t0)>setupDelay/1000:
                # Check if there are enough samples in the buffer for the
                # defined duration (fixDurSamples)
                if  len(d)>=fixDurSamples and gotFixRight==0:
                    # save the data for this fixation
                    VectXR[i] = np.median(VectXRight)
                    VectYR[i] = np.median(VectYRight)
                    GlintXR[i] = np.median(GlintXRight)
                    GlintYR[i] = np.median(GlintYRight)
                    print('Fixation #',str(i+1),': Found valid fixation for right eye')
                    gotFixRight = 1 # good fixation aquired

            if (time.time()-t0)>fixTimeout:
                if not gotFixLeft and trackLeftEye>0:
                    print('Fixation #',str(i+1),': Did not get fixation for left eye (timeout)')
                if not gotFixRight and trackRightEye>0:
                    print('Fixation #',str(i+1),': Did not get fixation for right eye (timeout)')
                break # fixation timed out


            # Exit if all eyes that are enabled have got a fixation
            if (gotFixLeft or trackLeftEye==False) and (gotFixRight or trackRightEye==False):
                win.flip()
                break


    # close the PsychoPy window
    win.close()

    # Clear the data in the buffer
    LiveTrack.ClearDataBuffer()


    # %% remove failed fixations from data

    # left eye
    failedFixL = []
    for i in range(0,len(VectXL)):
        if VectXL[i] is None:
            failedFixL.append(i)

    VectXL = np.delete(VectXL, failedFixL).tolist()
    VectYL = np.delete(VectYL, failedFixL).tolist()
    GlintXL = np.delete(GlintXL, failedFixL).tolist()
    GlintYL = np.delete(GlintYL, failedFixL).tolist()
    tgtLocsXL = np.delete(tgtLocs[:,0], failedFixL).tolist()
    tgtLocsYL = np.delete(tgtLocs[:,1], failedFixL).tolist()

    # right eye
    failedFixR = []
    for i in range(0,len(VectXR)):
        if VectXR[i] is None:
            failedFixR.append(i)

    VectXR = np.delete(VectXR, failedFixR).tolist()
    VectYR = np.delete(VectYR, failedFixR).tolist()
    GlintXR = np.delete(GlintXR, failedFixR).tolist()
    GlintYR = np.delete(GlintYR, failedFixR).tolist()
    tgtLocsXR = np.delete(tgtLocs[:,0], failedFixR).tolist()
    tgtLocsYR = np.delete(tgtLocs[:,1], failedFixR).tolist()

    # %% send fixation data to LiveTrack to calibrate

    if trackLeftEye:
        calErrL = LiveTrack.CalibrateDevice(0, len(tgtLocsXL), tgtLocsXL, tgtLocsYL, VectXL, VectYL, viewDist, np.median(GlintXL), np.median(GlintYL))
        print('Left eye calibration accuraccy: ',str(math.sqrt(float(calErrL)/len(tgtLocsXL))), 'pixels')
        print('Left eye calibration accuraccy: ',str(math.sqrt(float(calErrL)/len(tgtLocsXL))/pixPerDeg), 'degrees of visual angle')

    if trackRightEye:
        calErrR = LiveTrack.CalibrateDevice(1, len(tgtLocsXR), tgtLocsXR, tgtLocsYR, VectXR, VectYR, viewDist, np.median(GlintXR), np.median(GlintYR))
        print('Left eye calibration accuraccy: ',str(math.sqrt(float(calErrR)/len(tgtLocsXR))), 'pixels')
        print('Left eye calibration accuraccy: ',str(math.sqrt(float(calErrR)/len(tgtLocsXR))/pixPerDeg), 'degrees of visual angle')

    # %% plot the estimated fixation locations for the calibration

    #if trackLeftEye:
    #    [gazeXL, gazeYL] = LiveTrack.CalcGaze(0, len(tgtLocsXL), VectXL, VectYL)
    #
    #if trackRightEye:
    #    [gazeXR, gazeYR] = LiveTrack.CalcGaze(1, len(tgtLocsXR), VectXR, VectYR)

    gazeXL = [x+10 for x in tgtLocsXL]
    gazeYL = [x+10 for x in tgtLocsYL]
    gazeXR = [x-10 for x in tgtLocsXR]
    gazeYR = [x-10 for x in tgtLocsYR]

    LiveTrack.SetResultsTypeCalibrated()

    if useVideo:
        LiveTrackGS.VideoStop()

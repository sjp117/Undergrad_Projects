#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Author  : Sungjoon Park
# Created : 09/19/2019
# =============================================================================
"""
This is my protocol script for my research project "Mental Model Updating and
Pupil Response".
"""
# =============================================================================

import numpy as np
import random
import pandas as pd
import LiveTrack as lt
import pickle
import calibrate
import psychtoolbox as ptb
from psychopy import visual, core, event, gui, prefs
prefs.hardware['audioLib'] = ['PTB']
from psychopy import sound
from time import sleep
from threading import Thread
from copy import deepcopy
from os import makedirs, umask

print(sound.Sound)

# variables
# set window parameter
win0 = visual.Window(size=(600, 600),
                     color=(.5, .5, .5),
                     fullscr=True,
                     monitor='crtFP2141SB',
                     units='deg',
                     screen=1
                     )

# Visual elements
# fixation dot

fixStim = visual.Circle(win=win0, radius=0.4, edges=32, fillColor='white')

# shape/color stimuli
sqSize = 10
cirSize = 5
stimLineW = 2
blueVal = [0, 0, 1]
greenVal = [0, 0.5, 0]
stim_BluSqr = visual.Rect(win=win0,
                          size=sqSize,
                          fillColor=blueVal,
                          lineColor=(-1, -1, -1),
                          lineWidth=stimLineW
                          )

stim_BluCir = visual.Circle(win=win0,
                            size=cirSize,
                            fillColor=blueVal,
                            lineColor=(-1, -1, -1),
                            edges=99,
                            lineWidth=stimLineW
                            )

stim_GreSqr = visual.Rect(win=win0,
                          size=sqSize,
                          fillColor=greenVal,
                          lineColor=(-1, -1, -1),
                          lineWidth=stimLineW
                          )

stim_GreCir = visual.Circle(win=win0,
                            size=cirSize,
                            fillColor=greenVal,
                            lineColor=(-1, -1, -1),
                            edges=99,
                            lineWidth=stimLineW
                            )

stim = 0

# buttons for shape/color selection
downNotSelect = visual.ImageStim(win=win0,
                                 image="images/downNotSelect.png",
                                 pos=(0, -2)
                                 )

upNotSelect = visual.ImageStim(win=win0,
                               image="images/upNotSelect.png",
                               pos=(0, 2)
                               )


downSelect = visual.ImageStim(win=win0,
                              image="images/downSelect.png",
                              pos=(0, -2)
                              )

upSelect = visual.ImageStim(win=win0,
                            image="images/upSelect.png",
                            pos=(0, 2)
                            )

refStimUp = None
refStimDown = None

# confidence rating bar
confRatingScale = visual.Slider(win=win0, name='slider',
                                size=(10, 1), pos=(0, 0),
                                labels=None, ticks=(0, 20),
                                granularity=0, style=('slider',),
                                color='white', font='HelveticaBold',
                                flip=False)

scaleLabelList = ["COLOR", "SHAPE"]

scaleLabelLeft = visual.TextStim(win=win0,
                                 text=None,
                                 pos=(-7, 0),
                                 height=0.6,
                                 color=(1, 1, 1))

scaleLabelRight = visual.TextStim(win=win0,
                                  text=None,
                                  pos=(7, 0),
                                  height=0.6,
                                  color=(1, 1, 1))

# feedback
# audio
soundList = ['sound/sine700_0_5.wav', 'sound/sine400_0_8.wav']

noResp = visual.TextStim(win=win0,
                         text="No response!\nThis trial is skipped."
                         )

# debugging variables
doIntro = True
doPractice = True
doExp = True
doSave = True

# points screen
pointsScreen = visual.TextStim(win=win0, text="= 0")

# arrays
stimList = [stim_BluSqr, stim_BluCir, stim_GreSqr, stim_GreCir]
probConds = [0.75, 0.90]

dictInfo = {'version': 0, 'partID': "", 'gender': "m/f", 'age': "",
            'mascara': "y/n", 'glasses': "y/n", 'contactLens': "y/n",
            'session#': "", 'debug': "", 'blueEyes': "y/n"}

trialDataKeys = ['trialTotal', 'blockTrial', 'block', 'contingentCond',
                 'probCond', 'respSuccess', 'stimDisplayed', 'correctAnswer',
                 'choice', 'isCorrect', 'isForcedError', 'surpriseType',
                 'confRating', 'pointsStartTime', 'pointsEndTime', 'stimStartTime',
                 'stimEndTime', 'respStartTime', 'respEndTime', 'fixStartTime',
                 'fixEndTime', 'feedbackStartTime', 'feedbackEndTime', 'noRespStartTime',
                 'noRespEndTime', 'choiceHist', 'ratingHist', 'points']

trialDataDict = dict.fromkeys(trialDataKeys)
trialDataDict['points'] = 0
trialDataDict['trialTotal'] = -1

participantNumber = 123  # participand number code (dummy for now)
trialNumbTotal = 0

# switches for backup thread
backupCheck = True  # switch to keep backup thread going
trialCheck = False  # switch to trigger backup to initiate

refreshRate = int(round(win0.getActualFrameRate()))

# text variables
# Instruction section texts

introText1 = """
    In this experiment, you can imagine that you are on a quest in search of gold.\n
    On your journey, you will come across a sign that will guide you to where the gold is.\n
    The sign will be one of two shapes with one of two colors.\n
    One type of color and shape will signal up and the other color and shape will signal down.\n
    Press [space] to continue"""
introText2 = """
    On any series of trials, either the shape or the color will reliably guide you to the treasure.\n
    There will be no occasions where both shapes and colors are reliable guides at the same time.\n
    Choose wisely on whether you will trust the shape or the color.\n
    And be on your toes, as the reliable guide will change.\n
    Press [space] to continue"""
introText3 = """
    When the shape is the reliable guide, 'SQUARE' will signal 'UP' and 'CIRCLE' will signal 'DOWN'.\n
    When the color is the reliable guide, 'GREEN' will signal 'UP' and 'BLUE' will signal 'DOWN'.\n
    Note that the guide will not always be correct.\n
    There will always be a small chance for the correct guide to be mistaken.\n
    Press [space] to continue"""
introText3v2 = """
    When the shape is the reliable guide, 'CIRCLE' will signal 'UP' and 'SQUARE' will signal 'DOWN'.\n
    When the color is the reliable guide, 'BLUE' will signal 'UP' and 'GREEN' will signal 'DOWN'.\n
    Note that the guide will not always be correct.\n
    There will always be a chance for the correct guide to be mistaken.\n
    Press [space] to continue"""
introText4 = """
    After seeing the sign, you will make your decision to go 'UP' or 'DOWN' by pressing a button.\n
    And you will need to indicate how confident you feel that either the shape or the color is the reliable guide.\n
    You will indicate your confidence by clicking on a slider that says 'SHAPE' and 'COLOR' on either ends.\n
    Click closer to the ends, if you feel more confident.\n
    Press [space] to continue"""
introText5 = """
    After making your responses, you will be given a feedback on whether you made the correct choice.\n
    If you made the correct choice, you will hear a 'HIGH' tone sound.\n
    If you made the wrong choice, you will hear a 'LOW' tone sound.\n
    After hearing the result, you will see your success rate in percentage.\n
    This will be the end of a trial and and you will repeat this process.\n\n
    If you wish to read the instructions again, press [r]\n
    Press [Space] to move on."""
introText5v2 = """
    After making your responses, you will be given a feedback on whether you made the correct choice.\n
    If you made the correct choice, you will hear a 'LOW' tone sound.\n
    If you made the wrong choice, you will hear a 'HIGH' tone sound.\n
    After hearing the result, you will see your success rate in percentage.\n
    This will be the end of a trial and and you will repeat this process.\n\n
    If you wish to read the instructions again, press [r]\n
    Press [Space] to move on."""

# Practice section texts
practiceText1 = """
    Before starting the practice trials, we will calibrate the eye tracker.\n
    press [c] to start calibration."""
practiceText2 = """
    For the practice trials, the goal is for you to become familiar with your task.\n
    The first set of trials will have no time limit. However, the rest of the trials will have a time limit.\n
    For the first four trials the color will be the reliable guide. 'GREEN' means 'UP', 'BLUE' means 'DOWN'\n
    For the latter four trials the shape will be the reliable guide. 'SQUARE' means 'UP', 'CIRCLE' means 'DOWN'\n
    To start the practice trials, press [space]"""
practiceText2v2 = """
    For the practice trials, the goal is for you to become familiar with your task.\n
    The first set of trials will have no time limit. However, the rest of the trials will have a time limit.\n
	For the first four trials the color will be the reliable guide. 'BLUE' means 'UP', 'GREEN' means 'DOWN'\n
    For the latter four trials the shape will be the reliable guide. 'CIRCLE' means 'UP', 'SQUARE' means 'DOWN'\n
    To start the practice trials, press [space]"""
practiceText3 = """
    You have finished the untimed practice trials\n
    If you wish to repeat it, press [r]\n
    If you wish to move on to the timed practice trials, press [space]"""
practiceText4 = """
    You have finished the timed practice trials\n
    If you wish to repeat it, press [r]\n
    If you wish to move on to the experimental trials, press [space]"""

# Experimental section texts
expText1 = """
    We will perform a calibration before starting the experimental trials.\n
    Press [c] to calibrate."""
expText2 = """
    You are about to proceed to the experimental trials.\n
    If you have any question for the researcher, please ask now.\n
    If you are ready to proceed, press [space]"""

breakText = """
    BREAK!\n
    You may take your head off the chin-rest and relax.\n
    Simply inform the investigator when you are ready to continue."""

calibStartText = """
    For calibration, please stare at the dots that appear on the screen.\n
    Please do not move your eyes to a different part of the screen until the next dot appears.
    Press [Space] to start."""

calibEndText = """
    Calibration finished.\n
    Press [Space] to continue with the experiment."""


# Misc Commands
def shutDown():
    visual.TextStim(win=win0, text="Shuting Down...")
    win0.flip()
    lt.StopTracking()
    lt.Close()
    win0.close()
    core.quit()


def doCalibrate():
    visual.TextStim(win=win0, text=f"{calibStartText}", height=0.9).draw()
    win0.flip()
    keys = event.waitKeys(keyList=['space'])
    win0.flip()
    calibrate.main()
    visual.TextStim(win=win0, text=f"{calibEndText}", height=0.9).draw()
    win0.flip()
    keys = event.waitKeys(keyList=['space'])
    win0.flip()


def getdict(struct):
    # this function returns a dictionary of the cython data structure (eye data)
    return dict((field, getattr(struct, field)) for field, _ in struct._fields_)


# Helper Functions
def randIntNoRepeat(numb, min, max):
    """Function to create a list of integers that do not repeat subsequently.
    This is being used to create a list of which stimulus to present.
    Input: number of elements,
           minimum integer value
           maximum integer value
    Output: a list of
    """
    outList = []
    for i in range(numb):
        if len(outList) == 0:
            outList.append(random.randint(min, max))
        else:
            while True:
                pick = random.randint(min, max)
                if outList[-1] != pick:
                    outList.append(pick)
                    break
    return outList


def randIntListSetTotal(nVal=1, meanVal=0, minVal=0, maxVal=0, reapVal=0):
    """Returns a list of random integers This funciton generates a list of random
    integers from a normal distribution with a mean(meanVal), miminum(minVal),
    and maximum(maxVal) values.
    The sum of the list will == the product of mean(meanVal) and number of
    elements(nVal) specified.
    """
    total = nVal * meanVal
    if maxVal == 0:     # if no max value is specified it will default to total
                        # thus impossible to be met.
        maxVal = total
    while True:         # loop indefinitely (exit condition later)
        outputList = []
        # initial an empty list to be filled with our random values
        for i in range(nVal):
            # this loop will be as long as the number of value
            # specified (default to 1)
            if i == 0:
                outputList.append(random.randrange(minVal, maxVal))
                # appends a random integer between min and max value
            else:
                while True:
                    tempInt = random.randrange(minVal, maxVal)
                    if abs(outputList[-1] - tempInt) >= reapVal:
                        outputList.append(tempInt)
                        break
        if sum(outputList) == total:
            # if sum of the values meets desired total value, exit the loop
            break
    return(outputList)


def makeContingentBlockList(input):
    """Return a list of alternating 0s and 1s
    start of the sequence will be random, the list will be used to map the
    contingent condition (0 == shape, 1 == color)
    """
    outputList = []     # initiate an empty list
    outputList.append(np.random.randint(2))     # make first element random
    # since first element is alread set, loop for 1 element less
    for i in range(len(input) - 1):
        if outputList[-1] == 0:     # if last element is 0, append 1
            outputList.append(1)
        else:
            outputList[-1] == 1     # if last element is 1, append 0
            outputList.append(0)
    return outputList


def makeProbabilityConditionList(input):
    """Returns a list alternating values from the probability list
    in my case, the two values represent high and low probability conditions,
    probConds = [0.75,0.90]
    """
    while True:
        outputList = []     # initiate empty list
        for i in range(len(input)):     # iterate the length of input list
            if (i % 2) == 0:  # determine if element position is even (if divisible by 2)
                            # 0 is considered even
                # set prob to a random integer (0 or 1)
                prob = random.randint(0, 1)
                outputList.append(prob)  # append list with new prob value
            elif (i % 2) == 1:    # if element position is odd
                # append list with the same prob value as before
                outputList.append(prob)
        avgList = sum(outputList) / len(outputList)
        if avgList > 0.3 and avgList < 0.7:
            break
    return outputList


def debugging():
    global doIntro
    global doPractice
    global doExp
    global doSave
    if dictInfo['debug'] == "1":      # skip introduction
        doIntro = False
    elif dictInfo['debug'] == "2":    # skip practice
        doPractice = False
    elif dictInfo['debug'] == "3":    # only experimental trials
        doIntro = False
        doPractice = False
    elif dictInfo['debug'] == "4":    # only experimental trials, no save
        doIntro = False
        doPractice = False
        doSave = False
    elif dictInfo['debug'] == "5":    # only intro
        doPractice = False
        doExp = False
    elif dictInfo['debug'] == "6":    # only practice
        doIntro = False
        doExp = False
    elif dictInfo['debug'] == "7":    # nothing
        doIntro = False
        doPractice = False
        doExp = False


def introduction():
    visual.TextStim(win=win0, text=f"{introText1}", height=0.9).draw()
    win0.flip()
    keys = event.waitKeys(keyList=['space'])
    visual.TextStim(win=win0, text=f"{introText2}", height=0.9).draw()
    win0.flip()
    keys = event.waitKeys(keyList=['space'])
    if dictInfo['version'] == 0:
        visual.TextStim(win=win0, text=f"{introText3}", height=0.9).draw()
    elif dictInfo['version'] == 1:
        visual.TextStim(win=win0, text=f"{introText3v2}", height=0.9).draw()
    win0.flip()
    keys = event.waitKeys(keyList=['space'])
    visual.TextStim(win=win0, text=f"{introText4}", height=0.9).draw()
    win0.flip()
    keys = event.waitKeys(keyList=['space'])
    if dictInfo['version'] == 0:
        visual.TextStim(win=win0, text=f"{introText5}", height=0.8).draw()
    elif dictInfo['version'] == 1:
        visual.TextStim(win=win0, text=f"{introText5v2}", height=0.8).draw()
    win0.flip()
    keys = event.waitKeys(keyList=['space', 'r'])
    if keys[-1] == 'r':
        introduction()


def breakSection():
    lt.StopTracking()
    visual.TextStim(win=win0, text=f"{breakText}", height=0.9).draw()
    win0.flip()
    keys = event.waitKeys(keyList=['space'])
    lt.StartTracking()


# Main protocol scenes
def percentFixationScreen(duration=1):
    """Show a fixation screen with points on the center instead of a cross
    """
    trialDataDict['pointsStartTime'] = lt.GetLastResult().Timestamp
    if trialDataDict['trialTotal'] == 0:
        pointsScreen = visual.TextStim(win=win0, text='')
    else:
        percent = round(
            trialDataDict['points'] / ((trialDataDict['trialTotal']) * 10) * 100, 2)
        pointsScreen = visual.TextStim(win=win0, text=f"{percent}%")
    for frameN in range(duration * refreshRate):
        if event.getKeys(keyList=['escape']):
            break
        pointsScreen.draw()
        win0.flip()
    trialDataDict['pointsEndTime'] = lt.GetLastResult().Timestamp


def stimulusScreen(duration=2):
    """Show a random stimulus for a duration of time(s)
    Stimulus is chosn from a list of stimuli named "stimList"
    """
    global stim
    # choose a random stimulus from the stimulus list
    if doPractice == True:
        stim = stimList[trialDataDict['blockTrial']]
    else:
        trialDataDict['stimDisplayed'] = stimSequence[trialDataDict['trialTotal']]
        stim = stimList[trialDataDict['stimDisplayed']]
    trialDataDict['stimStartTime'] = lt.GetLastResult().Timestamp
    for frameN in range(duration * refreshRate):
        if event.getKeys(keyList=['escape']):
            break
        stim.draw()
        win0.flip()
    trialDataDict['stimEndTime'] = lt.GetLastResult().Timestamp


def responseScreen(duration=5):
    """Show the response screen where participant makes a choice and report
    their confidence with the slider
    """

    trialDataDict['choice'] = None
    choiceCounter = 0

    # initiate mouse and center it on screen
    mouse = event.Mouse(win=win0, newPos=[0, 0])
    responseCheck = False   # switch that checks if all responses have been made
    buttonCheck = False     # tracks if button choice has been made
    down = False
    up = False
    choiceList = []
    timer = core.Clock()
    # keeps looping while responses are not made and before the end of duration
    trialDataDict['respStartTime'] = lt.GetLastResult().Timestamp
    for frameN in range(duration * refreshRate) or responseCheck == False:
        # exit loop if 'escape' pressed
        if event.getKeys(keyList=['escape']):
            break
        # when no choice is made
        if buttonCheck == False:
            downNotSelect.draw()    # keep drawing unselected buttons
            upNotSelect.draw()
        # signal that 'UP' was chosen
        if mouse.isPressedIn(upNotSelect):
            choiceCounter += 1
            buttonCheck = True
            trialDataDict['choice'] = 1  # Up
            if up == False:
                choiceList.append([trialDataDict['choice'], timer.getTime()])
                up = True
                down = False
        # signal that 'Down' was chosen
        if mouse.isPressedIn(downNotSelect):
            choiceCounter += 1
            buttonCheck = True
            trialDataDict['choice'] = 0  # Down
            if down == False:
                choiceList.append([trialDataDict['choice'], timer.getTime()])
                up = False
                down = True
        # check if a choice was made
        if buttonCheck == True:
            # if 'DOWN' was chosen, draw appropriate buttons
            if trialDataDict['choice'] == 1:
                downNotSelect.draw()
                upSelect.draw()
            # if 'UP' was chosen, draw appropriate buttons
            elif trialDataDict['choice'] == 0:
                downSelect.draw()
                upNotSelect.draw()
        confRatingScale.draw()
        scaleLabelLeft.draw()
        scaleLabelRight.draw()
        refStimUp.draw()
        refStimDown.draw()
        win0.flip()

        # AUTOMATION
   # buttonCheck = True
   # trialDataDict['choice'] = np.random.choice(2)
   # trialDataDict['confRating'] = float(np.random.choice(20))
        # REVERT BELOW COMMAND WHEN NOT AUTOMATING: confRatingValue

    trialDataDict['confRating'] = confRatingScale.getRating()
    trialDataDict['ratingHist'] = confRatingScale.getHistory()
    if buttonCheck == False or trialDataDict['confRating'] == None:
        trialDataDict['respSuccess'] = 0
    else:
        responseCheck = True
        trialDataDict['respSuccess'] = 1
        trialDataDict['choiceHist'] = choiceList
        trialDataDict['noRespStartTime'] = None
        trialDataDict['noRespEndTime'] = None
    # else error screen
    confRatingScale.reset()  # reset for next input
    trialDataDict['respEndTime'] = lt.GetLastResult().Timestamp


def noRespScreen(duration=3):
    switch = True
    trialDataDict['noRespStartTime'] = lt.GetLastResult().Timestamp
    for frameN in range(duration * refreshRate):
        noResp.draw()
        win0.flip()
        if switch == True:
            trialDataDict['isCorrect'] = None
            trialDataDict['isForcedError'] = None
            trialDataDict['surpriseType'] = None
            trialDataDict['choice'] = None
            trialDataDict['confRating'] = None
            trialDataDict['fixStartTime'] = None
            trialDataDict['fixEndTime'] = None
            trialDataDict['feedbackStartTime'] = None
            trialDataDict['feedbackEndTime'] = None
            switch = False
    trialDataDict['noRespEndTime'] = lt.GetLastResult().Timestamp


def determineFeedback():
    global respSound

    # looks up the current contingent (color or shape)
    # if current contingent is color, set the correct answer to be based on color
    if trialDataDict['contingentCond'] == 0:  # 0 == color
        if stim == stim_BluSqr or stim == stim_BluCir:
            if dictInfo['version'] == 0:
                trialDataDict['correctAnswer'] = 0  # 0 == down
            elif dictInfo['version'] == 1:
                trialDataDict['correctAnswer'] = 1  # 1 == up
        elif stim == stim_GreSqr or stim == stim_GreCir:
            if dictInfo['version'] == 0:
                trialDataDict['correctAnswer'] = 1  # 1 == up
            elif dictInfo['version'] == 1:
                trialDataDict['correctAnswer'] = 0  # 0 == down

    # if current contingent is shape, set the correct answer to be based on shape
    elif trialDataDict['contingentCond'] == 1:  # 1 == shape
        if stim == stim_BluSqr or stim == stim_GreSqr:
            if dictInfo['version'] == 0:
                trialDataDict['correctAnswer'] = 1  # 1 == up
            elif dictInfo['version'] == 1:
                trialDataDict['correctAnswer'] = 0  # 0 == down
        elif stim == stim_BluCir or stim == stim_GreCir:
            if dictInfo['version'] == 0:
                trialDataDict['correctAnswer'] = 0  # 0 == down
            elif dictInfo['version'] == 1:
                trialDataDict['correctAnswer'] = 1  # 1 == up

    # determine outcome state considering probability condition
    # if participant made the correct choice
    if trialDataDict['correctAnswer'] == trialDataDict['choice']:
        # when probability condition is low (0)
        if trialDataDict['probCond'] == 0:
            # feedback is chosen with the low probability weighting
            trialDataDict['isCorrect'] = np.random.choice(
                2, p=(1 - probConds[0], probConds[0]))
            if trialDataDict['isCorrect'] == 0:
                trialDataDict['isForcedError'] = 1
            elif trialDataDict['isCorrect'] == 1:
                trialDataDict['isForcedError'] = 0
        # when probability condition is high (1)
        elif trialDataDict['probCond'] == 1:
            # feedback is chosen with the high probabiity weighting
            trialDataDict['isCorrect'] = np.random.choice(
                2, p=(1 - probConds[1], probConds[1]))
            if trialDataDict['isCorrect'] == 0:
                trialDataDict['isForcedError'] = 1
            elif trialDataDict['isCorrect'] == 1:
                trialDataDict['isForcedError'] = 0
        else:
            """this is only relevent for practice trials where there is no
            reliability manipulation"""
            trialDataDict['isCorrect'] = 1
            trialDataDict['isForcedError'] = 0
    elif trialDataDict['correctAnswer'] != trialDataDict['choice']:
        trialDataDict['isCorrect'] = 0  # 0 == incorrect
        trialDataDict['isForcedError'] = 0
    # when participant is not correct determine what type of surprise would be
    # experienced (Bayes or Information theoretic)
    if trialDataDict['isCorrect'] == 0:
        if stim == stim_BluCir or stim == stim_GreSqr:
            trialDataDict['surpriseType'] = 0   # InfoTheo Surpries
        else:
            trialDataDict['surpriseType'] = 1   # Bayes Surprise
        respSound = soundNotCorrect
    elif trialDataDict['isCorrect'] == 1:
        trialDataDict['points'] += 10
        trialDataDict['surpriseType'] = None
        respSound = soundCorrect


def fixationScreen(duration=1):
    """Show a fixation screen for a duration of time(s)
    and in the mean time, process what the feedback should be
    """
    feedbackProcessCheck = False
    trialDataDict['fixStartTime'] = lt.GetLastResult().Timestamp
    fixStim.draw()
    win0.flip()
    fixationTimer = core.Clock()
    while fixationTimer.getTime() < duration:
        if event.getKeys(keyList=['escape']):
            break
        if feedbackProcessCheck == False:
            determineFeedback()
            feedbackProcessCheck = True
        sleep(0.0000001)   # this sleep command prevents 'busy wait',
        # consuming less cpu
    trialDataDict['fixEndTime'] = lt.GetLastResult().Timestamp


def feedbackScreen(duration=4):
    trialDataDict['feedbackStartTime'] = lt.GetLastResult().Timestamp
    nextFlip = win0.getFutureFlipTime(clock='ptb')
    respSound.play(when=nextFlip)
    for frameN in range(duration * refreshRate):
        if event.getKeys(keyList=['escape']):
            break
        fixStim.draw()
        win0.flip()
    respSound.stop()
    trialDataDict['feedbackEndTime'] = lt.GetLastResult().Timestamp


def practiceSection():
    # function to organize practice section
    global trialNumbTotal
    global contingentBlockList
    global probabilityConditionList
    visual.TextStim(win=win0, text=f"{practiceText1}", height=0.9).draw()
    win0.flip()
    keys = event.waitKeys(keyList=['c', 'escape'])
    if keys[-1] == 'c':
        doCalibrate()
    while True:
        if dictInfo['version'] == 0:
            visual.TextStim(
                win=win0, text=f"{practiceText2}", height=0.9).draw()
        elif dictInfo['version'] == 1:
            visual.TextStim(
                win=win0, text=f"{practiceText2v2}", height=0.9).draw()
        win0.flip()
        keys = event.waitKeys(keyList=['escape', 'space'])
        if keys[-1] == 'escape':
            break
        blockTrialList = [4, 4]
        contingentBlockList = [0, 1]
        probabilityConditionList = [3, 3]
        for blockNumb in range(len(blockTrialList)):
            for trialNumb in range(blockTrialList[blockNumb]):
                trialDataDict['blockTrial'] = trialNumb
                trialNumbTotal += 1
                trialDataDict['trialTotal'] += 1
                trialDataDict['block'] = blockNumb
                trialDataDict['contingentCond'] = contingentBlockList[blockNumb]
                trialDataDict['probCond'] = probabilityConditionList[blockNumb]
                percentFixationScreen(duration=500)
                stimulusScreen(duration=500)
                responseScreen(duration=500)
                fixationScreen(duration=500)
                feedbackScreen(duration=500)
        visual.TextStim(win=win0, text=f"{practiceText3}", height=0.9).draw()
        win0.flip()
        keys = event.waitKeys(keyList=['space', 'r'])
        if keys[-1] == 'space':
            break
        elif keys[-1] == 'r':
            trialDataDict['points'] = 0
    while True:
        blockTrialList = [4, 4]
        contingentBlockList = [0, 1]
        probabilityConditionList = [3, 3]
        for blockNumb in range(len(blockTrialList)):
            for trialNumb in range(blockTrialList[blockNumb]):
                trialDataDict['blockTrial'] = trialNumb
                trialDataDict['trialTotal'] += 1
                trialDataDict['block'] = blockNumb
                trialDataDict['contingentCond'] = contingentBlockList[blockNumb]
                trialDataDict['probCond'] = probabilityConditionList[blockNumb]
                percentFixationScreen()
                stimulusScreen()
                responseScreen()
                fixationScreen()
                feedbackScreen()
        visual.TextStim(win=win0, text=f"{practiceText4}", height=0.9).draw()
        win0.flip()
        keys = event.waitKeys(keyList=['space', 'r'])
        if keys[-1] == 'space':
            break


def saveTrialData():
    '''This is a funciton that saves/backs up the trial data.
    This function is called on a seperate thread and is activated after the
    feedback screen.
    It takes the eye tracker data from the feedback period and translates it
    to a dataframe and adds additional information about the trial then exports
    it to a CSV file.'''
    global trialCheck

    dataDir = f"data/{dictInfo['partID']}/pickle/{dictInfo['session#']}"
    try:
        original_umask = os.umask(0)
        os.makedirs(dataDir, 0o777)
    except OSError:
        print("Creation of the directory %s failed" % dataDir)
    else:
        print("Successfully created the directory %s" % dataDir)
    finally:
        os.umask(original_umask)

    while backupCheck == True:  # this loop stays on throughout the experiment
        if trialCheck == True:  # this switch is turned on at the end of a trial
            timer = core.Clock()
            outDF = pd.DataFrame.from_dict(trialDataDictCopy, orient='index').T
            outDF.insert(0, 'partID', dictInfo['partID'])
            outDF.insert(1, 'session', dictInfo['session#'])
            outDF.insert(2, 'version', dictInfo['version'])
            outDF['gender'] = dictInfo['gender']
            outDF['age'] = dictInfo['age']
            outDF['mascara'] = dictInfo['mascara']
            outDF['glasses'] = dictInfo['glasses']
            outDF['contactLens'] = dictInfo['contactLens']

            # saving the dataframe as a CSV
            if trialDataDictCopy['trialTotal'] == 0:
                outDF.to_csv(f"data/{dictInfo['partID']}/{dictInfo['partID']}_{dictInfo['session#']}data.csv",
                             index=False, header=True)
            else:
                outDF.to_csv(f"data/{dictInfo['partID']}/{dictInfo['partID']}_{dictInfo['session#']}data.csv",
                             mode='a', index=False, header=False)

            # pickleing eye tracker data for backup
            eyeData = lt.GetBufferedEyePositions(fromBeginning=0,
                                                 removeFromBuffer=1)
            pickleName = f"{dataDir}/{trialDataDictCopy['trialTotal']}"
            pickleObject = open(pickleName, 'wb')
            pickle.dump(eyeData, pickleObject)
            print(f"{timer.getTime()}\tUPDATED!!")
            trialCheck = False
        sleep(0.001)


# Global Commands
event.globalKeys.add(key='s', modifiers=('ctrl', 'alt'), func=shutDown)
event.globalKeys.add(key='b', modifiers=('ctrl', 'alt'), func=breakSection)


def versionChange():
    global soundCorrect
    global soundNotCorrect
    global refStimUp
    global refStimDown
    refSize = 2
    refPos = 5
    if dictInfo['version'] == 1:
        scaleLabelList.reverse()
        soundList.reverse()
        refStimUp = visual.Circle(win=win0,
                                  size=refSize,
                                  fillColor=blueVal,
                                  lineColor=(-1, -1, -1),
                                  edges=99,
                                  lineWidth=stimLineW,
                                  pos=(0, refPos)
                                  )
        refStimDown = visual.Rect(win=win0,
                                  size=refSize * 2,
                                  fillColor=greenVal,
                                  lineColor=(-1, -1, -1),
                                  lineWidth=stimLineW,
                                  pos=(0, -refPos)
                                  )
    else:
        refStimUp = visual.Rect(win=win0,
                                size=refSize * 2,
                                fillColor=greenVal,
                                lineColor=(-1, -1, -1),
                                lineWidth=stimLineW,
                                pos=(0, refPos)
                                )
        refStimDown = visual.Circle(win=win0,
                                    size=refSize,
                                    fillColor=blueVal,
                                    lineColor=(-1, -1, -1),
                                    edges=99,
                                    lineWidth=stimLineW,
                                    pos=(0, -refPos)
                                    )
    soundCorrect = sound.Sound(value=soundList[0], stereo=-1,
                               hamming=True, preBuffer=-1)
    soundNotCorrect = sound.Sound(value=soundList[-1], stereo=-1,
                                  hamming=True, preBuffer=-1)

    scaleLabelLeft.text = scaleLabelList[0]
    scaleLabelRight.text = scaleLabelList[-1]


if __name__ == '__main__':
    # win0.fullscr = False
    # win0.winHandle.minimize()
    expName = 'mentalModelPupil'
    dlg = gui.DlgFromDict(dictionary=dictInfo,
                          title=expName,
                          screen=1,
                          order=['partID', 'version', 'session#', 'gender',
                                 'age', 'mascara', 'glasses', 'contactLens',
                                 'blueEyes', 'debug'])
    if dlg.OK == False:
        win0.close(), core.quit()    # user pressed cancel
    debugging()
    versionChange()
    lt.Init()   # initialize LiveTrack (Eye tracker)
    lt.StartTracking()  # LiveTrack start tracking
    # win0.winHandle.maximize()
    # win0.fullscr = True
    win0.flip()
    # Start of experiment body
    # Introduction Section
    if doIntro == True:
        introduction()
    # Practice Trials Section
    if doPractice == True:
        practiceSection()
    # Experimental Trials Section Start
    if doExp == True:
        visual.TextStim(win0, text=f"{expText1}").draw()
        win0.flip()
        keys = event.waitKeys(keyList=['c', 'escape'])
        if keys[-1] == 'c':
            doCalibrate()
        visual.TextStim(win0, text=f"{expText2}").draw()
        win0.flip()
        keys = event.waitKeys(keyList=['space'])
        win0.flip()
        # reset eye tracker buffer and dictionaries before exp trials
        trialDataDict = dict.fromkeys(trialDataKeys)
        trialDataDict['points'] = 0
        trialDataDict['trialTotal'] = -1
        lt.StopTracking()
        lt.ClearDataBuffer()
        lt.SetResultsTypeCalibrated()
        lt.StartTracking()
        blockTrialNumbs = randIntListSetTotal(12, 16, 10, 22, 3)
        contingentBlockList = makeContingentBlockList(blockTrialNumbs)
        probabilityConditionList = makeProbabilityConditionList(
            blockTrialNumbs)
        stimSequence = randIntNoRepeat(sum(blockTrialNumbs), 0, 3)
        if doSave == True:
            saveTrialThread = Thread(target=saveTrialData)
            saveTrialThread.start()
        totalTimer = core.Clock()
        timer = core.Clock()
        for blockNumb in range(len(blockTrialNumbs)):
            if blockNumb == len(blockTrialNumbs) / 2:
                breakSection()
            for trialNumb in range(blockTrialNumbs[blockNumb]):
                while True:
                    trialDataDict['blockTrial'] = trialNumb
                    trialDataDict['trialTotal'] += 1
                    trialDataDict['block'] = blockNumb
                    trialDataDict['contingentCond'] = contingentBlockList[blockNumb]
                    trialDataDict['probCond'] = probabilityConditionList[blockNumb]
                    timer.reset()
                    win0.mouseVisible = False
                    print(
                        f"trial#: {trialDataDict['trialTotal']}\tprob: {trialDataDict['probCond']}\tcont: {trialDataDict['contingentCond']}")
                    percentFixationScreen()
                    print(f"{timer.getTime()}\tpoints")
                    timer.reset()
                    stimulusScreen()
                    print(f"{timer.getTime()}\tstim")
                    timer.reset()
                    win0.mouseVisible = True
                    responseScreen()
                    win0.mouseVisible = False
                    if trialDataDict['respSuccess'] == 0:
                        noRespScreen()
                        trialDataDictCopy = deepcopy(trialDataDict)
                        trialCheck = True
                        break
                    print(f"{timer.getTime()}\tresp")
                    timer.reset()
                    fixationScreen(duration=0.985)
                    print(f"{timer.getTime()}\tfix")
                    timer.reset()
                    feedbackScreen()
                    trialDataDictCopy = deepcopy(trialDataDict)
                    trialCheck = True
                    print(f"{timer.getTime()}\tfeed")
                    break

        totalTime = totalTimer.getTime()
        print(f"total time elapsed:\t{totalTime}")
        if trialDataDict['points'] != 0:
            pointsPercent = round(
                ((trialDataDict['points'] / ((trialDataDict['trialTotal'] + 1) * 10)) * 100) + 0.5)
            visual.TextStim(win=win0, text=f"""You have finished the session!\n
                        You have earned {trialDataDict['points']} gold out of {(trialDataDict['trialTotal'] + 1)*10}!\n
                        That is {pointsPercent}%!\n
                        Thank you for your participation.\n\nSaving...""", height=0.9).draw()
            win0.flip()
            sleep(3)
            backupCheck = False
            if doSave == True:
                saveTrialThread.join()

            visual.TextStim(win=win0, text=f""""You have finished the session!\n
                        You have earned {trialDataDict['points']} gold out of {(trialDataDict['trialTotal'] + 1)*10}!\n
                        That is {pointsPercent}%!\n
                        Thank you for your participation.\n\nSaving done!\n
                        Press [Space] to end.""", height=0.9).draw()
            win0.flip()
    event.waitKeys(keyList=('space'))
    lt.StopTracking()
    lt.Close()
    win0.close()

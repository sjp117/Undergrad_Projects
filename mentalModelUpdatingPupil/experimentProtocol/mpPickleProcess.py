import pandas as pd
import  pickle
import os
import timeit
from multiprocessing import Pool, cpu_count
from psychopy import core
from tqdm import tqdm

def getdict(struct):
    # this function returns a dictionary of the cython data structure (eye data)
    return dict((field, getattr(struct, field)) for field, _ in struct._fields_)

def eyeData2DF(numb):
    global data
    dict1 = getdict(data[numb])
    outDF = pd.DataFrame.from_dict(dict1, orient='index').T
    return outDF

def mpFunc(numb):
    global outDF
    p = Pool(cpu_count()-1)
    results = p.map(eyeData2DF, numb)

    p.close()
    p.join()

    outDF = outDF.append(results)

if __name__=='__main__':
    dirPath = 'data/eyeData'
    fileList=os.listdir(dirPath)
    fileList.sort(key=int)
    timer = core.Clock()
    outDF = pd.DataFrame()
    csvName = 'test114.csv'
    for fileName in tqdm(['0','1','2','3','4','5','6','7']):
        data = pickle.load(open(f"pickles/{fileName}",'rb'))
        numb = range(len(data))
        mpFunc(numb)
        if fileName == '0':
            outDF.to_csv(csvName, index=False, header=True)
        else:
            outDF.to_csv(csvName, index=False, header=False, mode='a')
        outDF = pd.DataFrame()
#!/usr/bin/python

# ocrdv - reads frames from a .dv untill it finds a bunch of words

import subprocess
import pyffmpeg
from cStringIO import StringIO
from csv import DictReader
from collections import defaultdict

def Titwords():
    reader = DictReader(open("sched.csv", "rb"))
    titwords=defaultdict(list)
    for row in reader:
        title=row['title']
        for w in title.split():
            w = ''.join([c for c in w if c.isalpha()])
            if len(w)>3: 
                titwords[w.lower()].append(title)
#  re.compile('[^a-z]').sub('', 'foo:')
    return titwords

def Dictionary():
    dictionary = [w for w in open('dictionary.txt').read().split() if len(w)>3]
    return dictionary

def Score(ocrtext):
    score = 0
    words = ocrtext.split()
    titl=[]
    for w in words:
        # strip all non chars
        w = ''.join([c for c in w if c.isalpha()]).lower()
        if len(w)>3 and titwords.get(w):
            tits = titwords[w]
            titl.append(tits)
            score+=len(tits)

    dictwords = [w for w in words if len(w)>3 and w.upper() in dictionary]
    if dictwords:
        titl.append(dictwords)
        score+=len(dictwords)

    return score, titl

titwords = Titwords()
dictionary = Dictionary()

dvfn = '/home/carl/Videos/pyohio/2009-07-25/auditorium/pyohio-4.dv'

def ocrdv(dvfn,maxframes):
    
    stream = pyffmpeg.VideoStream()
    stream.open(dvfn)
    frameno=0
    lastocr = ''
    while frameno < maxframes:

        image = stream.GetFrameNo(frameno)

        # get PPM image from PIL image 
        buffer = StringIO()
        image.save(buffer,'PPM')
        img = buffer.getvalue()
        buffer.close()

        # ocr the image
        p = subprocess.Popen(['gocr', '-'],
          stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        ocrtext, stderrdata = p.communicate(img)
        if stderrdata: print "ERR:", stderrdata

        if ocrtext != lastocr:
            lastocr = ocrtext ## saves scoring the same wad of text

            # score the text
            print "GOCR found:\n", ocrtext
            score,titls = Score(ocrtext)
            if score>2:
                print "score", score
                print titls
                return ocrtext,image

        frameno+=30*60  # bump on min

    image = stream.GetFrameNo(0)
    return '',image
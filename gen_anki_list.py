#coding: utf-8
import codecs, sys

#Usage gen_anki_list kindlenote.html output.txt eiijorfilename.txt

# Constants
removelist = [u'◆', u'\ ・', u'【変化】', u'【分節】', u'【＠】']

def FindDefinitions(word, dic, startpoint=0):
    deflist = []
    found = False

    # find the first element that meets the condition
    # Don't want to evaluate all elements, so starting from 'startpoint'
    i = startpoint
    j = (i-1+len(dic)) % len(dic)
    while(i!=j and (not dic[i].startswith(word+' ///'))):
        i = (i+1) % len(dic)
    if i!=j: # found
        l = dic[i][len(word)+4:]
        for r in removelist:
            ii = l.find(r)
            l = l[:ii] if (ii >= 0) else l
        for d in l.split('\\'):
            if 0 <= d.find(u'＝<→') < d.find(u'>'):
                dl, w, k = FindDefinitions(d[d.find(u'＝<→') + 3:d.find(u'>')], dic) # w and k are not used
                deflist.extend(dl)
            elif (len(d.strip())>0):
                deflist.append(d.strip())
    else: # word not found
        if (word[-1]=='s'):
            deflist, w, k = FindDefinitions(word[:-1], dic)
            if (len(deflist)>0):
                print(word+' not found. '+w+' is used instead.')
                word = w
    j = (i+1) % len(dic) # next starting point
    return deflist, word, j

args = sys.argv
inputfilename = "wordlist.html" if len(args)<2 else args[1]
try:
    f = codecs.open(inputfilename, "r", 'utf-8')
    txt = f.readlines()
except:
    print("Error opening "+inputfilename)
    raise

dicfilename = "eijiro.txt" if len(args)<4 else args[3]
try:
    ef = codecs.open(dicfilename, 'r', 'utf-16')
    dic = ef.readlines()
except:
    print("Error opening "+dicfilename)
    raise

title = "quiz.txt" if len(args)<3 else args[2]

with codecs.open(title, 'w', 'utf-8') as fout:

    j = 0
    for word in txt:
        ii = word.find(u'<div class=\'noteText\'>')
        if ii < 0:
            continue
        word = word[ii + 22:]
        ii = word.find(u'</div>')
        if ii < 0:
            continue
        word = word[:ii].rstrip(',').rstrip('.').rstrip()
        defs, word, j = FindDefinitions(word, dic, j)
        if len(defs)==0:
            print(word+' not found')
            continue
        outtxt = word.strip() + "\t" + ('<br>'.join(defs)) + "\n"
        fout.write(outtxt)

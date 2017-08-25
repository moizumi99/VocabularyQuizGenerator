#coding: utf-8
import codecs, sys

args = sys.argv

txt = []
inputfilename = "wordlist.html" if len(args)<2 else args[1]
with codecs.open(inputfilename, "r", 'utf-8') as f:
    txt = f.readlines()

dic = []
dicfilename = "eijiro.txt" if len(args)<4 else args[3]
with codecs.open(dicfilename, 'r', 'utf-16') as ef:
    dic = ef.readlines()

removelist = [u'◆', u'\ ・', u'【変化】', u'【分節】', u'【＠】']

j = len(dic)-1
i = 0
title = "quiz" if len(args)<3 else args[2]
with codecs.open(title+'.csv', 'w', 'sjis') as fout:
    fout.write("psscsvfile,100,,,\n")
    fout.write(title+",,,,\n")
    fout.write(",,,,\n")
    fout.write("a1,q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,\n")

    for word in txt:
        ii = word.find(u'<div class=\'noteText\'>')
        if ii<0:
            continue
        word = word[ii+22:]
        ii = word.find(u'</div>')
        if ii<0:
            continue
        word = word[:ii].rstrip(',').rstrip('.').rstrip()
        found = False
        while(i!=j):
            if dic[i].startswith(word) and dic[i][len(word)]==' ':
                found = True
                break
            i = i+1 if (i<len(dic)-1) else 0
        if (not found):
            print(word, "Not found")
        else:
            # fout.write(dic[i])
            outtxt = "\""+word.strip()+"\""
            l = dic[i].rstrip()
            for r in removelist:
                ii = l.find(r)
                l = l[:ii] if (ii>=0) else l
                # fout.write(l+"\n")
            l = l[l.find(u"///")+3:]
            ii = 0
            while (ii>=0):
                ii = l.find(u"\\")
                d = l[:ii].strip() if (ii>=0) else l.strip()
                l = l[ii+1:]
                if 0<=d.find(u'＝<→')<d.find(u'>'):
                    d = d[0:d.find(u'＝<→')]+d[d.find(u'＝<→')+3:d.find(u'>')]+d[d.find(u'>')+1:]
                outtxt = outtxt + ", \"" + d + "\"" if len(d)>0 else outtxt
            try:
                fout.write(outtxt.encode('CP932').decode('SJIS') + "\n")
            except:
                print(outtxt)
                raise
        j = len(dic)-1 if (i==0) else i-1
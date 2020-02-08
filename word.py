#Requirements
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from tika import parser #requirement : JDK
import requests as req
from fake_headers import Headers
import json
import sys
#------------




class wordbook:
    r = req.Session()
    r.headers = Headers().generate()
    r.get("https://dic.daum.net/index.do?dic=eng&q=")   #init

    def __init__(self,import_file,export_file="wordbook.csv"):
        super().__init__()
        self.filters = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'LS', 'MD', 'PDT', 'POS', 'PRP', 'PRP$', 'TO', 'UH', 'WDT', 'WP', 'WP$', 'WRB', '.', ':', '(', ')', '!', '?', '{}', '&', '%', '$', '#', '``', "'", "''", 'VBZ', 'VBP', 'NNP', ',', '|', '“']    #nltk filters
        self.wfilters = "/\.<>{}[]%*·\"“”-~=•_0123456789"
        #NLTK
        self.lm = WordNetLemmatizer()
        #-------------
        self.outfile = export_file
        print("-----추출시작 : {imp}-----".format(imp=import_file))
        self.parsed = self.parse(self.extract(import_file))
        print("추출완료. : {imp}".format(imp=import_file))
        self.createw(self.parsed)
        self.out(self.wlist)

        #text->parse->createw

    
    
    def parse(self,txt):    #pos_tag
        tmp_list = []
        tks = word_tokenize(txt)
        for tk in pos_tag(tks):
            w,t = tk
            if t not in self.filters:
                tmp_list.append((w.lower(),t))
        return tmp_list
    
    def isvalid(self,word):
        for x in self.wfilters:
            if x in word:
                return False
        return True
    
    
    def createw(self,parsed_list):
        self.wlist = {}
        max = len(parsed_list)
        loading_bar = [" " for x in range(101)]
        for i,w in enumerate(parsed_list):
            a,b = w
            if not self.isvalid(a): continue
            if b[0] == "J":
                b = "a"
            org = self.origin(a,b[0].lower())
            if org in self.wlist.keys():
                self.wlist[org]+=1
            else:
                self.wlist[org]=1
            
            loading_bar[int((i/max)*100)] = "#"
            sys.stdout.write("\r단어추출시작 .... {lb} [{pt}%]".format(lb="".join(loading_bar),pt=int((i/max)*100)))
        print("\n단어추출완료!")
        self.wlist = {k: v for k, v in sorted(self.wlist.items(), key=lambda item: item[1],reverse=True)}
        max = len(self.wlist)
        print("추출된 단어수 : "+str(max))
        print("번역작업 시작...")
        loading_bar = [" " for x in range(101)]
        for i,w in enumerate(self.wlist.keys()):
            self.wlist[w] = self.search(w)
            loading_bar[int((i/max)*100)] = "#"
            sys.stdout.write("\r번역중 .... {lb} [{pt}%]".format(lb="".join(loading_bar),pt=int((i/max)*100)))
        print("번역완료!")
        return self.wlist
    
    def out(self,wlist):
        f = open(self.outfile,"w")
        print("단어를 파일로 저장중... "+self.outfile)
        for w in wlist:
            if wlist[w]:
                f.write(w+","+wlist[w]+"\n")
            else:
                f.write(w+",-no data\n")
        print("저장완료!")
        return



    
    def origin(self,w,pos):
        return self.lm.lemmatize(w,pos)


    def search(self,q):
        dq = "https://suggest-bar.daum.net/suggest?mod=json&code=utf_in_out&enc=utf&id=language&cate=eng&q={q}"
        #print(self.r.cookies)
        res = json.loads(self.r.get(dq.format(q=q)).text)
        return len(res["items"])>0 and "".join(res["items"][0].split("|")[1:]) or False

    

    #---------extract from file------
    def extract(self,file):
        raw = parser.from_file(file)
        return raw['content']



wordbook("tw.pdf","tangled.csv")
#filter : CC,CD,DT,EX,FW,IN,LS,MD,PDT,POS,PRP,PRP$,TO,UH,WDT,WP,WP$,WRB
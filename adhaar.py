import nltk,subprocess,glob,sys,traceback,code,os,json
import re
from convertPDFToText import convertPDFToText
from imageToText import convertImageToText

class Parse :
    inputString=''
    tokens = []
    lines = []
    sentences = []
    dirpath='D:/Parser/'
    
    def __init__(self, verbose=False):
        if len(sys.argv)>1:
            # print(self.dirpath+sys.argv[1])
            files = glob.glob(self.dirpath+sys.argv[1])        
        else:
            files = glob.glob(self.dirpath+"Files/adhar.jpg")  
        for f in files:
            info = {}
            if(os.path.splitext(f)[1]=='.pdf'):
                self.inputString = self.readFile(f,'pdf') 
            else:
                self.inputString = self.readFile(f,'image')              
            info['fileName'] = f
            if len(sys.argv)>2:
                info['file_type'] = sys.argv[2]      
            else:
                info['file_type'] = 'aadhaar'
            # print('Tokenizing file')
            self.tokenize(self.inputString)
            # print('Getting name from file')
            self.getName(info)
            # print('Getting date of birth from file')
            self.getDOB(info)
            # print('Getting gender from file')
            self.getGender(info)
            # print('Getting father\'s name from file')
            self.getFatherName(info)
            # print('Getting aadhar number from file')
            self.getAdhaarNo(info)
            # print('Getting state from file')
            self.getStateName(info)
            # print('Getting pincode from file')
            self.getPincode(self.inputString,info)
            # print('Getting address from file')
            self.getAddress(info)
            # print(info)
            print(json.dumps(info))

    def readFile(self, fileName,fileType):
        if fileType=='pdf':
            try:
                return convertPDFToText(fileName)
            except:
                return ''
        else:
            try:
                tempstr = convertImageToText(fileName)
                return tempstr.decode('utf-8')
            except:
                return ''

    def tokenize(self, inputString):
        try:
            self.tokens, self.lines, self.sentences = self.preprocess(inputString)
            return self.tokens, self.lines, self.sentences
        except Exception as e:
            print(e)

    def preprocess(self, document):
        try:
            try:
                document = document.decode('ascii', 'ignore')
            except:
                document = document.encode('ascii', 'ignore')
            lines = [el.strip() for el in document.splitlines() if len(el) > 0]  # Splitting on the basis of newlines 
            lines = [nltk.word_tokenize(el.decode('utf-8')) for el in lines]    # Tokenize the individual lines
            lines = [nltk.pos_tag(el) for el in lines]
            sentences = nltk.sent_tokenize(document.decode('utf-8'))    # Split/Tokenize into sentences (List of strings)
            sentences = [nltk.word_tokenize(sent) for sent in sentences]    # Split/Tokenize sentences into words (List of lists of strings)
            tokens = sentences
            sentences = [nltk.pos_tag(sent) for sent in sentences]
            dummy = []
            for el in tokens:
                dummy += el
            tokens = dummy

            return tokens, lines, sentences

        except Exception as e:
            print(e) 

    def getName(self,infoDict):
        indianNames = open(self.dirpath+"allNames.txt", "r").read().lower()
        # Lookup in a set is much faster
        indianNames = set(indianNames.split())

        nameHits = []
        name = None

        grammar = r'NAME: {<JJ><NN.*>*|<NN.*><NN.*>*}'

        chunkParser = nltk.RegexpParser(grammar)
        all_chunked_tokens = []
        for tagged_tokens in self.lines:
            if len(tagged_tokens)==0:continue
            chunked_tokens = chunkParser.parse(tagged_tokens)
            all_chunked_tokens.append(chunked_tokens)
            for subtree in chunked_tokens.subtrees():
                # print(subtree)
                if subtree.label() == 'NAME':
                    for ind, leaf in enumerate(subtree.leaves()):
                        if leaf[0].lower() in indianNames and leaf[1] in ['NN','JJ','NNP']:
                            hit = " ".join([el[0] for el in subtree.leaves()[ind:ind+3]])
                            if re.compile(r'[\d,:]').search(hit): continue
                            nameHits.append(hit)

        if len(nameHits) > 0:
            nameHits = [re.sub(r'[^a-zA-Z \-]', '', el).strip() for el in nameHits] 
            name = " ".join([el[0].upper()+el[1:].lower() for el in nameHits[0].split() if len(el)>0])
            # otherNameHits = nameHits[1:]
            infoDict['name']=name
            # infoDict['otherName']=otherNameHits



    def getDOB(self,infoDict):
        # print(self.inputString)
        yearline=''
        for wordlist in self.inputString.split('\n'):
            xx = wordlist.split( )
            if ([w for w in xx if re.search('(Year|Birth|irth|YoB|YOB:|DOB:|DOB)$', w)]):
                yearline = wordlist
                break
        if(yearline):
            yearline = re.split('Year|Birth|Birth |Birth :|Birth:|irth|YoB|YOB:|DOB:|DOB', yearline)[1:]
            infoDict['DOB']=yearline[0].strip()
        else:
            infoDict['DOB']='NA'

    def getFatherName(self,infoDict):
        nameline=''
        for wordlist in self.inputString.split('\n'):
            xx = re.split(r'[\s,]',wordlist)
            if ([w for w in xx if re.search('(S/O|SO|s/o|S/O:|SO:|so|so:|s/o:|S/O,|SO,)$', w)]):
                nameline = wordlist
                break
        if(nameline):
            nameline = re.split('S/O:|S/O,|S/O|s/o:|s/o|so|SO,|SO', nameline)[1:]
            infoDict['Father']=nameline[0].strip()
        else:
            infoDict['Father']='NA'

    def getGender(self,infoDict):
        infoDict['gender'] = "NA"
        for wordlist in self.inputString.split('\n'):
            xx = re.split(r'[\s]',wordlist)
            # print(xx)

            # print(re.search('(Female|Male|emale|male|ale|FEMALE|MALE|EMALE)$'))
            if ([w for w in xx if re.search('(Female|Male|emale|male|ale|FEMALE|MALE|EMALE)$', w)]):
                nameline = xx
                break
        if(nameline):
            infoDict['gender']=nameline[1:][0].strip()
        else:
            infoDict['gender']='NA'
    
    def getAdhaarNo(self,infoDict,debug=False):
        number = None
        try:
            # pattern = re.compile(r'(?<=[-, ]|^)\d{6}(?=[-, ]|$)')
            pattern = re.compile(r'[0-9]{4}[\s][0-9]{4}[\s][0-9]{4}')
            # print(pattern)
            match = pattern.findall(self.inputString)
            if len(match)>0:
                number=match[0]
            else:
                number="NA"
        except:
            pass

        infoDict['adhar_no'] = number.replace(" ", "")

        if debug:
            code.interact(local=locals())
            

    def getAddress(self,infoDict):
        address=''
        sen=''
        for ind, sentence in enumerate(self.lines):
            if len(sentence)==0:continue
            sen=" ".join([words[0].lower() for words in sentence])
            # print(sen)
            if sen=='address :' :
                index=ind
                break
        notCompleted=True
        try:
            i=index
            while notCompleted:
                i+=1
                if len(self.lines[i])==0:continue
                elif i==index:continue
                else:
                    address+=" ".join(words[0] for words in self.lines[i])
                    # pattern = re.compile(r'(?<=[-, ]|^)\d{6}(?=[-, ]|$)')
                    pattern = re.compile(r'[0-9][0-9]{5}')
                    # print(pattern)
                    match = pattern.findall(address)
                    if len(match)>0:
                        notCompleted=False
                    else:continue
            infoDict['address']=address            
        except:
            infoDict['address']="NA"

    def getStateName(self,infoDict):
        stateNames = open(self.dirpath+"stateslist.txt", "r").read().lower()
        # Lookup in a set is much faster
        indianStates = set(stateNames.split())
        stateHits=[]
        state='NA'

        grammar = r'STATE: {<NN.*><NN.*>*}'

        chunkParser = nltk.RegexpParser(grammar)
        all_chunked_tokens = []

        for tagged_tokens in self.lines:
            # print(tagged_tokens)
            if len(tagged_tokens)==0:continue
            chunked_tokens = chunkParser.parse(tagged_tokens)
            all_chunked_tokens.append(chunked_tokens)
            for subtree in chunked_tokens.subtrees():
                # print(subtree)
                if subtree.label() == 'STATE':
                    for ind, leaf in enumerate(subtree.leaves()):
                        if leaf[0].lower() in indianStates and 'NN' in leaf[1]:
                            hit = " ".join([el[0] for el in subtree.leaves()[ind:ind+3]])
                            if re.compile(r'[\d,:]').search(hit): continue
                            stateHits.append(hit)

        if len(stateHits) > 0:
            stateHits = [re.sub(r'[^a-zA-Z \-]', '', el).strip() for el in stateHits] 
            state = " ".join([el[0].upper()+el[1:].lower() for el in stateHits[0].split() if len(el)>0])
            # otherNameHits = stateHits[1:]
            infoDict['state']=state
            # infoDict['otherName']=otherNameHits
    
    def getPincode(self, inputString, infoDict, debug=False):
        number = None
        try:
            # pattern = re.compile(r'(?<=[-, ]|^)\d{6}(?=[-, ]|$)')
            pattern = re.compile(r'[0-9][0-9]{5}')
            # print(pattern)
            match = pattern.findall(inputString)
            if len(match)>0:
                number=match[0]
            else:
                number="NA"
        except:
            pass

        infoDict['pincode'] = number

        if debug:
            code.interact(local=locals())
    
    def adhaar(self,infoDict):
        return infoDict

if __name__ == "__main__":
    verbose = False
    if "-v" in str(sys.argv):
        verbose = True
    p = Parse(verbose)
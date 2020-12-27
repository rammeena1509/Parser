# import the following libraries 
# will convert the image to text string 
import pytesseract	 

# adds image processing capabilities 
from PIL import Image	 

# converts the text to speech 
import pyttsx3		 
						 
# path where the tesseract module is installed 
pytesseract.pytesseract.tesseract_cmd ='C:/Program Files/Tesseract-OCR/tesseract.exe'
# converts the image to result and saves it into result variable 

def convertImageToText(path):
    # opening an image from the source path 
    img = Image.open(path)
    result = pytesseract.image_to_string(img) 
    # print(result.encode('utf-8').strip())
    result=result.encode('utf-8').strip()
    # result=result.encode('ascii', 'ignore').decode('ascii')
    # result = filter(lambda x: ord(x)<128,result)
    return result

def readDataFromImage(img):
    result = pytesseract.image_to_string(img)
    return result

# write text in a text file and save it to source path 
# with open('abc.txt',mode ='w') as file:	 
	
# 				file.write(result) 
# 				print(result) 
				
# p = Translator()					 
# translates the text into german language 
# k = p.translate(result,dest='german')	 
# print(k) 
# engine = pyttsx3.init() 

# an audio will be played which speaks the test if pyttsx3 recognizes it 
# engine.say(k)							 
# engine.runAndWait() 

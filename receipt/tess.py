import io
import os
import sys
from PIL import Image
import pytesseract
from wand.image import Image as wi

def ocr(f_path):

#   img = input()

	new_path = os.path.join(os.getcwd(), f_path[1:])
	pdf = wi(filename = os.path.join(os.getcwd(), new_path), resolution = 300)
	pdfImage = pdf.convert('jpg')

	orig_stdout = sys.stdout
	# print(os.getcwd())
	f = open('receipt/media/txt/output1.txt', 'w+')
	sys.stdout = f

	imageBlob = []

	for img in pdfImage.sequence:
		imgPage = wi(image = img)
		imageBlob.append(imgPage.make_blob('jpeg'))

	recognized_text = []

	for blob in imageBlob:
		im = Image.open(io.BytesIO(blob))
		text = pytesseract.image_to_string(im, lang = 'eng')
		recognized_text.append(text)

	print(recognized_text[0])

	sys.stdout = orig_stdout
	f.close()
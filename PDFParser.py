import PyPDF2
import pytesseract
import os
import sys
from pdf2image import convert_from_path
from PIL import Image
from datetime import datetime
from configparser import ConfigParser
import shutil

settings_file = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\settings.ini"

def check_create_dir(order_number):

	# Read setting.ini file
	Config = ConfigParser()
	Config.read(settings_file)
	order_path = os.path.join(Config.get("PATH SETTINGS", "order_data"),order_number)
	temp_draft = Config.get("PATH SETTINGS", "draft_temp")
	draft_path = os.path.join(order_path, "DFT")

	# Check if foler exist, if not create folder
	if not os.path.exists(order_path):
		os.makedirs(order_path)
		os.makedirs(draft_path)

	# Move draft files to new folder
	for drawing in os.listdir(temp_draft):
		old_path = os.path.join(temp_draft,drawing)
		new_path = os.path.join(draft_path, drawing)
		shutil.move(old_path, new_path)


def split_to_sam(order_number):

	# Define file
	file = order_number + ".pdf"

	# Open combined WO pdf
	pdfFile = open(file, 'rb')
	pdfReader = PyPDF2.PdfFileReader(pdfFile)

	# remove .pdf from filename
	jobID = file.strip('.pdf')

	# initialize sam counter
	samID = 0

	# Total number of pages
	n_pages = pdfReader.numPages

	# create list for order data and samPages
	orderData = []
	samPages = []

	# Loop through document to find samPages
	for i in range(n_pages):
		
		# Create page obj
		page = pdfReader.getPage(i)
		
		# Extract text
		pageText = page.extractText()

		# Search JobID in text
		if jobID in pageText:
			samPages.append(i)
	
	# loop trough file and save sam
	for i in range(n_pages):

		# Create writer and get page
		pdfWriter = PyPDF2.PdfFileWriter() 
		
		# iterate trough document
		if i in samPages:
			
			# write PDF is sam in samPages
			pdfWriter.addPage(pdfReader.getPage(i))

			# Get part name 
			pageText = pdfReader.getPage(i).extractText()

			newLines = []
			n_letter = 0
		
			# iterate through text
			for line in pageText:
				n_letter += 1
				if line == "\n" and len(newLines) < 2:
					newLines.append(n_letter)
				
			# Cut string at new line to "omschrijving"
			partName = pageText[newLines[0] : pageText.find("Omschrijving")]

			# Cut string from article number to new line
			artStr = pageText[pageText.find("Artikelnummer:") + 14 : newLines[1]]

			# Extract number from string
			artNr = ""
			for char in artStr:
				if char.isdigit():
					artNr += char

			# check next pages
			for j in range(1,3):
				if i + j not in samPages and i + j < n_pages:
					pdfWriter.addPage(pdfReader.getPage(i + j))
				else:
					break

			# Read setting.ini file
			Config = ConfigParser()
			Config.read(settings_file)
			path = os.path.join(Config.get("PATH SETTINGS", "order_data"), jobID)

			# Define save path
			saveName = str(jobID) + ' SAM ' + str(samID) + '.pdf'
			savePath = os.path.join(path, saveName)

			# Save PDF
			samPDF = open(savePath,'wb')
			pdfWriter.write(samPDF)
			samPDF.close()

			# Create list of Filename,samID, partName, artNr and add to orderData 
			partData = [savePath, samID, partName, artNr]
			orderData.append(partData)

			samID += 1
			
	#return orderData


def get_drawing_data(drawing):

	#Script path
	path = os.path.abspath(os.path.dirname(sys.argv[0]))

	# get user name
	user = os.getlogin()

	#Tesseract executable
	pytesseract.pytesseract.tesseract_cmd = 'C:/Users/'+ user +'/AppData/Local/Tesseract-OCR/tesseract.exe'

	# Path to Poppler
	poppler_path= os.path.join(path, '/poppler-0.68.0/bin')

	# Open combined WO pdf
	with open(drawing, 'rb') as pdfFile:
		pdfReader = PyPDF2.PdfFileReader(pdfFile)
		page = pdfReader.getPage(0)
		
	# Convert to image, crop and save     
	images = convert_from_path(drawing, dpi=300, poppler_path=poppler_path)
	for image in images:
		left, upper, right, lower = image.getbbox()
		if right < lower:
			# Portrait
			temp_img = image.crop(((right - 1020), (lower - 300), (right - 380), (lower - 220)))     
		else:
			# Landscape
			temp_img = image.crop(((right - 970), (lower - 240), (right - 350), (lower - 155)))     
			
	# Get artNr and remove whitespace
	artNr = ''.join(pytesseract.image_to_string(temp_img).split())
	
	# Return atricle number from drawing
	return artNr


def combine_files(order_number):

	# Create drawingData dictionairy
	drawingData = {}
	# FOR DEBUGGING ONLY
	lastTime = datetime.now()

	# Define dirs
	# Read setting.ini file
	Config = ConfigParser()
	Config.read(settings_file)
	dftDir = os.path.join(Config.get("PATH SETTINGS", "order_data"), order_number, "DFT")

	count = 0

	# Run get_drawing_data on files in dir
	for drawing in os.listdir(dftDir):
		drawingPath = os.path.join(dftDir, drawing)
		artNr_dft = get_drawing_data(drawingPath)
		drawingData.update({artNr_dft : drawingPath})
		count += 1
	
	# Create WO PDF's and get orderData
	orderData = split_to_sam(order_number)

	# Match percentage
	match = 0.9

	# loop through orderData
	for order in orderData:
		artNr_wo = order[3][:-4]
		wo_pdf = str(order[0])
		foundPair = False

		# Create PdfFileMerger()
		pdfMerger = PyPDF2.PdfFileMerger()


		while foundPair == False:
			for key in drawingData:
				keyStr = key[:-4]
				counter = 0
				
				if len(artNr_wo) <= len(keyStr):
					for i in range(len(artNr_wo)):
						if artNr_wo[i] == keyStr[i]:
							counter += 1
				else:
					for i in range(len(keyStr)):
						if  keyStr[i] == artNr_wo[i]:
							counter += 1

				if counter > len(artNr_wo) * match:
					pdfMerger.append(PyPDF2.PdfFileReader(open(wo_pdf, 'rb')))
					pdfMerger.append(PyPDF2.PdfFileReader(open(drawingData[key], 'rb')))
					pdfMerger.write(wo_pdf)
					foundPair = True

	# FOR DEBUGGING ONLY
	# currentTime = datetime.now()

	# Time formatting
	time_delta = currentTime - lastTime
	
	# finish string
	finish_string = f'Program executed in {time_delta} seconds. \n{count} drawings combined'

	return finish_string


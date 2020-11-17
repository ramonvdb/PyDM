# PyDM

## What it does
This program takes a PDF file with all the production datasheets from a project and CAD drawings in PDF format and creates new PDF files combining the drawings with the corresponding datasheets.

## How it works
During execution the program does the following:

  1) Prompt a user to type in a specific order number using a simple GUI
  2) Check if the directory for the specific order number already exist and create the directory if not.
  3) Copy all the CAD drawings to a new folder in the order directory
  4) Iterate over all the CAD drawings and retrieve the article number of the drawing using OCR. This article number is combined with the file name        and saved in a dictionairy.
  5) Split the PDF containing the production datasheets in part specific PDF files.
  6) Iterate over all the seperate datasheets and combine them with the corresponding drawing.
  
## Challenges

### 1. Retrieving the article number from drawings
The biggest challenge was finding a way to retrieve the article number from the drawings. First i tried to retrieve the article number using the meta-data from the PDF. This didn't work because CAD program doesn't create usable meta-data when saving the drawings in PDF format. 

Next i tried converting the PDF to text but this did not yield any result because the article number is saved as picture block.

The last thing i could think of was implementing OCR using the Tesseract engine. For this to work i had to create a snippet from the drawing only displaying the article number. Because the drawings come in different orientations (A3 landscape and A4 portrait), the position of the article number differs. So i added a piece of code which checks the orientation and creates a snippet of the article number from the correct location.

Because OCR is not 100% accurate the characters from the OCR string are compared to the article numbers from the datasheets with a match percentage of 90%.


### 2. Splitting the PDF
The problem with splitting the PDF containing the datasheets was that some datasheets consist only of one page while others where two and even three pages long. To catch this problem i added a piece of code which adds all the pages with the JobID on it (JobID's are only on the first page of a datasheet) to a list which is used to split the file at the correct pages.


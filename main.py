import PyPDF2
import pyttsx3
import re

def clean_text(text, book_title, book_author):
    book_name_pattern = rf'{book_title} \d+'  
    book_author_pattern = rf'\d+ {book_author}'
    # print("Original text:\n", text)
    text = re.sub(book_name_pattern, '', text, flags=re.IGNORECASE)
    text = re.sub(book_author_pattern, '', text, flags=re.IGNORECASE)
    # print("Cleaned text:\n", text.strip())  # Debug: Print cleaned text
    return text.strip()
try:
    with open('test.pdf', 'rb') as path:
        pdfReader = PyPDF2.PdfReader(path)

        if len(pdfReader.pages) > 282:
            from_page = pdfReader.pages[282]

            text = from_page.extract_text()

            if text:
                book_title = "P R E T E N D  YO U  L OV E  M E"  
                book_author = "W. WINTERS & AMELIA WILDE"
                cleaned_text = clean_text(text, book_title, book_author)
                if cleaned_text:
                    engine = pyttsx3.init()
                    voices = engine.getProperty('voices')
                    engine.setProperty('voice', voices[1].id)
                    engine.save_to_file(cleaned_text, 'test.mp3')
                    # engine.say(cleaned_text)
                    engine.runAndWait()
                else:
                    print("No valid text found on the page after cleaning.")
            else:
                print("No text found on the page.")
        else:
            print("Page number out of range.")
except FileNotFoundError:
    print("The specified PDF file was not found.")
except Exception as e:
    print(f"An error occurred: {e}")

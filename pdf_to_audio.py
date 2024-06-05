import PyPDF2
import pyttsx3
import re


class PDFToAudioConverter:
    def __init__(self):
        self.book_title = ""
        self.book_author = ""
        self.narrator_gender = "female"  # default gender
        self.first_page = 0
        self.last_page = 0
        self.text = None

    def clean_text(self, text):
        book_name_pattern = rf'{self.book_title} \d+'
        book_author_pattern = rf'\d+ {self.book_author}'
        text = re.sub(book_name_pattern, '', text, flags=re.IGNORECASE)
        text = re.sub(book_author_pattern, '', text, flags=re.IGNORECASE)
        return text.strip()

    def get_text(self, pdf_path):
        combined_text = ""
        for page_number in range(self.first_page, self.last_page + 1):
            text = self.read_pdf(pdf_path, page_number)
            if text:
                cleaned_text = self.clean_text(text)
                if cleaned_text:
                    combined_text += cleaned_text + " "
                else:
                    print(f"No valid text found on page {page_number} after cleaning.")
            else:
                print(f"No text found on page {page_number}.")
        self.text = combined_text
        return combined_text

    def set_book_title(self, book_title):
        self.book_title = book_title

    def set_author_name(self, book_author):
        self.book_author = book_author

    def set_narrator_gender(self, gender):
        if gender in ["male", "female"]:
            self.narrator_gender = gender
        else:
            print("Invalid input. Defaulting to 'female'.")

    def set_pages_to_convert(self, first_page, last_page):
        self.first_page = first_page
        self.last_page = last_page

    def label_file(self):
        return f"{self.book_title}_pgs_{self.first_page}_{self.last_page}_{self.narrator_gender}.mp3"

    def read_pdf(self, pdf_path, page_number):
        try:
            with open(pdf_path, 'rb') as path:
                pdf_reader = PyPDF2.PdfReader(path)
                if len(pdf_reader.pages) > page_number:
                    return pdf_reader.pages[page_number].extract_text()
                else:
                    print("Page number out of range.")
                    return None
        except FileNotFoundError:
            print("The specified PDF file was not found.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def configure_tts_engine(self):
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        # Select voice based on gender
        voice_id = voices[0].id if self.narrator_gender.lower() == "male" else voices[1].id
        engine.setProperty('voice', voice_id)
        return engine

    def convert_text_to_audio(self, text, output_file):
        engine = self.configure_tts_engine()
        engine.save_to_file(text, output_file)
        engine.runAndWait()
        print(f"Audio saved as {output_file}")

    def convert_to_audio(self, pdf_path):
        combined_text = self.get_text(pdf_path)
        if combined_text:
            output_file = self.label_file()
            self.convert_text_to_audio(combined_text, output_file)
        else:
            print("No valid text found in the specified page range.")

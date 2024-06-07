import PyPDF2
import pyttsx3
import re
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

class PDFToAudioConverter:
    """
    A class to convert PDF text to audio files.

    Attributes:
    ----------
    book_title : str
        Title of the book to ignore in the text.
    book_author : str
        Author of the book to ignore in the text.
    narrator_gender : str
        Gender of the narrator ('male' or 'female').
    first_page : int
        The first page number to start narration.
    last_page : int
        The last page number to end narration.
    text : str
        The combined cleaned text from the PDF.
    output_folder : str
        Folder to save the output audio files.
    """

    def __init__(self):
        """Initialize the PDFToAudioConverter with default values."""
        self.book_title = ""
        self.book_author = ""
        self.narrator_gender = "female"  # default gender
        self.first_page = 0
        self.last_page = 0
        self.text = None
        self.output_folder = "outputs"

    def clean_text(self, text):
        """
        Clean the text by removing book title and author references.

        Parameters:
        ----------
        text : str
            The text to be cleaned.

        Returns:
        -------
        str
            The cleaned text.
        """
        book_name_pattern = rf'{self.book_title} \d+'
        book_author_pattern = rf'\d+ {self.book_author}'
        text = re.sub(book_name_pattern, '', text, flags=re.IGNORECASE)
        text = re.sub(book_author_pattern, '', text, flags=re.IGNORECASE)
        return text.strip()

    def get_text(self, pdf_path):
        """
        Extract and clean text from a range of pages in the PDF.

        Parameters:
        ----------
        pdf_path : str
            The path to the PDF file.

        Returns:
        -------
        str
            The combined cleaned text.
        """
        combined_text = ""
        for page_number in range(self.first_page, self.last_page + 1):
            text = self.read_pdf(pdf_path, page_number)
            if text:
                cleaned_text = self.clean_text(text)
                if cleaned_text:
                    combined_text += cleaned_text + " "
                else:
                    logging.warning(f"No valid text found on page {page_number} after cleaning.")
            else:
                logging.warning(f"No text found on page {page_number}.")
        self.text = combined_text
        return combined_text

    def set_book_title(self, book_title):
        """
        Set the book title to be ignored in the text.

        Parameters:
        ----------
        book_title : str
            The title of the book.
        """
        self.book_title = book_title

    def set_author_name(self, book_author):
        """
        Set the book author to be ignored in the text.

        Parameters:
        ----------
        book_author : str
            The author of the book.
        """
        self.book_author = book_author

    def set_narrator_gender(self, gender):
        """
        Set the gender of the narrator.

        Parameters:
        ----------
        gender : str
            The gender of the narrator ('male' or 'female').
        """
        if gender in ["male", "female"]:
            self.narrator_gender = gender
        else:
            logging.warning("Invalid input. Defaulting to 'female'.")

    def set_pages_to_convert(self, first_page, last_page):
        """
        Set the range of pages to convert.

        Parameters:
        ----------
        first_page : int
            The first page number.
        last_page : int
            The last page number.
        """
        self.first_page = first_page
        self.last_page = last_page

    def label_file(self):
        """
        Create a label for the output audio file based on the book details.

        Returns:
        -------
        str
            The labeled file name.
        """
        return f"{self.book_title}_pgs_{self.first_page}_{self.last_page}_{self.narrator_gender}.mp3"

    def read_pdf(self, pdf_path, page_number):
        """
        Read the text from a specific page of the PDF.

        Parameters:
        ----------
        pdf_path : str
            The path to the PDF file.
        page_number : int
            The page number to read from.

        Returns:
        -------
        str
            The extracted text from the page.
        """
        try:
            with open(pdf_path, 'rb') as path:
                pdf_reader = PyPDF2.PdfReader(path)
                if len(pdf_reader.pages) > page_number:
                    return pdf_reader.pages[page_number].extract_text()
                else:
                    logging.error("Page number out of range.")
                    return None
        except FileNotFoundError:
            logging.error("The specified PDF file was not found.")
            return None
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None

    def configure_tts_engine(self):
        """
        Configure the text-to-speech engine based on the narrator's gender.

        Returns:
        -------
        pyttsx3.Engine
            The configured text-to-speech engine.
        """
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        # Select voice based on gender
        voice_id = voices[0].id if self.narrator_gender.lower() == "male" else voices[1].id
        engine.setProperty('voice', voice_id)
        return engine

    def convert_text_to_audio(self, text, output_file):
        """
        Convert the cleaned text to an audio file.

        Parameters:
        ----------
        text : str
            The text to be converted to audio.
        output_file : str
            The name of the output audio file.

        Returns:
        -------
        str
            The path to the saved audio file.
        """
        engine = self.configure_tts_engine()
        output_path = os.path.join(self.output_folder, output_file)
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        logging.info(f"Audio saved as {output_path}")
        return output_path

    def convert_to_audio(self, pdf_path):
        """
        Convert the PDF to an audio file.

        Parameters:
        ----------
        pdf_path : str
            The path to the PDF file.

        Returns:
        -------
        str
            The path to the saved audio file.
        """
        combined_text = self.get_text(pdf_path)
        if combined_text:
            output_file = self.label_file()
            return self.convert_text_to_audio(combined_text, output_file)
        else:
            logging.error("No valid text found in the specified page range.")
            return None

from flask import Flask, render_template, redirect, url_for, flash, send_from_directory
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, FileField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange
import os
from pdf_to_audio import PDFToAudioConverter

app = Flask(__name__)
app.config['SECRET_KEY'] =  os.getenv('SECRET_KEY', 'default-secret-key')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
Bootstrap5(app)

# Form class
class PDFToAudioForm(FlaskForm):
    """
    A form for collecting input data to convert a PDF to an audio file.

    Attributes:
    ----------
    book_title : str
        Title of the book as it appears in the text to ignore.
    author : str
        Author of the book as it appears in the text to ignore.
    narrator_gender : str
        Gender of the narrator ('male' or 'female').
    first_page : int
        First page number to start narration.
    last_page : int
        Last page number to end narration.
    file : FileField
        The uploaded PDF file.
    submit : SubmitField
        The submit button for the form.
    """
    book_title = StringField('Title of Book as it appears in the text to ignore when creating audio', validators=[DataRequired()])
    author = StringField('Author name of Book as it appears in the text to ignore when creating audio', validators=[DataRequired()])
    narrator_gender = SelectField('Gender', choices=[
        ('male', 'male'),
        ('female', 'female'),
    ], validators=[DataRequired()])
    first_page = IntegerField('First Page to start narration', [NumberRange(min=0, max=999)])
    last_page = IntegerField('Last Page to end narration', [NumberRange(min=0, max=999)])
    file = FileField(validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route("/", methods=['GET', 'POST'])
def home():
    """
    Render the home page and handle form submission.

    Returns:
    -------
    str
        The rendered home page or a redirect to the download page.
    """
    form = PDFToAudioForm()
    if form.validate_on_submit():
        book_title = form.book_title.data
        author = form.author.data
        narrator_gender = form.narrator_gender.data
        first_page = form.first_page.data
        last_page = form.last_page.data
        file = form.file.data
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the PDF to audio conversion
        converter = PDFToAudioConverter()
        converter.set_book_title(book_title)
        converter.set_author_name(author)
        converter.set_narrator_gender(narrator_gender)
        converter.set_pages_to_convert(first_page, last_page)
        audio_file_path = converter.convert_to_audio(file_path)

        if audio_file_path:
            flash('The audio file has been successfully created. Click the link below to download it.', 'success')
            return redirect(url_for('download_file', filename=os.path.basename(audio_file_path)))
        else:
            flash('Failed to create the audio file. Please check the PDF and try again.', 'danger')
    return render_template("index.html", form=form)

@app.route('/download/<filename>')
def download_file(filename):
    """
    Serve the generated audio file for download.

    Parameters:
    ----------
    filename : str
        The name of the audio file to be downloaded.

    Returns:
    -------
    Response
        The response object for file download.
    """
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
    app.run(debug=True)

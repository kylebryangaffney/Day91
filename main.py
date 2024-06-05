from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, FileField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange
import os
from pdf_to_audio import PDFToAudioConverter

app = Flask(__name__)
app.config['SECRET_KEY'] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
app.config['UPLOAD_FOLDER'] = 'uploads'
Bootstrap5(app)

# Form class
class PDFToAudioForm(FlaskForm):
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
        converter.convert_to_audio(file_path)

        return redirect(url_for('home'))
    return render_template("index.html", form=form)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)

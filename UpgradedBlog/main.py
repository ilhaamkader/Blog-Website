from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date, datetime
import smtplib
from email.message import EmailMessage

my_email = "lokiofassguardd@gmail.com"
password = "grgw rjii krle prtn"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # Retrieve the post from the database based on post_id
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post)


class BlogPostForm(FlaskForm):
    title = StringField('Blog Post Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    author = StringField('Your Name', validators=[DataRequired()])
    img_url = StringField('Blog Image URL', validators=[DataRequired()])
    body = CKEditorField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

# TODO: add_new_post() to create a new blog post
@app.route('/new-post', methods=['GET', 'POST'])
def new_post():
    form = BlogPostForm()
    action = 'New Post'
    if form.validate_on_submit():
        # Create a new BlogPost object and populate it with form data
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            author=form.author.data,
            img_url=form.img_url.data,
            date=datetime.now().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        # Commit changes to the database
        db.session.commit()
        # Redirect to the home page
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=form, action=action)


@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    form = BlogPostForm(obj=post)

    if form.validate_on_submit():
        # Update the post object with the form data
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.body = form.body.data
        post.author = form.author.data
        post.img_url = form.img_url.data

        db.session.commit()

        return redirect(url_for('show_post', post_id=post.id))

    return render_template("make-post.html", form=form, action="Edit Post", post=post)



@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        send_email(data["name"], data["email"], data["phone"], data["message"])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)

def send_email(name, email, phone, message):
    msg = EmailMessage()
    msg.set_content(f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}")
    msg["Subject"] = "New Contact Form Submission"
    msg["From"] = my_email
    msg["To"] = "kaderilhaam@gmail.com"
    with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
        smtp.starttls()
        smtp.login(user=my_email, password=password)
        smtp.send_message(msg)


if __name__ == "__main__":
    app.run(debug=True, port=5003)

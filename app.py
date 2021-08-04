import click
from dynamic_qr import app, db
from dynamic_qr.models import User, QRCode

app.run()


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, QRCode=QRCode)


@app.cli.command("create-user")
@click.argument("username")
@click.argument("email")
@click.argument("password")
def create_user(username, email, password):
    try:
        user = User(username=username, email=email)
        user.set_password(password=password)
        db.session.add(user)
        db.session.commit()
        print("New user {} with email {} created".format(user, email))
    except:
        print("Something went wrong")


@app.cli.command("update-password")
@click.argument("username")
@click.argument("email")
@click.argument("password")
def update_password(username, email, password):
    try:
        user = User.query.filter_by(email=email).first()
        user.set_password(password=password)
        db.session.add(user)
        db.session.commit()
        print("User {} with email {} updated password".format(user, email))
    except:
        print("Something went wrong")


@app.cli.command("update-email")
@click.argument("username")
@click.argument("email")
@click.argument("password")
def update_email(username, email, password):
    try:
        user = User.query.filter_by(email=email).first()
        user.email = email
        db.session.add(user)
        db.session.commit()
        print("User {} with email {} updated password".format(user, email))
    except:
        print("Something went wrong")


@app.cli.command("delete-user")
@click.argument("username")
@click.argument("email")
@click.argument("password")
def delete_user(username, email, password):
    try:
        user = User.query.filter_by(email=email).first()
        db.session.delete(user)
        db.session.commit()
        print("User {} with email {} deleted".format(user, email))
    except:
        print("Something went wrong")

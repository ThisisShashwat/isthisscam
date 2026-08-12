from datetime import datetime

from flask import Flask, render_template, request, redirect
from sqlalchemy.orm import selectinload
from sqlmodel import select, Session

from utils.db_utils import init_db, engine
from utils.insta_utils import get_thread_id
from utils.models import Messages

app = Flask(__name__, static_folder="media", static_url_path="/media")

THREAD_ID = get_thread_id(None, test=True)
init_db()


@app.route("/")
def home():
    return redirect(f"/chat/{THREAD_ID}")

@app.route("/chat/<thread_id>")
def chat(thread_id):
    with Session(engine) as session:
        messages = session.exec(
            select(Messages)
            .where(Messages.thread_id == thread_id)
            .order_by(Messages.timestamp)
            .options(selectinload(Messages.replied_to))
        ).all()

    return render_template("chat.html", messages=messages, thread_id=THREAD_ID, after=None)


@app.route("/chat/<thread_id>/poll")
def poll(thread_id):
    after = request.args.get("after")

    with Session(engine) as session:
        query = select(Messages).where(Messages.thread_id == thread_id)
        if after:
            query= query.where(Messages.timestamp > datetime.fromisoformat(after))
            query = query.order_by(Messages.timestamp)
            query = query.options(selectinload(Messages.replied_to))

            messages = session.exec(query).all()

        return render_template("bubbles.html", messages=messages, thread_id=thread_id, after=after)


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")

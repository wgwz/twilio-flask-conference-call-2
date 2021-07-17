import logging
from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO, emit
from twilio.twiml.voice_response import Dial, Gather, VoiceResponse


logging.basicConfig(level="DEBUG")
logger = logging.getLogger()
app = Flask(__name__)
app.config.update({"SECRET_KEY": "mysecret"})
socketio = SocketIO(app)


@app.route("/conference", methods=["POST"])
def conference():
    print(f"{request.form=}")
    response = VoiceResponse()
    pin_code = request.form.get("Digits")
    if pin_code and pin_code == "12345":
        dial = Dial()
        dial.conference(
            "Twilio Test Conference",
            status_callback="/events",
            status_callback_event="start end join leave mute hold",
        )
        response.append(dial)
    else:
        gather = Gather(action="/conference")
        gather.say("Please enter your conference pin,\nfollowed by the pound sign")
        response.append(gather)
    return Response(str(response), mimetype="text/xml")


@app.route("/events", methods=["POST"])
def events():
    socketio.emit("conference event", dict(request.form))
    return "", 200


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    socketio.run(app, use_reloader=True)

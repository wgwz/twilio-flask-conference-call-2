from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO, emit
from twilio.twiml.voice_response import Dial, Gather, VoiceResponse


app = Flask(__name__)
app.config.update({"SECRET_KEY": "mysecret"})
socketio = SocketIO(app)
caller_cache = {}


@app.route("/conference", methods=["POST"])
def conference():
    print(f"/conference: {request.form=}")
    print(f"/conference: {caller_cache=}")
    response = VoiceResponse()
    pin_code = request.form.get("Digits")
    call_sid = request.form.get("CallSid")
    caller = request.form.get("Caller")
    if call_sid and caller:
        caller_cache[call_sid] = caller
    if pin_code and pin_code == "12345":
        dial = Dial()
        dial.conference(
            "Twilio Test Conference",
            status_callback="/events",
            status_callback_event="start end join leave mute hold speaker",
        )
        response.append(dial)
    else:
        gather = Gather(action="/conference")
        gather.say("Please enter your conference pin,\nfollowed by the pound sign")
        response.append(gather)
    return Response(str(response), mimetype="text/xml")


conference_events = []


@app.route("/events", methods=["POST"])
def events():
    print(f"/events: {request.form=}")
    print(f"/events: {caller_cache=}")
    data = dict(request.form)
    call_sid = data.get("CallSid")
    caller = caller_cache.get(call_sid)
    if call_sid and caller:
        data["Caller"] = caller
    socketio.emit("conference event", data)
    if data["StatusCallbackEvent"] == "conference-end":
        conference_events.clear()
    else:
        conference_events.append(data)
    return "", 200


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def on_connect():
    for event in conference_events:
        emit("conference event catchup", event)


if __name__ == "__main__":
    socketio.run(app, use_reloader=True)

from flask import Flask, request,redirect,url_for, jsonify, render_template
from twilio.util import TwilioCapability
from twilio import TwilioRestException 
import twilio.twiml
from twilio.rest import TwilioRestClient
import re
 
DEBUG= True 
 
app = Flask(__name__)
app.config.from_object(__name__)
 
# Add a Twilio phone number or number verified with Twilio as the caller ID
caller_id = "+17788002755"
 
# put your default Twilio Client name here, for when a phone number isn't given
default_client = "jenny"

account_sid = "xxxxxxxxxxx"
auth_token = "xxxxxxxxxxx"
application_sid = "xxxxxxxxxxx"

 
@app.route('/voice', methods=['GET', 'POST'])
def voice():
	resp = twilio.twiml.Response()
	#phone number for voice and sms
	to_number = request.values.get('phone', None)
	#speech parama
	dialogue = request.values.get('dialogue', None)
	voice_gender = request.values.get('voice', None)
	lang = request.values.get('language', None)
	#sms params
	body = request.values.get('body', None)
	#action
	action = request.values.get('action', None)

	if lang == "English":
		lang = "en"
	else:
		lang = "fr"

	if action == "voice":
		with resp.dial(callerId=caller_id) as r: 
		# If we have a number, and it looks like a phone number:
			if to_number  and re.search('^[\d\(\)\- \+]+$', to_number):
				r.number(to_number)
			else:
				r.client(default_client)
	elif action == "speech":
		if dialogue:
			dialogue_kwargs = {'voice': voice_gender, 'language' : lang}
			resp.say(dialogue, **dialogue_kwargs)

	return str(resp)

	
@app.route('/call', methods=['GET', 'POST'])
def call():
	#account_sid = "AC4273cb19463cc24c4eedc5ac8f0ede0a"
	#auth_token = "abca2cd531a6d58379aadad992fdffbe"
	client = TwilioRestClient(account_sid, auth_token)
	call = client.calls.create(to="+17787886939", from_="+17788002755",url="file.mp3")
	#print call.length
	return call.sid

@app.route('/twimlme',methods=['GET', 'POST'])
def twimlme():
	resp = twilio.twiml.Response()
	voiceVal = request.values.get("voice")
	smsVal = request.values.get("sms")
	if(voiceVal=="true"):
		resp.play("http://demo.twilio.com/hellomonkey/monkey.mp3")
	if(smsVal)=="true":
		resp.sms("woohaha")
	return str(resp)



@app.route('/broadcast', methods=['GET', 'POST'])
def broadcast():
	client = TwilioRestClient(account_sid, auth_token)
	getVals = ["phone_1", "phone_2", "phone_3"]
	phonesToCall =[]
	voiceVal = request.values.get("voice")
	smsVal = request.values.get("sms")
	for getVal in getVals:
		phoneNum= request.values.get(getVal, None)
		if (phoneNum is not None and re.search('^[\d\(\)\- \+]+$', phoneNum)):
			phonesToCall.append(phoneNum)
	if len(phonesToCall)==0:
		return jsonify(message="no phone to call...")		
	# to send voice, or voice + sms combo	
	if(voiceVal=="true" and smsVal=="true") or (voiceVal=="true"):
		for index, phoneToCall in enumerate(phonesToCall):
				try:
					call = client.calls.create(to=phoneToCall, from_="+17788002755",url="http://twilio-epact.herokuapp.com/twimlme?voice="+voiceVal + "&sms=" +smsVal)
				except:
					return jsonify(message='oops. something went terribly wrong')
	#to send sms only....
	if(voiceVal!="true" and smsVal=="true"):
		for index, phoneToCall in enumerate(phonesToCall):
				try:
					message = client.sms.messages.create(to=phoneToCall, from_="+17788002755",body="woohahahah")
				except:
					return jsonify(message='oops. something went terribly wrong')	
	return jsonify(message="Call(s) made...")

@app.route('/broadcastclient', methods=['GET', 'POST'])
def broadcastclient():
	return render_template('broadcast.html')


@app.route('/')
def hello():
 	return render_template('home.html')

 
@app.route('/voiceclient', methods=['GET', 'POST'])
def voiceclient():

    capability = TwilioCapability(account_sid, auth_token)
    capability.allow_client_outgoing(application_sid)
    token = capability.generate()
 
    return render_template('voiceclient.html', token=token)


@app.route('/smsclient', methods=['GET','POST'])
def smsclient():
	capability = TwilioCapability(account_sid, auth_token)
	capability.allow_client_outgoing(application_sid)
	token = capability.generate()
 	return render_template('smsclient.html', token=token)


@app.route('/sms', methods=['GET','POST'])
def sms():

	#phone number for voice and sms
	#to_number = request.values.get('FromNumber', None)
	callers = {
	"+16047606930": "Kirsten",
	"+17782316618": "Christine",
	"+17787886939": "DR",
	"+16045613675" : "Fruit Bat"
	}

	from_number = request.values.get('From', None)
	if from_number in callers:
		message = callers[from_number] + ", welcome to ePACT!"
	else:
		message = "Crazy Monkey, thanks for the message!"

	resp = twilio.twiml.Response()
	resp.sms(message)
 
	return str(resp)

@app.route('/SMSreply', methods=['GET','POST'])
def SMSreply():
	return render_template('SMSreply.html')


@app.route('/sendsms', methods=['GET','POST'])
def sendsms():

	client = TwilioRestClient(account_sid, auth_token)

	to = request.values.get('phone', None)
	#invalid phone number?
	if not(re.search('^[\d\(\)\- \+]+$', to)):
		return jsonify(type='error',message='invalid phone number')

	body = request.values.get('body', None)
	if not(body):
		return jsonify(type='error',message='no message')
	try:
		message = client.sms.messages.create(to=to, from_="+17788002755",body=body)
	except TwilioRestException as err:
		return jsonify(message='oops. something went terribly wrong')
	
	return jsonify(message="Message successfully sent to " + str(to))


@app.route('/speechclient', methods=['GET','POST'])
def speechclient():
    capability = TwilioCapability(account_sid, auth_token)
    capability.allow_client_outgoing(application_sid)
    token = capability.generate()
 
    return render_template('speechclient.html', token=token)


 
if __name__ == "__main__":
    app.run(debug=True)
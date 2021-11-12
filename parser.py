#!/usr/bin/python3

def alertParser(msg_subject, msg_body):
	
	if "failed" in msg_subject.lower():
		return ('alert')
	
	elif "failed" in msg_body.lower():
		return ('alert')

	# can create more parsing rules with more elif's...

	else:
		return ('ok')

import uuid

def get_uid():
	return str(uuid.uuid4())[:8]
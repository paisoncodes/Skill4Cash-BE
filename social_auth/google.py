from google.auth.transport import requests
from google.oauth2 import id_token

class Google:
	"""
	Google class to fetch the user
	information
	"""

	@staticmethod
	def gg_validate(token):
		"""
		Validate method queries the 
		Google OAUTH2 API to fetch the 
		user information
		"""
		try:
			id_info = id_token.verify_oauth2_token(token, requests.Request())
			if 'accounts.google.com' in id_info['iss']:
				return id_info
		except:
			return None


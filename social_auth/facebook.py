import facebook

class Facebook:
	"""
	Facebook class to fetch the user
	information
	"""

	@staticmethod
	def fb_validate(auth_token):
		"""
		Validate method queries the facebook
		GraphAPI to fetch the user information
		"""
		try:
			graph = facebook.GraphAPI(access_token=auth_token)
			# scope we need (email, id, name, phonenumber, state, city)
			profile = graph.request('/me?fields=id,name,email')
			return profile
		except:
			return "Invalid Token."

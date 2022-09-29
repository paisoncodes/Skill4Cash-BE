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
			# scope we need (email, id, first_name,last_name)
			profile = graph.request('/me?fields=id,email,first_name,last_name')
			return profile
		except:
			return None

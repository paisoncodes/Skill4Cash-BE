from django.core.management.base import BaseCommand
import requests

from utils.models import Lga, State


class Command(BaseCommand):

    def add_states(self):
        url_1 = "https://api.facts.ng/v1/states/"
        response = requests.request("GET", url_1)
        for state in response.json():
            state_, created_ = State.objects.get_or_create(state=state["name"])
            lgas = (requests.request("GET", state["uri"])).json()
            for lga in lgas["lgas"]:
                lga__, created__ = Lga.objects.get_or_create(lga=lga, state=state_)
        abuja, created = State.objects.get_or_create(state="FCT")
        _lgas = ["Abaji", "Municipal", "Bwari", "Gwagwalada", "Kuje", "Kwali"]
        for _lga in _lgas:
            __lga, __create = Lga.objects.get_or_create(lga=_lga, state=abuja)

    
    def handle(self, *args, **options):
        print("Started")
        self.add_states()
        print("Done")


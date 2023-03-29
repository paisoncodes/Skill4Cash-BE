from django.core.management.base import BaseCommand
import requests

from utils.models import Lga, State


class Command(BaseCommand):

    def add_states(self):
        url_1 = "https://api.facts.ng/v1/states/"
        response = requests.request("GET", url_1)
        for state in response.json():
            if not State.objects.filter(state=state["name"]).exists():
                state_ = State.objects.create(state=state["name"])
                lgas = (requests.request("GET", state["uri"])).json()
                for lga in lgas["lgas"]:
                    if not Lga.objects.filter(lga=lga, state=state_).exists():
                        Lga.objects.create(lga=lga, state=state_)
                    continue
            continue

    
    def handle(self, *args, **options):
        print("Started")
        self.add_states()
        print("Done")


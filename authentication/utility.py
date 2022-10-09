from authentication.models import User


def update_customer(instance:dict, validated_data:dict) -> dict:
    update_data = {
        "id": instance["id"],
        "first_name": instance["first_name"] if "first_name" not in validated_data.keys() else validated_data["first_name"],
        "last_name": instance["last_name"] if "last_name" not in validated_data.keys() else validated_data["last_name"],
        "email": instance["email"] if "email" not in validated_data.keys() else validated_data["email"],
        "state": instance["state"] if "state" not in validated_data.keys() else validated_data["state"],
        "city": instance["city"] if "city" not in validated_data.keys() else validated_data["city"],
        "profile_picture": instance["profile_picture"] if "profile_picture" not in validated_data.keys() else validated_data["profile_picture"],
    }
    return update_data



def update_service_provider(instance, validated_data):
    update_data = {
        "id": instance["id"],
        "first_name": instance["first_name"] if "first_name" not in validated_data.keys() else validated_data["first_name"],
        "last_name": instance["last_name"] if "last_name" not in validated_data.keys() else validated_data["last_name"],
        "email": instance["email"] if "email" not in validated_data.keys() else validated_data["email"],
        "state": instance["state"] if "state" not in validated_data.keys() else validated_data["state"],
        "city": instance["city"] if "city" not in validated_data.keys() else validated_data["city"],
        "profile_picture": instance["profile_picture"] if "profile_picture" not in validated_data.keys() else validated_data["profile_picture"],
        "keywords": instance["keywords"] if "keywords" not in validated_data.keys() else validated_data["keywords"],
        "gallery": instance["gallery"] if "gallery" not in validated_data.keys() else validated_data["gallery"],
        "card_front": instance["card_front"] if "card_front" not in validated_data.keys() else validated_data["card_front"],
        "card_back": instance["card_back"] if "card_back" not in validated_data.keys() else validated_data["card_back"],
        "pob": instance["pob"] if "pob" not in validated_data.keys() else validated_data["pob"],
        "service_category": instance["service_category"] if "service_category" not in validated_data.keys() else validated_data["service_category"],
        "business_name": instance["business_name"] if "business_name" not in validated_data.keys() else validated_data["business_name"],
    }
    return update_data

def get_user(phone_number:str=None, email:str=None):
    if phone_number:
        User.objects.get(phone_number=phone_number)
    else:
        User.objects.get(email=email)
from pydantic import BaseModel, ConfigDict

from src.authorization.models import User
from src.profiles import service
from src.profiles.models import Profile

from src import database




def main(*argv):
    database.init_db()

    pipeline = [
        {"$geoNear": {
            "near": {"type": "Point", "coordinates": [10.634584, 35.8245029]}, "distanceField": "coordinates",
            "spherical": True
        }}
    ]

    result = list(Profile.objects.aggregate(*pipeline))
    print(result)

    database.close_db()


if __name__ == '__main__':

    main()

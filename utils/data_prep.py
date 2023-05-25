import json
import pandas as pd

given_names = []
surnames = []

with open("dev_data/names.txt") as f:
    for line in f.readlines():
        first, last = line.strip().split(" ")
        given_names.append(first)
        surnames.append(last)


with open("dev_data/emails.txt", "r") as f:
    emails = list(line.strip() for line in f.readlines())

cities_df = pd.read_csv("dev_data/worldcities.csv", nrows=1000)
cities = (
    cities_df[["city_ascii", "country"]]
    .apply(lambda row: row["city_ascii"] + ", " + row["country"], axis=1)
    .tolist()
)

with open("../synthwave/data.json", "w") as f:
    json.dump(
        {
            "given_name": given_names,
            "family_name": surnames,
            "location": cities,
            "email": emails,
        },
        f,
    )

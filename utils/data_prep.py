import json
import pandas as pd

given_names = []
surnames = []

given_df = pd.read_csv("dev_data/NationalNames.csv")

for gender in ("F", "M"):
    given_names.extend(
        given_df.query(f"Gender == '{gender}'")
        .sort_values("Count", ascending=False)
        .drop_duplicates(subset=["Name"])
        .head(500)["Name"]
        .tolist()
    )

surname_df = pd.read_csv("dev_data/Names_2010Census_Top1000.csv", nrows=1000)
surnames.extend(surname_df["SURNAME"].apply(lambda s: s.lower().capitalize()).tolist())

cities_df = pd.read_csv("dev_data/worldcities.csv", nrows=1000)
cities = (
    cities_df[["city_ascii", "country"]]
    .apply(lambda row: row["city_ascii"] + ", " + row["country"], axis=1)
    .tolist()
)

with open("synthwave/data.json", "w") as f:
    json.dump(
        {"given_name": given_names, "family_name": surnames, "locations": cities}, f
    )

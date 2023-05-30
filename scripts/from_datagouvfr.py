"""
Update the datapackage from data.gouv.fr source
"""
import requests

from frictionless import Package, Resource

pkg = Package("datapackage.yaml")

dgf_api_url = next(s["path"] for s in pkg.sources if s["title"] == "datagouvfr")

r = requests.get(dgf_api_url)
data = r.json()

r = requests.get(data["resources"]["href"])
data = r.json()

resources = data["data"]

while next_page := data["next_page"]:
    r = requests.get(next_page)
    data = r.json()
    resources += data["data"]

versions = []
for resource in resources:
    slug = resource["title"].replace(".csv", "")
    version = slug.split("-")[-1]
    versions.append(version)
    if not pkg.has_resource(slug) and resource["format"] == "csv":
        pkg.add_resource(Resource(**{
            "name": slug,
            "path": resource["latest"],
            "datatype": "table",
            "format": "csv",
            "mediatype": "text/csv",
            "encoding": "utf-8",
            "schema": "schema.yaml",
        }))

pkg.version = max(versions)
pkg.to_yaml("datapackage.yaml")

print(f"Updated datapackage, now has {len(pkg.resources)} resources.")

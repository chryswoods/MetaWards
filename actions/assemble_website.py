import metawards
import sys
import os
from distutils import dir_util
import glob
import json

branch = metawards.__branch__
release = metawards.__version__
version = metawards.__version__.split("+")[0]

if version.find("untagged") != -1:
    print("This is an untagged branch")
    version = metawards.__manual_version__

print(f"Build docs for branch {branch} version {version}")

# we will only build docs for the master and devel branches
# (as these are moved into special locations)
is_tagged_release = False

if branch not in ["master", "devel"]:
    if branch.find(version) != -1:
        print(f"Building the docs for tag {version}")
        is_tagged_release = True
    else:
        print(f"We don't assemble the website for branch {branch}")
        sys.exit(0)

os.environ["METAWARDS_VERSION"] = version
os.environ["METAWARDS_BRANCH"] = branch
os.environ["METAWARDS_RELEASE"] = release
os.environ["METAWARDS_REPOSITORY"] = metawards.__repository__
os.environ["METAWARDS_REVISIONID"] = metawards.__revisionid__

if not os.path.exists("./gh-pages"):
    print("You have not checked out the gh-pages branch correctly!")
    sys.exit(-1)

# if this is the master branch, then copy the docs to both the root
# directory of the website, and also to the 'versions/version' directory
if is_tagged_release or (branch == "master"):
    print(f"Copying main docs to gh-pages and gh-pages/versions/{version}")
    dir_util.copy_tree("doc/build/html/", "gh-pages/")
    dir_util.copy_tree("doc/build/html/", f"gh-pages/versions/{version}/")

elif branch == "devel":
    dir_util.copy_tree("doc/build/html/", "gh-pages/versions/devel/")

# now write the versions.json file
versions = []
versions.append(["latest", "/"])
versions.append(["development", "/versions/devel/"])

vs = {}

for version in glob.glob("gh-pages/versions/*"):
    if version.find("devel") == -1:
        version = version.split("/")[-1]
        vs[version] = f"/versions/{version}/"

# remove / deduplicate files into symlinks

keys = list(vs.keys())
keys.sort()

for i in range(len(keys)-1, -1, -1):
    versions.append([keys[i], vs[keys[i]]])

print(f"Saving paths to versions\n{versions}")

with open("gh-pages/versions.json", "w") as FILE:
    json.dump(versions, FILE)

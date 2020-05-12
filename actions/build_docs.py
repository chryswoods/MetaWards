
import metawards
import sys
import os
import subprocess
import shlex

branch = metawards.__branch__
release = metawards.__version__
version = metawards.__version__.split("+")[0]

if version.find("untagged") != -1:
    print("This is an untagged branch")
    version = metawards.__manual_version__

print(f"Build docs for branch {branch} version {version}")

# we will only build docs for the master and devel branches
# (as these are moved into special locations)

if branch not in ["master", "devel"]:
    if branch.find(version) != -1:
        print(f"Building the docs for tag {version}")
        is_tagged_release = True
    else:
        print(f"We don't build the docs for branch {branch}")
        sys.exit(0)

os.environ["METAWARDS_VERSION"] = version
os.environ["METAWARDS_BRANCH"] = branch
os.environ["METAWARDS_RELEASE"] = release
os.environ["METAWARDS_REPOSITORY"] = metawards.__repository__
os.environ["METAWARDS_REVISIONID"] = metawards.__revisionid__


def run_command(cmd, dry=False):
    """Run the passed shell command"""
    if dry:
        print(f"[DRY-RUN] {cmd}")
        return

    print(f"[EXECUTE] {cmd}")

    try:
        args = shlex.split(cmd)
        subprocess.run(args).check_returncode()
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(-1)


# install doc dependencies
run_command("pip install sphinx sphinx_issues sphinx_rtd_theme "
            "sphinxcontrib-programoutput")

# make the documentation
run_command("make doc")

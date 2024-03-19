import os
import sys
import subprocess


def _get_tag():
    git_tags = subprocess.run(
        ["git", "tag", "--sort", "-creatordate"],
        capture_output=True
    ).stdout.decode("ascii").split("\n")
    prod_tags = [
        x for x in git_tags if ("dev" not in x) and ("chart-release" not in x) and ("asm2vec-pytorch" not in x)
    ]
    latest_tag = prod_tags[0]
    return latest_tag


def _get_mac_fix():
    """Due to: https://github.com/lmquang/til/issues/18 we add this fix"""
    if sys.platform.startswith("linux"):
        return ""
    else:
        return "''"


def update_version():
    tag = _get_tag()
    fix = _get_mac_fix()
    os.system(f"sed -i {fix} 's/package_version/{tag}/g' asm2vec/version.py")


def reset_version():
    tag = _get_tag()
    fix = _get_mac_fix()
    os.system(f"sed -i {fix} 's/{tag}/package_version/g' asm2vec/version.py")

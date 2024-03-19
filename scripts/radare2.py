import os
import sys
import platform


def install(version: str) -> None:
    if sys.platform.startswith("linux"):
        machine = platform.machine()
        if machine in ["aarch64", "arm"]:
            architecture = "arm64"
        elif machine in ["x86_64"]:
            architecture = "amd64"
        elif machine in ["i386", "i686"]:
            architecture = "i386"
        else:
            raise Exception(f"No architecture for Linux Machine: '{machine}'")

        commands = [
            "apt-get update",
            "apt-get install -y --no-install-recommends wget",
            f"wget -O /tmp/radare2_{version}_{architecture}.deb https://github.com/radareorg/radare2/releases/download/{version}/radare2_{version}_{architecture}.deb",
            f"dpkg -i /tmp/radare2_{version}_{architecture}.deb",
            "r2pm init",
            "r2pm update",
            f"rm /tmp/radare2_{version}_{architecture}.deb"
        ]
        for command in commands:
            if os.system(command) != 0:
                raise Exception(f"Install 'radare2' failed: '{command}'")
    else:
        print("Ensure 'radar2' is installed...")

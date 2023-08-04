import subprocess

command = ["gcloud", "endpoints", "configs", "list", "--service=gateway-uavkhjofda-nw.a.run.app"]
output = subprocess.check_output(command, shell = True,  universal_newlines=True)
CONFIG_ID = output.splitlines()[1].split(' ')[0]
print(CONFIG_ID)
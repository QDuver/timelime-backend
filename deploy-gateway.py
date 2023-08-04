import subprocess

output = subprocess.check_output("gcloud endpoints configs list --service=gateway-uavkhjofda-nw.a.run.app", shell = True,  universal_newlines=True)
CONFIG_ID = output.splitlines()[1].split(' ')[0]
print(f"::set-output name=id::{CONFIG_ID}")
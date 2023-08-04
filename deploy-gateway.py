import subprocess
import re

# Replace this with your actual service name
service_name = "gateway-uavkhjofda-nw.a.run.app"


# command = ["gcloud", "endpoints", "services", "deploy", "openapi-run.yaml", "--project", "timelime-dev"]
# subprocess.call(command, shell = True)

# command = ["gcloud", "endpoints", "configs", "list", "--service=" + service_name]
# output = subprocess.check_output(command, shell = True,  universal_newlines=True)
# CONFIG_ID = output.splitlines()[1].split(' ')[0]

# command = ["./gcloud_build_image.sh", "-s", "gateway-uavkhjofda-nw.a.run.app", "-c", CONFIG_ID, "-p", "timelime-dev"]
# subprocess.call(command, shell = True)

# commad = ["gcloud", "run", "deploy", "gateway", "--image=gcr.io/timelime-dev/endpoints-runtime-serverless:2.45.0-gateway-uavkhjofda-nw.a.run.app-"+CONFIG_ID, "--allow-unauthenticated", "--region", "europe-west2", "--platform", "managed", "--project=timelime-dev"]
# subprocess.call(command, shell = True)


command = "./gcloud_build_image.sh -s gateway-uavkhjofda-nw.a.run.app -c 2023-08-04r0 -p timelime-dev"

# Run the command using subprocess
try:
    subprocess.run(command, shell=True, check=True)
    print("Command executed successfully.")
except subprocess.CalledProcessError as e:
    print("Error executing the command:", e)
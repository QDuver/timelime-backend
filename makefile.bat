
docker build . -t timelime-backend-img
docker run -p 5000:5000 -e GOOGLE_APPLICATION_CREDENTIALS=secrets/timelime-dev-sa.json timelime-backend-img
gcloud run deploy timelime-backend --region=europe-west2 --source . --port 5000

gcloud endpoints services deploy openapi-run.yaml --project timelime-dev

//deploy ESPVv2 default Docker Image
gcloud run deploy gateway --image="gcr.io/endpoints-release/endpoints-runtime-serverless:2" --allow-unauthenticated --region europe-west2 --platform managed

//Deploy ESPv2 Docker image
chmod +x gcloud_build_image.sh
./gcloud_build_image.sh -s gateway-uavkhjofda-nw.a.run.app -c 2023-08-04r0 -p timelime-dev
gcloud run deploy gateway --image="gcr.io/timelime-dev/endpoints-runtime-serverless:2.45.0-gateway-uavkhjofda-nw.a.run.app-2023-08-04r0" --allow-unauthenticated --region europe-west2 --platform managed --project=timelime-dev


https://gateway-uavkhjofda-nw.a.run.app
curl --request GET --header "content-type:application/json" "https://gateway-uavkhjofda-nw.a.run.app/quentino"

gcloud endpoints configs list --service=gateway-uavkhjofda-nw.a.run.app



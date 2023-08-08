
docker build . -t timelime-backend-img
docker run -p 5000:5000 -e GOOGLE_APPLICATION_CREDENTIALS=secrets/timelime-dev-sa.json timelime-backend-img
gcloud run deploy timelime-backend --region=europe-west2 --source . --port 5000 --no-allow-unauthenticated

gcloud endpoints services deploy openapi-run.yaml --project timelime-dev


gcloud auth print-access-token main-641@timelime-dev.iam.gserviceaccount.com
gcloud config set account main-641@timelime-dev.iam.gserviceaccount.com
curl --request GET https://gateway-uavkhjofda-nw.a.run.app/quentinoo --header "Authorization: Bearer ${gcloud auth print-access-token}"
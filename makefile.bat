
docker build . -t timelime-backend-img
docker run -p 5000:5000 -e GOOGLE_APPLICATION_CREDENTIALS=secrets/timelime-dev-sa.json timelime-backend-img
gcloud run deploy timelime-backend --region=europe-west2 --source . --port 5000 --no-allow-unauthenticated

gcloud endpoints services deploy openapi-run.yaml --project timelime-dev



curl -X POST \
     -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
     -H "Content-Type: application/json" \
     -d @request_payload.json https://<CLOUD_RUN_SERVICE_URL>


curl -X POST "https://oauth2.googleapis.com/token" -d "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=$(cat secrets/timelime-dev-7f677154d05e.json)"

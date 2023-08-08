
docker build . -t timelime-backend-img
docker run -p 5000:5000 -e GOOGLE_APPLICATION_CREDENTIALS=secrets/timelime-dev-sa.json timelime-backend-img
gcloud run deploy timelime-backend --region=europe-west2 --source . --port 5000 --no-allow-unauthenticated

gcloud endpoints services deploy openapi-run.yaml --project timelime-dev

gcloud sql export csv avito-db-instance gs://avito-bronze-bucket-central1/Adsinfo.csv \
    --database=avito_db \
    --query="SELECT * FROM AdsInfo"

gcloud sql export csv avito-db-instance gs://avito-bronze-bucket-central1/Location.csv \
    --database=avito_db \
    --query="SELECT * FROM Location"

gcloud sql export csv avito-db-instance gs://avito-bronze-bucket-central1/PhoneRequestsStream.csv \
    --database=avito_db \
    --query="SELECT * FROM PhoneRequestsStream"

gcloud sql export csv avito-db-instance gs://avito-bronze-bucket-central1/SearchInfo.csv \
    --database=avito_db \
    --query="SELECT * FROM SearchInfo"

gcloud sql export csv avito-db-instance gs://avito-bronze-bucket-central1/SearchStream.csv \
    --database=avito_db \
    --query="SELECT * FROM SearchStream"

gcloud sql export csv avito-db-instance gs://avito-bronze-bucket-central1/UserInfo.csv \
    --database=avito_db \
    --query="SELECT * FROM UserInfo"

gcloud sql export csv avito-db-instance gs://avito-bronze-bucket-central1/VisitPhoneRequestStream.csv \
    --database=avito_db \
    --query="SELECT * FROM VisitPhoneRequestStream"

gcloud sql export csv avito-db-instance gs://avito-bronze-bucket-central1/VisitsStream.csv \
    --database=avito_db \
    --query="SELECT * FROM VisitsStream"
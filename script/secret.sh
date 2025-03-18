gcloud secrets create cloud-sql-creds --replication-policy="automatic"
echo '{
  "database": "avito_db",
  "instance": "ordinal-reason-449406-f0:us-central1:avito-db-instance",
  "user": "thiru",
  "password": "thiru"
}' | gcloud secrets versions add cloud-sql-creds --data-file=-

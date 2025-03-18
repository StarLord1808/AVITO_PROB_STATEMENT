CREATE OR REPLACE EXTERNAL TABLE `avito_data.AdsInfo_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://avito-bronze-bucket-central1/AdsInfo/part-00000-97bb04bf-81a4-4bcc-aeca-9b55559c529c-c000.snappy.parquet']
);

CREATE OR REPLACE EXTERNAL TABLE `avito_data.location_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://avito-bronze-bucket-central1/Location/part-00000-4cf20f25-90da-4409-b19f-ba48bad6c98f-c000.snappy.parquet']
);


CREATE OR REPLACE EXTERNAL TABLE `avito_data.searchstream_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://avito-bronze-bucket-central1/SearchStream/part-00000-c9b1cf6a-b8cc-4fa5-9353-dd0bfc37f07e-c000.snappy.parquet']
);

CREATE OR REPLACE EXTERNAL TABLE `avito_data.visitsstream_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://avito-bronze-bucket-central1/VisitsStream/part-00000-ac3f5a9c-9abd-4903-9299-60343b8f7a53-c000.snappy.parquet']
);

CREATE OR REPLACE EXTERNAL TABLE `avito_data.phonerequestsstream_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://avito-bronze-bucket-central1/PhoneRequestsStream/part-00000-dfcdf1b0-40b2-42df-bc59-59274b40c569-c000.snappy.parquet']
);

CREATE OR REPLACE EXTERNAL TABLE `avito_data.userinfo_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://avito-bronze-bucket-central1/UserInfo/part-00000-8526b62f-d690-40b7-ae68-2cd7b15cf3ea-c000.snappy.parquet']
);
/*Load data from External table to Native BigQuery Table*/

--UserInfo
CREATE OR REPLACE TABLE `ordinal-reason-449406-f0.avito_silver.userinfo`
AS
SELECT * FROM `ordinal-reason-449406-f0.avito_data.userinfo_external`;

--Location
CREATE OR REPLACE TABLE `ordinal-reason-449406-f0.avito_silver.location`
AS
SELECT * FROM `ordinal-reason-449406-f0.avito_data.location_external`;

--AdsInfo
CREATE OR REPLACE TABLE `ordinal-reason-449406-f0.avito_silver.adsinfo`
AS
SELECT * FROM `ordinal-reason-449406-f0.avito_data.AdsInfo_external`;

--SearchStream
CREATE OR REPLACE TABLE `ordinal-reason-449406-f0.avito_silver.searchstream`
AS
SELECT * FROM `ordinal-reason-449406-f0.avito_data.searchstream_external`;

--VisitsStream
CREATE OR REPLACE TABLE `ordinal-reason-449406-f0.avito_silver.visitsstream`
AS
SELECT * FROM `ordinal-reason-449406-f0.avito_data.visitsstream_external`;

--PhoneRequestsStream
CREATE OR REPLACE TABLE `ordinal-reason-449406-f0.avito_silver.phonerequestsstream`
AS
SELECT * FROM `ordinal-reason-449406-f0.avito_data.phonerequestsstream_external`;


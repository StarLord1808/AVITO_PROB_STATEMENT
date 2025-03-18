--  This script is used to get the DDL of the tables in the dataset
SELECT ddl ,table_name
FROM `ordinal-reason-449406-f0`.`avito_silver`.INFORMATION_SCHEMA.TABLES 
WHERE table_name in('searchstream','visitsstream','phonerequestsstream');
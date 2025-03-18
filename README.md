# **Avito Dataset - Data Engineering Pipeline**  

## **📌 Problem Statement**  
The goal of this project is to build a **scalable and efficient data engineering pipeline** for the **Avito Context Ad Clicks dataset**. The pipeline processes raw event logs from Avito's advertising platform and transforms them into meaningful insights for **click-through rate (CTR) analysis, user behavior tracking, and ad performance evaluation**.  

---

## **📂 Data Pipeline Architecture**  
The pipeline follows a **Bronze → Silver → Gold** architecture using **Google Cloud Platform (GCP)** services.  

### **1️⃣ Data Ingestion & Landing Layer**  
- Extract the **Avito Context Ad Clicks dataset** from Kaggle.  
- Upload the dataset to a **Google Compute Engine (VM)**.  
- Transfer raw data from the **VM to GCS (Landing Layer)** using the `gsutil` command.  
- Store the raw dataset in **Google Cloud Storage (Landing Layer)** for further processing.  

### **2️⃣ Bronze Layer (Raw Data Storage & Cloud SQL Loading)**  
- Load data from the **Landing Layer → Cloud SQL (MySQL)** while maintaining schema integrity:
  - Keep **7 original tables** (`AdsInfo`, `Category`, `Location`, `PhoneRequestsStream`, `SearchInfo`, `SearchStream`, `UserInfo`, `VisitsStream`).
  - Add an **insertion timestamp** column.  
  - Merge `VisitsStream` and `PhoneRequestsStream` into `VisitPhoneRequestStream` using **Cloud Run**.  
- Store a copy of raw data in the **GCS Bronze Bucket** for backup and future processing.  

### **3️⃣ Silver Layer (Data Cleaning & Normalization)**  
- Extract data from **Cloud SQL → GCS (Silver Layer)** using **Cloud Composer (Airflow DAGs)**.  
- Perform **data cleansing, deduplication, and normalization** using **PySpark on Dataproc**.  
- Normalize user interactions by merging `SearchStream`, `VisitsStream`, and `PhoneRequestsStream`.  
- Enrich `UserInfo` with **synthetic IP & Device details** using Faker.  
- Enhance `Location` table with **geolocation enrichment**.  
- Store cleaned and transformed data in the **Silver Layer (BigQuery & GCS Silver Bucket)**.  

### **4️⃣ Gold Layer (Aggregated & Analytical Data)**  
- Perform advanced feature engineering in **BigQuery**.  
- Join `SearchStream` with `AdsInfo` to enrich ad metadata.  
- Compute **Click-Through Rate (CTR)** and **ad performance metrics**.  
- Store aggregated insights in the **Gold Layer (BigQuery & GCS Gold Bucket)** for analytics.  

---

## **⚙️ Tech Stack & Tools**  
| **Component**      | **Technology Used** |
|--------------------|--------------------|
| **Compute**       | Google Compute Engine (VM) |
| **Storage**       | Google Cloud Storage (GCS) |
| **Database**      | Cloud SQL (MySQL) |
| **Processing**    | Dataproc (PySpark), BigQuery |
| **Orchestration** | Cloud Composer (Airflow) |
| **Automation**    | Terraform (Infrastructure as Code) |
| **CI/CD**         | Bitbucket CI Pipelines |
| **Visualization** | Tableau |

---

## **🔗 Data Flow Overview**  
1. **Extract data from Kaggle** → Load onto **GCE VM**.  
2. **Move data from VM → GCS Landing Layer** (`gsutil`).  
3. **Load raw data from GCS Landing → Cloud SQL (Bronze Layer)**.  
4. **Extract data from Cloud SQL → GCS Silver Layer** (Airflow).  
5. **Transform data using PySpark on Dataproc**.  
6. **Load transformed data into BigQuery & GCS Silver Bucket**.  
7. **Aggregate and compute insights in BigQuery (Gold Layer)**.  
8. **Build Tableau/Looker Studio dashboards for analysis**.  

---

## **📊 Dashboards & Insights**
- **CTR Analysis**: Measure how frequently users click on ads.  
- **Ad Performance**: Track ad interactions across categories.  
- **User Behavior**: Understand user engagement based on search and visit patterns.  
- **Dashboard Link:** https://public.tableau.com/views/Ad_Performance_by_Region/Dashboard1?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link 

---

## **🚀 Deployment & CI/CD**
- Terraform automates **GCP infrastructure** setup.  
- **Bitbucket CI/CD pipelines** deploy Airflow DAGs, Cloud Functions & PySpark scripts.  
- Automated testing ensures **pipeline reliability and scalability**.  

---
## **📌 Sample Dataset and Gold Layer Data**
**Sample Avito Data:** https://drive.google.com/drive/folders/1r0us7UAylEpU1BFZRo9w4GoohBw5HmI2?usp=drive_link
**Gold Layer Data:** https://drive.google.com/drive/folders/1EeM8MVC1Xa_3cJLduIwK8xF-r_qulM9i?usp=drive_link

---

## **📊 Dataflow Diagram**
Below is the high-level architecture showing data flow across the pipeline:  

```plaintext
+---------------------+    gsutil     +--------------------------+
|  Kaggle Dataset     | ------------> |  GCS Landing             |
+---------------------+               +--------------------------+
                                             | 
                                             | gsutil
                                             |
                                             v
                                      +--------------------------+
                                      |  GCS Landing             |
                                      +--------------------------+
                                             |
                                             | Pyspark script script triggered through Data Proc
                                             |
                                             v
                                      +--------------------------+       Cloud Composer            +-------------------+
                                      |  Cloud SQL(Bronze Layer) |     ------------------->        | GCS Bronze Bucket |
                                      +--------------------------+                                 +-------------------+
                                             |
                                             | Pyspark script script triggered through Data Proc
                                             |
                                             v
                                      +--------------------------+       Cloud Composer            +-------------------+
                                      |  BigQuery (Silver Layer) |     ------------------->        | GCS Silver Bucket |
                                      +--------------------------+                                 +-------------------+
                                             |
                                             | Pyspark script script triggered through Data Proc
                                             |
                                             v
                                      +--------------------------+       Cloud Composer            +-------------------+
                                      |  BigQuery (Gold   Layer) |     ------------------->        | GCS Gold Bucket   |
                                      +--------------------------+                                 +-------------------+
                                             |
                                             |
                                             |
                                             v
                                     +----------------------+
                                     |     Tableau          |
                                     +----------------------+


## **📌 Next Steps**
✅ Finalize **Gold Layer transformations**.  
✅ Improve **query performance in BigQuery**.  
✅ Enhance **Tableau dashboards for ad insights**.  
✅ Optimize **pipeline for real-time data processing**.  

🚀 **Stay tuned for updates!** 🚀  

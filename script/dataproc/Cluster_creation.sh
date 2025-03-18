Issue:
The PySpark script make use of packages that weren't installed during the creation of Cluster. Resulting in below error.
    "ModuleNotFoundError: No module named 'faker'"

Fix:
-> Drop the existing cluster.
-> Recreate the cluster as below.
    1. Create a cluster_init.sh script with required packages that are used in PySPark script.

        #!/bin/bash

        # Update package lists
        apt-get update

        # Install pip
        apt-get install -y python3-pip

        # Install required Python packages
        pip3 install --upgrade pip
        pip3 install faker

        # Restart services if needed
        echo "Initialization script execution completed."

    2. Upload it to GCS bucket using below command
        gsutil cp cluster_init.sh gs://avito-silver-bucket-central1/scripts

    3. Delete the existing cluster with below command
        gcloud dataproc clusters delete avito-dataproc --region=us-central1

    4. Create a new cluster with below command
        gcloud dataproc clusters create avito-dataproc \
            --region=us-central1 \
            --master-machine-type=n1-standard-2 \
            --master-boot-disk-size=100 \
            --num-workers=2 \
            --worker-machine-type=n1-standard-2 \
            --worker-boot-disk-size=100 \
            --image-version=2.0-debian10 \
            --enable-component-gateway \
            --bucket=avito-silver-bucket-central1 \
            --initialization-actions=gs://avito-silver-bucket-central1/scripts/cluster_init.sh

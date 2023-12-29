Project Description

This project comprises of the following Kubernetes objects:

Deployments:

-) api-region: Manages the deployment of api-region (a Flask-based app handling specific functionalities) 
-) api-genre: Manages the deployment of api-genre (a Flask-based app handling specific functionalities) 
-) game-store-db: Manages the deployment of the game-store-db database.

Services: 
-) api-genre (Exposed externally through an Ingress controller). 
-) api-region (Exposed externally through an Ingress controller). 
-) game-store-db.

Additional Components:
Secret for Database Initialization: 
-) Contains sensitive data required for initializing the MySQL database securely. ConfigMap for API-Database Communication: 
-) Configures the API services to communicate with the MySQL database.

Project Flow: Ingress Configuration: -)The Ingress controller allows external access to both Flask API services. API Interaction: -)External clients can interact with the APIs to query the MySQL database. Configuration Components: -)Utilizes Kustomize for Kubernetes manifest management.

Usage: Deploy the Project: -) Apply the Kubernetes manifests using Kustomize to deploy the API services, MySQL database, secret, and configmap. Run the command: Accessing APIs: -)Use the Ingress endpoint to access the API services externally. APIs communicate securely with the MySQL database.
# Example: Deploying two Flask Api with a MYSQL Database in Kubernetes

This tutorial shows you how deploy a simple ingress to route certain paths of the host to a different backend. This example consists of the following kubernetes components:
* api-genre-deploy
* api-genre-svc
* api-region-deploy
* api-region-svc
* game-store-db-svc
* game-store-db
* ingress-genre-region
* kustomization
* namespace


# Objectives

* How to initialize the MySQL database with specific state provided by a ConfigMap and a Secret resources 

* api-genre-svc
* api-region-deploy
* api-region-svc
* game-store-db-svc
* game-store-db
* ingress-genre-region
* kustomization
* namespace

# How to initialize the MySQL database with specific state provided by a ConfigMap and a Secret resources 
To ensure secure storage of sensitive MySQL database credentials, we'll create a secret named mysql-cred using a script named `database-cred.sh`:

```
MYSQL_ROOT_PASSWORD=<yourpassword>
MYSQL_DATABASE=<yourdatabase>
MYSQL_HOST=<yourhostname>
MYSQL_USER=<youruser>
```

Execute the following command to generate the secret:
```
kubectl create secret generic mysql-cred \
--from-env-file=.database-cred -n my-games   
```

Next, let's create a ConfigMap named `mysql-dump-config` using a MySQL dump file named videogames-db.sql:

```
kubectl create configmap mysql-dump-config \
--from-file=videogames-db.sql -n my-games
```

 api-region: Manages the deployment of api-region (a Flask-based app handling specific functionalities);

-) api-genre: Manages the deployment of api-genre (a Flask-based app handling specific functionalities);

-) game-store-db: Manages the deployment of the game-store-db database.
A single-instance Redis to store guestbook entries
Multiple web frontend instances

This project comprises of the following Kubernetes objects:

## Deployments:

-) api-region: Manages the deployment of api-region (a Flask-based app handling specific functionalities);

-) api-genre: Manages the deployment of api-genre (a Flask-based app handling specific functionalities);

-) game-store-db: Manages the deployment of the game-store-db database.

## Services: 

-) api-genre (Exposed externally through an Ingress controller);

-) api-region (Exposed externally through an Ingress controller); 

-) game-store-db;

## Additional Components:

-) Secret for Database Initialization (contains sensitive data required for initializing the MySQL database securely);

-) ConfigMap for API-Database Communication (configures the API services to communicate with the MySQL database);

## Project Flow: 

-) Ingress Configuration (allows external access to both Flask API services. API Interaction); 

-)External clients can interact with the APIs to query the MySQL database.

-) Configuration Components (utilizes Kustomize for Kubernetes manifest management);

## Usage: Deploy the Project
 
 -) Apply the Kubernetes manifests using Kustomize. Run the command: Accessing APIs: 
 
 ```
kubectl apply -k base
```

 -)Use the Ingress endpoint to access the API services externally. APIs communicate securely with the MySQL database

 To delete all the objects deployed, run the command:
 ```
 kubectl delete -k base
 ```
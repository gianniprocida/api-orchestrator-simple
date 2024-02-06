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

The manifest file, included below, specifies a Deployment controller that runs a single replica MySQL Pod.

```
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    app: game-store-db
  name: game-store-db
  namespace: my-games
spec:
  replicas: 1
  selector:
    matchLabels:
      app: game-store-db
  strategy: {}
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: game-store-db
    spec:
      volumes:
       - name: my-sql-dump
         configMap: 
           name: mysql-dump-config
      containers:
      - image: mysql
        name: mysql
        env: 
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-cred
              key: MYSQL_ROOT_PASSWORD
        - name: MYSQL_DATABASE
          valueFrom:
            secretKeyRef:
              name: mysql-cred
              key: MYSQL_DATABASE
        ports:
        - containerPort: 3306
        volumeMounts: 
          - name: my-sql-dump
            mountPath: /docker-entrypoint-initdb.d  
        resources: {}
status: {}
```
Apply the Deployment from the `game-store-db.yaml` file:
```
kubectl apply -f game-store-db.yaml
```

Essentially this yaml file sets up a volume named my-sql-dump that is populated with data from the ConfigMap named `mysql-dump-config`. This volume is later mounted into the MySQL container at the path `/docker-entrypoint-initdb.d`, allowing the container to access the data stored in the ConfigMap. Our sensitive information are securely injected into the container using the `env` section.

The api needs to communicate to the MySQL to query its data. You need to apply a Service to proxy the traffic to the MySQL pod. A Service defines a policy to access the Pods:

```
apiVersion: v1
kind: Service
metadata:
  creationTimestamp: null
  labels:
    app: game-store-db
  name: game-store-db
  namespace: my-games
spec:
  ports:
  - port: 3306
    protocol: TCP
    targetPort: 3306
  selector:
    app: game-store-db
status:
  loadBalancer: {}
```

```
Apply the Service from the `game-store-db-service.yaml` file:
```
kubectl apply -f game-store-db-serviceyaml
```


## Create the Flask Python Api

Go the folder `source-api-region` and then run the folling command:

```
docker build -f Dockerfile -t <yourDockerHub>/api-genre:v1.0
docker push <yourDockerHub>/api-genre:v1.0
```

These commands build and push a Docker image tagged as <yourDockerHub>/api-genre:v1.0 to a Docker registry for deployment. 

```
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    app: api-genre
  name: api-genre
  namespace: my-games
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api-genre
  strategy: {}
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: api-genre
    spec:
      containers:
      - image: gprocida/api-genre:v1.0
        name: api-genre
        imagePullPolicy: Never
        ports:
        - containerPort: 5000
        envFrom:
        - secretRef: 
            name: mysql-cred
        resources: {}
status: {}
```

Apply the Deployment from the `api-genre-deploy.yaml` file:
```
kubectl apply -f api-genre-deploy.yaml
```


Now we will user this configuaration for
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
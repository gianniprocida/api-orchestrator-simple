# Deploying Flask APIs, Simple Frontend, and MySQL Database in a Kubernetes Cluster

Requirements:

* Docker Desktop
* nginx controller installed

This tutorial shows you how deploy a simple ingress to route certain paths of the host to a different backend. 


# Objectives

* How to initialize the MySQL database with specific state provided by a ConfigMap and a Secret resources 
* Start up the api-region and api-pod deployment
* Start up the simple frontend pod deployment
* Expose the two api's and the frontend pod
* Apply the Ingress resource to expose the two APIs and the frontend service
* Test your endpoints



## How to initialize the MySQL database with specific state provided by a ConfigMap and a Secret resources 
To ensure secure storage of sensitive MySQL database credentials, we'll create a secret named `mysql-cred` using a script named `database-cred.sh`:

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

Apply the Service from the `game-store-db-service.yaml` file:
```
kubectl apply -f game-store-db-serviceyaml
```


## Create the API-Genre and the API-Region

Navigate to the `souce-api-genre` and run the two commands:

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
Our sensitive information are securely injected into the container using the `envFrom` section so that our api will know how to connect to the MySQL Service.


Apply the Deployment from the `api-genre-deploy.yaml` file:
```
kubectl apply -f api-genre-deploy.yaml
```



We will create a Service to proxy the traffic to the api-genre pod:

```
apiVersion: v1
kind: Service
metadata:
  creationTimestamp: null
  labels:
    app: api-genre
  name: api-genre
  namespace: my-games
spec:
  ports:
  - port: 8080
    protocol: TCP
    targetPort: 5000
  selector:
    app: api-genre
status:
  loadBalancer: {}
```


Apply the Service from the `api-genre-service.yaml` file:
```
kubectl apply -f api-genre-service.yaml
```


Next, let's configure the second API. Go to the `source-api-region` directory and execute the following two commands:


```
docker build -f Dockerfile -t <yourDockerHub>/api-region:v1.0
docker push <yourDockerHub>/api-region:v1.0
```

These commands build and push a Docker image tagged as <yourDockerHub>/api-region:v1.0 to your Docker registry for deployment. 


```
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    app: api-region
  name: api-region
  namespace: my-games
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api-region
  strategy: {}
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: api-region
    spec:
      containers:
      - image: gprocida/api-region:v1.0
        name: api-region
        imagePullPolicy: Never
        envFrom:
        - secretRef: 
            name: mysql-cred
        ports:
        - containerPort: 5000
        resources: {}
status: {}
```



Apply the Deployment from the `api-region-deploy.yaml` file:
```
kubectl apply -f api-region-deploy.yaml
```


We will create another Service to proxy the traffic to the api-region pod:

```
apiVersion: v1
kind: Service
metadata:
  creationTimestamp: null
  labels:
    app: api-region
  name: api-region
  namespace: my-games
spec:
  ports:
  - port: 9090
    protocol: TCP
    targetPort: 5000
  selector:
    app: api-region
status:
  loadBalancer: {}
```



Query the list of Services to verify that the Redis Service is running:

```
kubectl get service -n my-games
```




## Create the frontend menu



Next, we'll create a ConfigMap named `index-html`, utilizing the index.html file, to establish the volume configuration for future mounting into the pod:

```
kubectl create configmap index-html \
--from-file=index.html -n my-games

```


Apply the Deployment from the `simple-frontend-deploy.yaml` file:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    app: simple-frontend
  name: simple-frontend
  namespace: my-games
spec:
  replicas: 1
  selector:
    matchLabels:
      app: simple-frontend
  strategy: {}
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: simple-frontend
    spec:
      volumes:
       - name: index-html
         configMap:
          name: index-html
      containers:
      - image: gprocida/simple-frontend
        name: simple-frontend
        imagePullPolicy: Never
        ports:
        - containerPort: 80
        volumeMounts:
         - name: index-html
           mountPath: /usr/share/nginx/html
        resources: {}
status: {}
```


A volume named `index-html` sourced from a ConfigMap named "index-html" is mounted at /usr/share/nginx/html within the container. By providing access to this volumes, changes can be made to the default Nginx page served by the container.


We will create another Service to proxy the traffic to the frontend pod:

```
apiVersion: v1
kind: Service
metadata:
  creationTimestamp: null
  labels:
    app: simple-frontend
  name: simple-frontend
  namespace: my-games
spec:
  ports:
  - port: 8080
    protocol: TCP
    targetPort: 80
  selector:
    app: simple-frontend
status:
  loadBalancer: {}
```



We can query the list of Services to verify their operation status:

```
kubectl get service -n my-games
```



## Deploy Ingress Controller

Before exposing your services externally using an Ingress, ensure that your Kubernetes cluster has an Ingress controller installed and configured. Services can be accessed externally from localhost once the Ingress controller is set up.


```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  generation: 1
  name: ingress-genre-region
  namespace: my-games
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - backend:
          service:
            name: api-genre
            port:
              number: 5000
        path: /filter/genre
        pathType: Prefix
      - backend:
          service:
            name: api-region
            port:
              number: 9090
        path: /filter/region
        pathType: Prefix
      - backend:
          service:
            name: simple-frontend
            port:
              number: 8080
        path: /
        pathType: Prefix
```


## Test your endpoints


curl -v localhost/filter/region
curl -v localhost/filter/genre
curl -v localhost/





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
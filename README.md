# K8S-Drupal-Journey
Self-study Kubernetes by Creating a Drupal real-world app following geerlingguy playlist on youtube

Kubernetes Implementation Journey

This project documents my personal journey to implement a real-world application on Kubernetes.
It starts from a simple Python Flask app, and grows into a full Drupal (LAMP stack) deployment with persistent storage, Helm charts, scaling, and troubleshooting.

All steps were done manually to understand the mechanics before any automation.

Flask App on Kubernetes
1. Create a Python Script using Flask to return GET requests

Make sure firewall allows port 5000 and http/https:

# firewall-cmd --add-port=5000/tcp
# firewall-cmd --add-service=http


After testing the app, build a container image.

Base image: python:3.11-alpine

Dockerfile:

Pulls the base image

Creates directory /app

Copies app and requirements

Installs Flask via pip

Exposes port 5000

Runs the app

Build and save image:

# podman build -t flask-app:v1.0.0 .
# podman save -o flask-app.tar flask-app:v1.0.0


Load into minikube:

# minikube image load flask-app.tar


Create deployment:

# kubectl create deploy myapp --image localhost/flask-app --dry-run=client -o yaml > myapp.yaml


Modify YAML to expose port 5000.

Expose service:

# kubectl expose deployment myapp --type NodePort --port 5000


Check service:

# kubectl get svc
# curl <minikube IP>:<svc port>/Hello


Observe requests routing:

# kubectl logs -f -l app=myapp --prefix=true

Updating and Rollback
# kubectl set image deploy myapp flask-app=localhost/flask-app:v1.0.1
# kubectl rollout history deploy myapp
# kubectl rollout undo deploy myapp

Deploying a Real Application – Drupal

Drupal is built on the LAMP stack:

Linux

Apache

MySQL / MariaDB

PHP

The goal was to understand how to deploy it natively and then through Helm on Kubernetes.

Bare Metal Setup (for comparison)

Install and configure MariaDB, Apache, PHP manually.
Create Drupal site under /var/www/html/drupal.

This was just to understand dependencies and file layout before containerizing.

Using Helm to Deploy Drupal on Kubernetes

Helm is the package manager for Kubernetes.

# helm repo add bitnami https://charts.bitnami.com/bitnami
# helm install mysite bitnami/drupal


This automatically deploys:

Drupal + Apache + PHP

MariaDB

Services and PVCs

To access the site:

# kubectl get svc
# minikube tunnel


Check secrets for database:

# kubectl get secrets mysite-mariadb


Helm charts use template YAML files under the hood that deploy all of this into a namespace (drupal).

Custom Deployment Details

PVCs for persistent data (ReadWriteOnce)

ConfigMap for PHP settings mounted inside container

InitContainer for file permissions on multi-node clusters

Liveness/Readiness probes for health checking

Services (NodePort for external access)

Scaling up replicas:

# kubectl edit deployment -n drupal drupal
replicas: 3


At this point, the new pods failed due to multi-attach error on the PVC, which can only be mounted on one node at a time (RWO).
Solution: use node affinity or switch to a shared storage backend.

Storage Layer: NFS Provisioner

A separate VM was used as NFS server.

Helm chart:

# helm repo add groundhog2k https://groundhog2k.github.io/helm-charts
# helm install --set nfs.server=192.168.24.227 --set nfs.path=/home/ldap groundhog2k/nfs-client-provisioner --generate-name


Update PVCs:

accessModes:
  - ReadWriteMany
storageClassName: nfs-client


Apply manifests again.
Drupal and MariaDB both now write to NFS.

Access and Testing
# kubectl port-forward -n drupal svc/drupal 8080:80 --address=0.0.0.0


Access from browser: http://<vm-ip>:8080

Created content and verified that uploaded files were stored on NFS server.

Load testing:

# ab -n 500 -c 10 http://192.168.49.2:31267/


Measured around 17 requests per second.

Scaling replicas to 3 didn’t increase performance significantly since PHP/DB were bottlenecks.

Horizontal Pod Autoscaling

Enable metrics server:

# minikube addons enable metrics-server
# kubectl top nodes


Create autoscaler:

# kubectl autoscale -n drupal deploy drupal --min=1 --max=8 --cpu-percent=50


Run heavy load test using cookies to simulate user sessions:

# ab -n 1000 -c 3 -C "SESSION=..." http://192.168.24.226:8080/admin/modules


Observed CPU reaching 600m, triggering scale-up.
Pods scaled automatically from 1 to 8 and back down after load decreased.

Lessons Learned

Stateless apps scale easily; stateful apps (like Drupal) need careful storage planning.

NFS works for shared media but not for databases.

Rook/Ceph are powerful but complex to maintain.

Helm simplifies deployment, but understanding YAML and underlying architecture is mandatory.

Kubernetes scaling and storage behavior depend heavily on storageClass and accessMode.

Next Steps

Add screenshots and YAML manifests.

Automate NFS and Helm setup via Ansible.

Deploy ingress controller for domain access instead of NodePort.

Repository Structure
/flask-app/
    app.py
    Dockerfile
    requirements.txt
/k8s/
    myapp.yaml
    drupal/
        drupal-deploy.yaml
        mariadb-deploy.yaml
        pvc.yaml
        configmap.yaml
/notes/
    implementation-steps.md

# Credits

All steps written and executed manually as part of personal learning and proof-of-concept for real-world K8s application deployment.

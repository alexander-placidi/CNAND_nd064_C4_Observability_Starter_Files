## Cloud Native Architecture Nanodegree (CNAND): Observability

This is the public repository for the Observability course of Udacity's Cloud Native Architecture Nanodegree (CNAND) program (ND064).

The  **Exercise_Starter_Files** directory has all of the files you'll need for the exercises found throughout the course.

The **Project_Starter_Files** directory has the files you'll need for the project at the end of the course.

## Playbook ##

### Spin up VM

vagrant up

### Verify K3s ###

kubectl version
systemctl status k3s
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

### Install Helm ###

curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

### Setup monitoring ###

kubectl create namespace monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add stable https://charts.helm.sh/stable
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring
kubectl get pods,svc --namespace=monitoring
kubectl --namespace monitoring get pods -l "release=prometheus"

### Install cert manager ###

kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.16.1/cert-manager.yaml

### Install Ingress controller ###

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
kubectl get pods -n ingress-nginx

### Setup Tracing ###

kubectl create namespace observability
export jaeger_version=v1.65.0
kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/download/${jaeger_version}/jaeger-operator.yaml -n observability
kubectl get deployment jaeger-operator -n observability
kubectl get pods -n observability
touch jaeger-ingress.yaml
nano jaeger-ingress.yaml 

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: jaeger-ingress
  namespace: observability
spec:
  ingressClassName: nginx
  rules:
  - host: jaeger.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: jaeger-query
            port:
              number: 16686

kubectl apply -n observability -f jaeger-ingress.yaml
kubectl get nodes -o wide
echo "10.0.2.15 jaeger.local" | sudo tee -a /etc/hosts
kubectl get svc -n ingress-nginx
kubectl patch svc ingress-nginx-controller -n ingress-nginx -p '{"spec": {"type": "NodePort"}}'

touch jaeger.yaml
nano jaeger.yaml

apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: jaeger
  namespace: observability
spec:
  strategy: allInOne
  ingress:
    enabled: true
  storage:
    type: memory

kubectl apply -f jaeger.yaml -n observability
kubectl get svc -n observability
curl -v http://jaeger.local

### Port-Forwarding services ###

#### Monitoring/Grafana ####
kubectl port-forward service/prometheus-grafana --address 0.0.0.0 3000:80 --namespace monitoring
http://localhost:3000/
un: admin, pw: prom-operator

#### Tracing/Jaeger UI ####
kubectl port-forward -n observability svc/jaeger-query 16686:16686 --address 0.0.0.0

#### Backend and frontend service ####
kubectl port-forward service/backend-service --address 0.0.0.0 8081:8081 & kubectl port-forward service/frontend-service --address 0.0.0.0 8080:8080

#### Prom UI ####
kubectl port-forward service/prometheus-kube-prometheus-prometheus --address 0.0.0.0 9090:9090 --namespace monitoring

** Temporary notes **

#### Miscellaneous ####

kubectl run mycurlpod --image=curlimages/curl -i --tty -- sh
kubectl scale --replicas=1 deployment/backend-app
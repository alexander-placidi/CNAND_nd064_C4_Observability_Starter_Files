## Cloud Native Architecture Nanodegree (CNAND): Observability

This is the public repository for the Observability course of Udacity's Cloud Native Architecture Nanodegree (CNAND) program (ND064).

The  **Exercise_Starter_Files** directory has all of the files you'll need for the exercises found throughout the course.

The **Project_Starter_Files** directory has the files you'll need for the project at the end of the course.


** Temporary notes **

kubectl port-forward service/prometheus-grafana --address 0.0.0.0 3000:80 --namespace monitoring
kubectl port-forward service/prometheus-kube-prometheus-prometheus --address 0.0.0.0 9090:9090 --namespace monitoring    # PromUI

kubectl port-forward service/frontend-service --address 0.0.0.0 8080:8080
kubectl port-forward service/backend-service --address 0.0.0.0 8081:8081

kubectl port-forward service/jaeger-inmemory-instance-collector 8086:16686

kubectl run mycurlpod --image=curlimages/curl -i --tty -- sh

kubectl scale --replicas=0 deployment/backend-app



kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.6.3/cert-manager.yaml

kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.65.0/jaeger-operator.yaml -n observability

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.0/deploy/static/provider/cloud/deploy.yaml




kubectl port-forward -n observability  service/hotrod-query --address 0.0.0.0 16686:16686

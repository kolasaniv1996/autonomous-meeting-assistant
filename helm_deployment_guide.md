# Autonomous Meeting Assistant Helm Deployment Guide

This guide provides instructions on how to deploy the Autonomous Meeting Assistant application to your Kubernetes cluster using Helm.

## 1. Prerequisites

Before you begin, ensure you have the following installed and configured:

*   **Helm**: The Kubernetes package manager.
*   **kubectl**: The Kubernetes command-line tool, configured to connect to your Kubernetes cluster.
*   **Docker**: For building container images.
*   **Container Registry Access**: You will need access to a container registry (e.g., Docker Hub) to store your Docker images. Ensure you are logged in to your chosen registry and have pushed the images as described in the main `deployment_guide.md`.

## 2. Clone the Repository

If you haven't already, clone the application repository to your local machine:

```bash
git clone https://github.com/kolasaniv1996/autonomous-meeting-assistant.git
cd autonomous-meeting-assistant
```

## 3. Build and Push Docker Images

Ensure you have built and pushed the Docker images for both the backend and frontend to your container registry. Refer to the `deployment_guide.md` in the root of this repository for detailed instructions on this step.

**Important**: The Helm chart is configured to use `vivekkolasani1996/autonomous-meeting-assistant-backend:latest` and `vivekkolasani1996/autonomous-meeting-assistant-frontend:latest` by default. If you pushed your images to a different registry or with different tags, you will need to update the `values.yaml` file in the Helm chart accordingly.

## 4. Deploy with Helm

Navigate to the root of the cloned repository where the `autonomous-meeting-assistant-chart` directory is located.

### 4.1. Install the Helm Chart

To install the Helm chart, run the following command:

```bash
helm install autonomous-meeting-assistant ./autonomous-meeting-assistant-chart \
  --set backend.image.repository=your-dockerhub-username/autonomous-meeting-assistant-backend \
  --set frontend.image.repository=your-dockerhub-username/autonomous-meeting-assistant-frontend
```

Replace `your-dockerhub-username` with your actual Docker Hub username.

### 4.2. Customize Values (Optional)

If you need to customize any values (e.g., replica counts, service types, ingress hosts), you can create a `my-values.yaml` file:

```yaml
# my-values.yaml
backend:
  replicaCount: 2
  service:
    type: LoadBalancer

frontend:
  ingress:
    enabled: true
    hosts:
      - host: myapp.example.com
        paths:
          - path: /
            pathType: Prefix
```

Then, install the chart using your custom values file:

```bash
helm install autonomous-meeting-assistant ./autonomous-meeting-assistant-chart -f my-values.yaml
```

## 5. Verify Deployment

After installing the Helm chart, verify that your pods are running and healthy, and that the services are reachable.

### 5.1. Check Helm Release Status

```bash
helm list
```

### 5.2. Check Kubernetes Resources

```bash
kubectl get all -l app.kubernetes.io/instance=autonomous-meeting-assistant
```

### 5.3. Access the Application

To access the frontend, you will need the external IP or hostname of your Ingress. If you enabled Ingress and configured a host, you can access it via that hostname. Otherwise, you might need to check your Ingress Controller or cloud provider's load balancer details.

If you are using Minikube for local testing, you can get the Ingress URL using:

```bash
minikube ingress list
```

Then, open the provided URL in your web browser to access the Autonomous Meeting Assistant dashboard.

## 6. Upgrade the Helm Release

If you make changes to the Helm chart or your custom `values.yaml` file, you can upgrade the release:

```bash
helm upgrade autonomous-meeting-assistant ./autonomous-meeting-assistant-chart -f my-values.yaml
```

## 7. Uninstall the Helm Release

To uninstall the application and remove all associated Kubernetes resources:

```bash
helm uninstall autonomous-meeting-assistant
```



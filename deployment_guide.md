# Autonomous Meeting Assistant Kubernetes Deployment Guide

This guide provides step-by-step instructions to deploy the Autonomous Meeting Assistant application to your Kubernetes cluster.

## 1. Prerequisites

Before you begin, ensure you have the following installed and configured:

*   **Git**: For cloning the application repository.
*   **Docker**: For building container images. Ensure your Docker daemon is running.
*   **kubectl**: The Kubernetes command-line tool, configured to connect to your Kubernetes cluster.
*   **Container Registry Access**: You will need access to a container registry (e.g., Docker Hub, Google Container Registry, AWS ECR) to store your Docker images. Ensure you are logged in to your chosen registry.

## 2. Clone the Repository

First, clone the application repository to your local machine:

```bash
git clone https://github.com/kolasaniv1996/autonomous-meeting-assistant.git
cd autonomous-meeting-assistant
```

## 3. Build and Push Docker Images

The application consists of two main components: a Flask backend and a React frontend. You need to build Docker images for both and push them to your container registry.

### 3.1. Build Backend Image

Navigate to the `autonomous-meeting-assistant` directory and build the backend image:

```bash
docker build -t autonomous-meeting-assistant-backend:latest ./agent_web_interface
```

### 3.2. Build Frontend Image

Build the frontend image:

```bash
docker build -t autonomous-meeting-assistant-frontend:latest ./agent-dashboard
```

### 3.3. Tag and Push Images to Your Registry

Replace `your-dockerhub-username` with your actual Docker Hub username (or the path to your private registry).

**Login to Docker Hub (if not already logged in):**

```bash
docker login
# Enter your username and password/PAT when prompted
```

**Tag and push the backend image:**

```bash
docker tag autonomous-meeting-assistant-backend:latest your-dockerhub-username/autonomous-meeting-assistant-backend:latest
docker push your-dockerhub-username/autonomous-meeting-assistant-backend:latest
```

**Tag and push the frontend image:**

```bash
docker tag autonomous-meeting-assistant-frontend:latest your-dockerhub-username/autonomous-meeting-assistant-frontend:latest
docker push your-dockerhub-username/autonomous-meeting-assistant-frontend:latest
```

## 4. Kubernetes Manifests

Kubernetes manifests (YAML files) define how your application will run in the cluster. These files are located in the `kubernetes/` directory.

### 4.1. Backend Deployment (`kubernetes/backend.yaml`)

This file defines the Deployment, Service, and PersistentVolumeClaim for the Flask backend.

*   **Deployment**: Creates a single replica of the backend application. It uses the `autonomous-meeting-assistant-backend:latest` image. **Make sure to update the image name in this file to reflect your registry path (e.g., `your-dockerhub-username/autonomous-meeting-assistant-backend:latest`)**.
*   **Liveness and Readiness Probes**: Configured to check the `/api/configurations` endpoint on port `5001` to ensure the application is running and ready to receive traffic.
*   **PersistentVolumeClaim (PVC)**: `backend-pvc` is defined to provide persistent storage for the SQLite database at `/app/src/database` within the container. Ensure your Kubernetes cluster has a default StorageClass or configure one.
*   **Service**: Exposes the backend deployment internally within the cluster on port `5001`.

### 4.2. Frontend Deployment (`kubernetes/frontend.yaml`)

This file defines the Deployment, Service, and Ingress for the React frontend.

*   **Deployment**: Creates a single replica of the frontend application. It uses the `autonomous-meeting-assistant-frontend:latest` image. **Make sure to update the image name in this file to reflect your registry path (e.g., `your-dockerhub-username/autonomous-meeting-assistant-frontend:latest`)**.
*   **Liveness and Readiness Probes**: Configured to check the root path `/` on port `80`.
*   **Service**: Exposes the frontend deployment internally within the cluster on port `80`.
*   **Ingress**: Exposes the frontend service externally. It uses `nginx.ingress.kubernetes.io/rewrite-target: /` annotation for path rewriting. Ensure you have an Ingress Controller (like Nginx Ingress Controller) installed in your cluster.

**Important**: Before applying the manifests, open `kubernetes/backend.yaml` and `kubernetes/frontend.yaml` and update the `image` fields to point to the images in your container registry (e.g., `your-dockerhub-username/autonomous-meeting-assistant-backend:latest`).

## 5. Deploy to Kubernetes

Once you have updated the image names in the YAML files, apply the manifests to your Kubernetes cluster:

```bash
kubectl apply -f kubernetes/backend.yaml
kubectl apply -f kubernetes/frontend.yaml
```

## 6. Verify Deployment

After applying the manifests, verify that your pods are running and healthy, and that the services are reachable.

### 6.1. Check Pod Status

Monitor the status of your pods until they are `Running` and `READY`:

```bash
kubectl get pods
```

Expected output (after some time):

```
NAME                                   READY   STATUS    RESTARTS   AGE
backend-deployment-xxxxxxxxxx-xxxxx    1/1     Running   0          XmYs
frontend-deployment-xxxxxxxxxx-xxxxx   1/1     Running   0          XmYs
```

If pods are not running, check their logs and events for troubleshooting:

```bash
kubectl logs <pod-name>
kubectl describe pod <pod-name>
```

### 6.2. Check Service Endpoints

Verify that the services are created:

```bash
kubectl get services
```

### 6.3. Access the Application

To access the frontend, you will need the external IP or hostname of your Ingress. If you are using Minikube, you can get the Ingress URL using:

```bash
minikube service frontend-service --url
```

For other Kubernetes clusters, you might need to check your Ingress Controller's documentation or your cloud provider's load balancer details to find the external IP/hostname.

Once you have the URL, open it in your web browser to access the Autonomous Meeting Assistant dashboard.

### 6.4. Test Core Features

Interact with the application through the web interface. For example, try to create a new configuration or agent to ensure the backend API is working as expected.

## 7. Environment Variables and Configuration

For production deployments, you should manage sensitive information like API keys and database credentials securely. Consider using Kubernetes Secrets for sensitive data and ConfigMaps for non-sensitive configuration.

Currently, the backend uses an SQLite database, which is suitable for development and testing but not recommended for production. For production, consider migrating to a robust database like PostgreSQL or MySQL and updating your backend configuration accordingly.

## 8. Troubleshooting

*   **ImagePullBackOff**: Ensure your Docker images are correctly tagged and pushed to a registry that your Kubernetes cluster can access. Verify the image names in your YAML files.
*   **Pending Pods**: Check `kubectl describe pod <pod-name>` for events. Common issues include insufficient resources, unbound PVCs (check your StorageClass setup), or image pull errors.
*   **Connection Refused**: Verify that your services are running and exposed correctly. Check container logs for application-level errors.

If you encounter persistent issues, gather logs and events from your pods and services, and consult the Kubernetes documentation or community forums for assistance.



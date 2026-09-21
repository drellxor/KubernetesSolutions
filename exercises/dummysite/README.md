# dummysite

A `DummySite` resource serves a copy of any web page.

```yaml
apiVersion: dwk.io/v1
kind: DummySite
metadata:
  name: example
spec:
  website_url: https://example.com/
```

The controller watches DummySites and, for each one, creates a Deployment and
a Service named after it. An init container fetches the page into an
`emptyDir`, and nginx serves it. Only the page itself is fetched, so a complex
site renders without its stylesheets.

Both created objects carry an `ownerReference` back to the DummySite, so
deleting the resource lets Kubernetes garbage-collect them. That is also why
there is no finalizer and no delete handling in the controller.

## Deploying

```sh
kubectl apply -f manifests/crd.yaml
kubectl apply -f manifests/rbac.yaml
kubectl apply -f manifests/deployment.yaml
kubectl apply -f manifests/dummysite-example.yaml
```

Then `kubectl port-forward svc/example 8080:80` to see the copy.

## Running locally

Against the current kubectl context, without deploying the controller:

```sh
pip install -r exercises/dummysite/requirements.txt
python3 exercises/dummysite/controller.py
```

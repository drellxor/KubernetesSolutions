# knative

The Knative getting-started examples (first service, autoscaling, traffic
splitting) on a separate k3d cluster, `knative`, so the Istio cluster stays
untouched.

## Cluster

```sh
k3d cluster create knative --port 8082:30080@agent:0 -p 8081:80@loadbalancer \
  --agents 2 --k3s-arg "--disable=traefik@server:0" \
  --image rancher/k3s:v1.34.1-k3s1 --kubeconfig-switch-context=false
```

Knative Serving v1.23.0 with Kourier and sslip.io magic DNS, from the release
YAML:

```sh
B=https://github.com/knative
kubectl --context k3d-knative apply -f $B/serving/releases/download/knative-v1.23.0/serving-crds.yaml
kubectl --context k3d-knative apply -f $B/serving/releases/download/knative-v1.23.0/serving-core.yaml
kubectl --context k3d-knative apply -f $B/net-kourier/releases/download/knative-v1.23.0/kourier.yaml
kubectl --context k3d-knative patch configmap/config-network -n knative-serving --type merge \
  -p '{"data":{"ingress-class":"kourier.ingress.networking.knative.dev"}}'
kubectl --context k3d-knative apply -f $B/serving/releases/download/knative-v1.23.0/serving-default-domain.yaml
```

The pods did not crash-loop on these versions. The first `default-domain` job
pod failed because the webhook had no endpoints yet; its retry succeeded.

## The service

```sh
kubectl --context k3d-knative apply -f exercises/knative/hello.yaml
curl -H "Host: $(kubectl --context k3d-knative get ksvc hello -o jsonpath='{.status.url}' | cut -d/ -f3)" http://localhost:8081
```

Kourier's LoadBalancer listens on port 80, which k3d maps to `localhost:8081`;
the Host header picks the service.

- **Autoscaling:** with no traffic the revision scaled to zero after 81s. The
  next request still answered, held by the activator while a pod started,
  about 8s later.
- **Traffic splitting:** changing `TARGET` created `hello-00002`, and
  `hello.yaml` splits traffic 50/50 between it and `hello-00001`. 200 requests
  came back 103 `Hello Knative!` and 97 `Hello World!`.

## On the Istio cluster

Ping-pong is a Knative service on the main k3d cluster too, next to Istio. Same
Serving release, but Kourier's external Service is made ClusterIP, since
hello-gateway already holds port 80 on the nodes, and there is no magic DNS:
ping-pong is cluster-local.

```sh
B=https://github.com/knative
kubectl apply -f $B/serving/releases/download/knative-v1.23.0/serving-crds.yaml
kubectl apply -f $B/serving/releases/download/knative-v1.23.0/serving-core.yaml
curl -sL $B/net-kourier/releases/download/knative-v1.23.0/kourier.yaml \
  | sed 's/type: LoadBalancer/type: ClusterIP/' | kubectl apply -f -
kubectl patch configmap/config-network -n knative-serving --type merge \
  -p '{"data":{"ingress-class":"kourier.ingress.networking.knative.dev"}}'
```

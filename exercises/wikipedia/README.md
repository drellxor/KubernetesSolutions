# wikipedia

Serves a Wikipedia page from nginx. No image of its own: the pod is three
stock containers sharing one `emptyDir`.

- `fetch-kubernetes` (init container) saves
  https://en.wikipedia.org/wiki/Kubernetes before nginx starts.
- `nginx` serves whatever is in the directory.
- `fetch-random` (sidecar) waits a random 5 to 15 minutes, saves a page from
  https://en.wikipedia.org/wiki/Special:Random in its place, and repeats. Its
  log names each page and the next wait.

Pages are written to a temp file and renamed into place, so nginx never serves
a half-written one. A `<base>` tag is added to each saved page so its styles
and images load from Wikipedia rather than 404ing here.

Reached through the exercises gateway at `/wikipedia`:

```sh
kubectl -n exercises port-forward svc/log-output-gateway-istio 8080:80
```

then open http://localhost:8080/wikipedia.

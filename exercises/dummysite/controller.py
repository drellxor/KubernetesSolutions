"""Watches DummySite resources and serves a copy of each website."""

import logging
import os

from kubernetes import client, config, watch

GROUP = "dwk.io"
VERSION = "v1"
PLURAL = "dummysites"
IMAGE = os.getenv("SITE_IMAGE", "nginx:1.27-alpine")
FETCH_IMAGE = os.getenv("FETCH_IMAGE", "busybox:1.36")

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(message)s")
logger = logging.getLogger("dummysite")


def owner(site: dict) -> dict:
    """Tie created objects to the DummySite so deleting it cleans them up."""
    return {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "DummySite",
        "name": site["metadata"]["name"],
        "uid": site["metadata"]["uid"],
        "controller": True,
    }


def deployment(site: dict) -> dict:
    name = site["metadata"]["name"]
    url = site["spec"]["website_url"]
    labels = {"app": name, "dummysite": name}

    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": name, "ownerReferences": [owner(site)]},
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": labels},
            "template": {
                "metadata": {"labels": labels},
                "spec": {
                    "volumes": [{"name": "site", "emptyDir": {}}],
                    "initContainers": [
                        {
                            "name": "fetch",
                            "image": FETCH_IMAGE,
                            # One page only; assets stay remote, so a complex
                            # site renders without its stylesheets.
                            "command": ["wget", "-O", "/site/index.html", url],
                            "volumeMounts": [
                                {"name": "site", "mountPath": "/site"}
                            ],
                        }
                    ],
                    "containers": [
                        {
                            "name": "nginx",
                            "image": IMAGE,
                            "ports": [{"containerPort": 80}],
                            "volumeMounts": [
                                {
                                    "name": "site",
                                    "mountPath": "/usr/share/nginx/html",
                                }
                            ],
                        }
                    ],
                },
            },
        },
    }


def service(site: dict) -> dict:
    name = site["metadata"]["name"]
    return {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": name, "ownerReferences": [owner(site)]},
        "spec": {
            "selector": {"app": name},
            "ports": [{"port": 80, "targetPort": 80}],
        },
    }


def apply(create, replace, namespace: str, body: dict) -> None:
    """Create the object, or overwrite it if this is a resync or an update."""
    name = body["metadata"]["name"]
    try:
        create(namespace, body)
        logger.info("Created %s/%s", body["kind"].lower(), name)
    except client.ApiException as error:
        if error.status != 409:
            raise
        replace(name, namespace, body)
        logger.info("Updated %s/%s", body["kind"].lower(), name)


def main() -> None:
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    apps = client.AppsV1Api()
    core = client.CoreV1Api()
    crds = client.CustomObjectsApi()

    logger.info("Watching %s.%s", PLURAL, GROUP)
    for event in watch.Watch().stream(
        crds.list_cluster_custom_object, GROUP, VERSION, PLURAL
    ):
        site = event["object"]
        if event["type"] == "DELETED":
            # ownerReferences let Kubernetes remove the children for us.
            continue

        namespace = site["metadata"]["namespace"]
        apply(
            apps.create_namespaced_deployment,
            apps.replace_namespaced_deployment,
            namespace,
            deployment(site),
        )
        apply(
            core.create_namespaced_service,
            core.replace_namespaced_service,
            namespace,
            service(site),
        )


if __name__ == "__main__":
    main()

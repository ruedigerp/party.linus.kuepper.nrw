

podman build --no-cache --platform linux/arm64,linux/amd64  --manifest "ghcr.io/ruedigerp/esc-essen:v0.0.24"   --build-arg VERSION=v0.0.24 \
  --build-arg STAGE=prod -f ./Dockerfile

podman push ghcr.io/ruedigerp/esc-essen:v0.0.24

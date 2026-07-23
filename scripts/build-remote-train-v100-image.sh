#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

IMAGE_URI="${IMAGE_URI:-chestvision/remote-train-yolo:v100-ultralytics-8.3.158}"
BASE_IMAGE="${BASE_IMAGE:-pytorch/pytorch:2.7.0-cuda12.6-cudnn9-runtime}"
ULTRALYTICS_VERSION="${ULTRALYTICS_VERSION:-8.3.158}"
BUILD_CONTEXT="${BUILD_CONTEXT:-$ROOT_DIR/.docker/remote-train-v100}"
PUSH="${PUSH:-0}"
NO_CACHE="${NO_CACHE:-0}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker command not found. Install Docker or run this script on a build host." >&2
  exit 1
fi

mkdir -p "$BUILD_CONTEXT"

cat > "$BUILD_CONTEXT/Dockerfile" <<DOCKERFILE
FROM ${BASE_IMAGE}

ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PIP_NO_CACHE_DIR=1 \\
    MKL_THREADING_LAYER=GNU \\
    OMP_NUM_THREADS=1 \\
    TF_CPP_MIN_LOG_LEVEL=3

RUN apt-get update && \\
    apt-get install -y --no-install-recommends \\
      curl \\
      git \\
      libgl1 \\
      libglib2.0-0 \\
      libsm6 \\
      unzip \\
      zip \\
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel && \\
    python -m pip install --no-cache-dir \\
      "ultralytics==${ULTRALYTICS_VERSION}" \\
      opencv-python-headless \\
      pyyaml \\
      requests \\
      tqdm

RUN python - <<'PY'
import torch
import ultralytics

print("torch:", torch.__version__)
print("torch cuda:", torch.version.cuda)
print("ultralytics:", ultralytics.__version__)
PY

WORKDIR /workspace

CMD ["python", "-c", "import torch, ultralytics; print('remote train image ready', torch.__version__, ultralytics.__version__)"]
DOCKERFILE

build_args=()
if [[ "$NO_CACHE" == "1" ]]; then
  build_args+=(--no-cache)
fi

echo "Building $IMAGE_URI"
echo "Base image: $BASE_IMAGE"
echo "Ultralytics: $ULTRALYTICS_VERSION"
docker build "${build_args[@]}" -t "$IMAGE_URI" "$BUILD_CONTEXT"

echo "Built image: $IMAGE_URI"
echo "Run this smoke test on a V100 host before using it in PAI-DLC:"
echo "docker run --rm --gpus all $IMAGE_URI python - <<'PY'"
echo "import torch"
echo "print(torch.__version__, torch.version.cuda)"
echo "print(torch.cuda.get_device_name(0))"
echo "print(torch.cuda.get_device_capability(0))"
echo "print(torch.cuda.get_arch_list())"
echo "print(torch.ones(1, device='cuda') * 2)"
echo "PY"

if [[ "$PUSH" == "1" ]]; then
  echo "Pushing $IMAGE_URI"
  docker push "$IMAGE_URI"
fi

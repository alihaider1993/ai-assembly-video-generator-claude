# The public website (web/server.py) with the whole pipeline and Blender, for
# a CPU-only server such as a free Hugging Face Space. Build from the repo root:
#     docker build -t assembly-site .
#     docker run -p 7860:7860 -e GEMINI_API_KEY=... assembly-site
# The free deployment doesn't use this: see deploy/cloudflare/ and web/worker.py.
FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Blender's runtime libraries, Mesa for software OpenGL (no GPU) and the
# caption font render_video.py falls back to.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl xz-utils fonts-dejavu-core \
        libx11-6 libxi6 libxxf86vm1 libxfixes3 libxrender1 libxkbcommon0 libsm6 libice6 \
        libgl1 libegl1 libgl1-mesa-dri libglu1-mesa libgomp1 libwayland-client0 libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

ARG BLENDER_VERSION=5.1.2
RUN curl -fsSL "https://download.blender.org/release/Blender${BLENDER_VERSION%.*}/blender-${BLENDER_VERSION}-linux-x64.tar.xz" \
        | tar -xJ -C /opt \
    && mv "/opt/blender-${BLENDER_VERSION}-linux-x64" /opt/blender

# Hugging Face runs the container as user 1000.
RUN useradd -m -u 1000 user && mkdir -p /home/user/app && chown user:user /home/user/app
WORKDIR /home/user/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=user . .
USER user

# No GPU: render with Workbench (see V3_RENDER_ENGINE in blender_builder_v3.py).
ENV BLENDER_EXE=/opt/blender/blender \
    V3_RENDER_ENGINE=WORKBENCH

EXPOSE 7860
CMD ["uvicorn", "web.server:app", "--host", "0.0.0.0", "--port", "7860", \
     "--no-server-header", "--proxy-headers", "--forwarded-allow-ips", "*"]

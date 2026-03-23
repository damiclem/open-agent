# https://podman-desktop.io/docs/podman/gpu

# Set fedora version
FROM fedora:44
# Set root user
USER 0

# Install dependencies + Vulkan libkrun drivers
RUN dnf -y install dnf-plugins-core dnf-plugin-versionlock && \
    dnf -y install mesa-vulkan-drivers vulkan-loader-devel vulkan-headers vulkan-tools glslc @development-tools gcc-c++ cmake wget libcurl-devel curl && \
    dnf -y copr enable slp/mesa-libkrun-vulkan && \
    REPOID="copr:copr.fedorainfracloud.org:slp:mesa-libkrun-vulkan" && \
    MESA_VERSION=$(dnf repoquery -q --available --repoid="$REPOID" --latest-limit=1 --qf '%{evr}' mesa-vulkan-drivers 2>/dev/null) && \
    dnf downgrade -y "mesa-vulkan-drivers-${MESA_VERSION}" && \
    dnf versionlock add "mesa-vulkan-drivers-${MESA_VERSION}" && \
    dnf clean all && rm -rf /var/cache/dnf

# Clone into llama.cpp & build llama.cpp
# https://github.com/ggml-org/llama.cpp/blob/master/.devops/vulkan.Dockerfile
RUN git clone https://github.com/ggml-org/llama.cpp.git

# Set working directory
WORKDIR /llama.cpp

# Compile llama.cpp
RUN cmake -B build -DGGML_OPENMP=OFF -DGGML_VULKAN=ON && \
    cmake --build build --config Release -j1 --target llama-cli llama-bench llama-server VERBOSE=1

# Execute llama.cpp CLI
# -ngl N controls GPU offload:
   # 99 offloads as many transformer layers as possible to the GPU.
   # 0 disables GPU offload, forcing inference on the CPU
# GPU-accelerated (offload up to 99 layers)
CMD [ "./build/bin/llama-cli", "--list-devices" ]

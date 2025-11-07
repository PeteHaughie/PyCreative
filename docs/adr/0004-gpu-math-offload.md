# 0004 - GPU Math Offload

Date: 2025-10-07

Status: Proposed

Context
-------

## Context

We want to accelerate matrix and vector mathematics operations in Python by moving computation from CPU to GPU. This must be implemented in a way that avoids CUDA, so the solution will be portable across consumer Mac hardware (including Apple Silicon) and Raspberry Pi (RPi) SoCs. We presume GPU compute should be accomplished using APIs such as Metal, Vulkan, or OpenGL (3+), as appropriate for the platform. Prefer generic single portable solution over specific platform solutions where possible.git add 

Typical GPU-accelerated Python libraries (e.g., CuPy) rely on CUDA and are thus not suitable. Common targets:

- **macOS / Apple Silicon:** Prefers Metal or OpenCL.
- **RPi and many Linux platforms:** Prefers OpenCL, OpenGL, or (possibly) Vulkan.

## Decision

After investigation, the following options were considered:

### 1. [ArrayFire](https://arrayfire.com/)
- **Backends:** OpenCL, CUDA, CPU.
- **Python bindings**: Yes.
- **Pros:** Mature, supports OpenCL (works on Mac and RPi if drivers available), high-level array math, portable.
- **Cons:** Metal is not supported natively, but some Mac OpenCL implementations map to Metal.

### 2. [pyopencl](https://documen.tician.de/pyopencl/)
- **Backends:** OpenCL.
- **Pros:** Direct, flexible, portable, supports Apple Silicon and ARM platforms with OpenCL.
- **Cons:** Requires manual kernel authoring and computation management.

### 3. [TensorFlow with Metal plugin](https://developer.apple.com/metal/tensorflow-plugin/)
- **Backends:** Metal (Mac), fallback to CPU elsewhere.
- **Pros:** Accelerates general math on Mac, high-level API.
- **Cons:** Mac-only hardware acceleration, overkill for non-ML workloads.

### 4. [PyTorch MPS Backend](https://pytorch.org/docs/stable/notes/mps.html)
- **Backends:** Metal via MPS (Mac), CPU.
- **Pros:** Simple tensor math on Mac.
- **Cons:** Mac-only; not portable to ARM/Linux.

### 5. [moderngl](https://moderngl.readthedocs.io/)
- **Backends:** OpenGL 3.3+
- **Pros:** Cross-platform; can use OpenGL compute or fragment shaders.
- **Cons:** Low-level; need to write own compute shaders for array math.

### 6. [Vulkan libraries](https://github.com/realitix/vulkan)
- **Backends:** Vulkan
- **Pros:** Modern, flexible, but very low-level.
- **Cons:** No mature high-level Python math or array libraries yet; not simple to use.

**Summary Table:**

| Library      | Backend(s)                  | Mac | RPi | Notes             |
|--------------|-----------------------------|-----|-----|-------------------|
| ArrayFire    | OpenCL, CUDA, CPU           | ✔️  | ✔️  | High-level, uses OpenCL |
| PyOpenCL     | OpenCL                      | ✔️  | ✔️  | Lower-level, portable   |
| TensorFlow   | Metal Plugin (Mac), CPU     | ✔️  |     | Mac-optimized     |
| PyTorch      | MPS (Metal), CPU            | ✔️  |     | Mac-optimized     |
| moderngl     | OpenGL                      | ✔️  | ✔️  | General OpenGL compute |
| Vulkan/python-vulkan | Vulkan              | (⚠️) | (⚠️)| Low-level, not mature for GPGPU |

## Consequences

- **Preference for Portability:** Solutions like ArrayFire and pyopencl provide broad support using OpenCL; Metal and MPS (PyTorch) are great for Mac-only, but not cross-platform.
- **Abstraction Level:** Higher-level APIs (ArrayFire, TensorFlow) are easier but less flexible, lower-level APIs (PyOpenCL, moderngl) require more manual setup.
- **If OpenCL is supported by the hardware and drivers, ArrayFire or pyopencl are the best portable choices.**
- **For maximum performance (and minimal code changes) on Mac, consider Metal-backed TensorFlow or PyTorch—but with reduced portability.**
- OpenGL compute via moderngl is viable as a fallback, but requires writing GPU shader code manually.

## Example Usage (ArrayFire):

```python
import arrayfire as af
a = af.Array([1, 2, 3, 4, 5])
b = af.Array([6, 7, 8, 9, 10])
c = a + b  # Performed on the GPU!
```

## Example Usage (pyopencl):

```python
import pyopencl as cl
import numpy as np

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

a_np = np.array([1, 2, 3, 4, 5]).astype(np.float32)
b_np = np.array([6, 7, 8, 9, 10]).astype(np.float32)
mf = cl.mem_flags

a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)
b_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b_np)
res_g = cl.Buffer(ctx, mf.WRITE_ONLY, a_np.nbytes)

prg = cl.Program(ctx, """
__kernel void sum(__global const float *a, __global const float *b, __global float *res) {
    int gid = get_global_id(0);
    res[gid] = a[gid] + b[gid];
}
""").build()

prg.sum(queue, a_np.shape, None, a_g, b_g, res_g)
res_np = np.empty_like(a_np)
cl.enqueue_copy(queue, res_np, res_g)
print(res_np)
```

## Related Decisions

- Use platform-appropriate OpenCL, Metal, or OpenGL backends.
- CUDA libraries (CuPy, Numba CUDA) are not considered due to required NVIDIA GPU support.

## References

- [ArrayFire Documentation](https://arrayfire.com/docs/)
- [PyOpenCL Documentation](https://documen.tician.de/pyopencl/)
- [Apple Metal for TensorFlow](https://developer.apple.com/metal/tensorflow-plugin/)
- [PyTorch MPS Backend](https://pytorch.org/docs/stable/notes/mps.html)
- [moderngl Docs](https://moderngl.readthedocs.io/)
- [python-vulkan repo](https://github.com/realitix/vulkan)
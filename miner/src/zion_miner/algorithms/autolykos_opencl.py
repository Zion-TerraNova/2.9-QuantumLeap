import pyopencl as cl
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

class AutolykosOpenCL:
    def __init__(self, platform_idx=0, device_idx=0):
        self.ctx = None
        self.queue = None
        self.program = None
        self.initialized = False
        
        try:
            platforms = cl.get_platforms()
            if not platforms:
                raise RuntimeError("No OpenCL platforms found")
            
            platform = platforms[platform_idx]
            devices = platform.get_devices()
            if not devices:
                raise RuntimeError("No OpenCL devices found")
            
            device = devices[device_idx]
            logger.info(f"Using OpenCL device: {device.name}")
            
            self.ctx = cl.Context([device])
            self.queue = cl.CommandQueue(self.ctx)
            
            # Load kernel source
            kernel_path = os.path.join(os.path.dirname(__file__), "autolykos_v2.cl")
            with open(kernel_path, "r") as f:
                kernel_src = f.read()
            
            self.program = cl.Program(self.ctx, kernel_src).build()
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenCL: {e}")
            raise

    def hash_batch(self, input_data: bytes, nonces: list[int]) -> list[bytes]:
        if not self.initialized:
            raise RuntimeError("OpenCL not initialized")
            
        count = len(nonces)
        if count == 0:
            return []
            
        input_len = len(input_data)
        
        # Prepare buffers
        mf = cl.mem_flags
        
        # Input buffer (single shared input)
        input_np = np.frombuffer(input_data, dtype=np.uint8)
        d_input = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=input_np)
        
        # Nonces buffer
        nonces_np = np.array(nonces, dtype=np.uint32)
        d_nonces = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=nonces_np)
        
        # Output buffer (32 bytes per nonce)
        output_size = 32 * count
        d_output = cl.Buffer(self.ctx, mf.WRITE_ONLY, size=output_size)
        
        # Execute kernel
        global_size = (count,)
        local_size = None  # Let driver decide
        
        self.program.autolykos_kernel(
            self.queue, 
            global_size, 
            local_size,
            d_input,
            np.uint32(input_len),
            d_nonces,
            d_output,
            np.uint32(count)
        )
        
        # Read result
        output_np = np.empty(output_size, dtype=np.uint8)
        cl.enqueue_copy(self.queue, output_np, d_output)
        
        # Parse results
        results = []
        for i in range(count):
            start = i * 32
            end = start + 32
            results.append(bytes(output_np[start:end]))
            
        return results

    def hash_single(self, input_data: bytes, nonce: int) -> bytes:
        return self.hash_batch(input_data, [nonce])[0]

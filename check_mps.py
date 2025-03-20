#!/usr/bin/env python3
# Script to check MPS (Metal Performance Shaders) status and memory usage

import torch
import subprocess
import os
import time
import platform
import sys

def print_header(message):
    print("\n" + "=" * 50)
    print(message)
    print("=" * 50)

def check_mps_availability():
    print_header("MPS AVAILABILITY")
    
    # Check if MPS is available
    mps_available = torch.backends.mps.is_available()
    mps_built = torch.backends.mps.is_built()
    
    print(f"MPS is built: {mps_built}")
    print(f"MPS is available: {mps_available}")
    
    if not mps_available:
        print("\nMPS is not available. Possible reasons:")
        print("- You are not using macOS 12.3+")
        print("- You are not using a Mac with Apple Silicon (M1/M2/M3)")
        print("- PyTorch was not compiled with MPS support")
        
        # Show macOS version
        print(f"\nYour macOS version: {platform.mac_ver()[0]}")
        
        if not platform.processor() or 'arm' not in platform.processor().lower():
            print("Your processor does not appear to be Apple Silicon.")
            print(f"Processor detected: {platform.processor()}")
        
        sys.exit(1)
    
    print("\nGood news! MPS is available on your system.")
    return mps_available

def check_torch_version():
    print_header("TORCH VERSION")
    print(f"PyTorch version: {torch.__version__}")
    print(f"Torch CUDA available: {torch.cuda.is_available()}")
    print(f"Torch device count: {torch.cuda.device_count() if torch.cuda.is_available() else 'N/A'}")

def get_memory_usage():
    try:
        # Run vm_stat command to get memory information
        vm_stat = subprocess.check_output(['vm_stat'], universal_newlines=True)
        lines = vm_stat.strip().split('\n')
        
        # Extract memory metrics (each page is 4096 bytes or 4KB)
        memory_stats = {}
        page_size_kb = 4  # 4KB per page
        
        for line in lines[1:]:  # Skip the first line (header)
            if ':' in line:
                key, value = line.split(':')
                key = key.strip()
                value = int(value.strip('.').strip())
                memory_stats[key] = value * page_size_kb / 1024  # Convert to MB
        
        # Extract the information we need
        free_mb = memory_stats.get("Pages free", 0)
        active_mb = memory_stats.get("Pages active", 0)
        inactive_mb = memory_stats.get("Pages inactive", 0)
        wired_mb = memory_stats.get("Pages wired down", 0)
        compressed_mb = memory_stats.get("Pages occupied by compressor", 0)
        
        # Calculate total physical memory
        total_mb = free_mb + active_mb + inactive_mb + wired_mb + compressed_mb
        
        # Get GPU memory utilization for Apple Silicon
        try:
            # Use system_profiler to get GPU info
            gpu_info = subprocess.check_output(
                ['system_profiler', 'SPDisplaysDataType'], 
                universal_newlines=True
            )
            
            # This is a very rough approximation as macOS doesn't expose exact GPU memory usage
            # through standard tools like system_profiler
            gpu_memory_line = "GPU Memory: "
            gpu_memory_mb = "N/A"
            
            if "Metal" in gpu_info:
                print("Metal GPU detected")
            else:
                print("Metal GPU information not found")
                
        except Exception as e:
            print(f"Error getting GPU info: {e}")
            gpu_memory_mb = "N/A"
        
        return {
            "total_physical_mb": total_mb,
            "free_mb": free_mb,
            "active_mb": active_mb,
            "inactive_mb": inactive_mb,
            "wired_mb": wired_mb,
            "compressed_mb": compressed_mb,
            "gpu_memory_mb": gpu_memory_mb
        }
    except Exception as e:
        print(f"Error getting memory stats: {e}")
        return {}

def test_tensor_allocation():
    print_header("TENSOR ALLOCATION TEST")
    
    # Try to allocate tensors of increasing size to see when it fails
    device = torch.device("mps")
    
    for size_mb in [100, 500, 1000, 2000, 4000, 8000, 16000]:
        try:
            # Calculate number of elements for the target size in MB (4 bytes per float32)
            elements = size_mb * 1024 * 1024 // 4  
            
            print(f"Attempting to allocate {size_mb}MB tensor...")
            
            # Record start time
            start_time = time.time()
            
            # Create tensor
            x = torch.rand(elements, device=device)
            
            # Ensure tensor is allocated by doing a small operation
            y = x + 1
            
            # Ensure operation is complete
            torch.mps.synchronize()
            
            # Calculate elapsed time
            elapsed = time.time() - start_time
            
            print(f"✓ Successfully allocated {size_mb}MB tensor in {elapsed:.2f} seconds")
            
            # Free memory
            del x, y
            torch.mps.empty_cache()
            
        except Exception as e:
            print(f"✗ Failed to allocate {size_mb}MB tensor: {e}")
            break
    
    print("\nTensor allocation test complete.")

def show_model_memory_requirements():
    print_header("MODEL MEMORY REQUIREMENTS")
    
    model_sizes = {
        "gemma-3-2b-it": "~4 GB",
        "gemma-3-4b-it": "~8 GB",
        "gemma-3-8b-it": "~16 GB",
        "gemma-3-27b-it": "~54 GB"
    }
    
    print("Estimated memory requirements for Gemma 3 models:")
    
    for model, size in model_sizes.items():
        print(f"- {model}: {size}")
    
    print("\nNote: Actual memory usage may be higher due to:")
    print("- Tokenization and processing overhead")
    print("- Input/output tensors")
    print("- Memory fragmentation")
    print("- Operating system and other applications")

def main():
    print_header("MPS DIAGNOSTIC TOOL")
    print("This tool checks Apple Silicon GPU (MPS) availability and memory")
    
    if check_mps_availability():
        check_torch_version()
        
        print_header("SYSTEM MEMORY")
        memory_stats = get_memory_usage()
        
        if memory_stats:
            print(f"Total Physical Memory: {memory_stats['total_physical_mb']:.0f} MB")
            print(f"Free Memory: {memory_stats['free_mb']:.0f} MB")
            print(f"Active Memory: {memory_stats['active_mb']:.0f} MB")
            print(f"Inactive Memory: {memory_stats['inactive_mb']:.0f} MB")
            print(f"Wired Memory: {memory_stats['wired_mb']:.0f} MB")
            print(f"Compressed Memory: {memory_stats['compressed_mb']:.0f} MB")
            print(f"GPU Memory (dedicated): {memory_stats['gpu_memory_mb']}")
            
            available_mem = memory_stats['free_mb'] + memory_stats['inactive_mb']
            print(f"\nEstimated Available Memory: {available_mem:.0f} MB")
        
        show_model_memory_requirements()
        
        # Ask if user wants to run allocation test
        response = input("\nWould you like to run a tensor allocation test? (y/n): ")
        if response.lower() == 'y':
            test_tensor_allocation()
        
        print_header("RECOMMENDATIONS")
        
        if memory_stats and available_mem < 8000:
            print("⚠️ Your available memory may be too low for gemma-3-4b-it.")
            print("Consider:")
            print("1. Closing other applications to free up memory")
            print("2. Using a smaller model like gemma-3-2b-it")
            print("3. Using fp16 precision instead of fp32")
            print("4. Adding more swap space")
        else:
            print("✅ Your system appears to have sufficient memory for the gemma-3-4b-it model.")
        
        print("\nTo run the model, try:")
        print("./run_element_check.sh")
        
    print_header("DIAGNOSTIC COMPLETE")

if __name__ == "__main__":
    main() 
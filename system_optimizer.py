"""
System optimization module for the Optimus Prime Voice Assistant
"""
import os
import psutil


class SystemOptimizer:
    @staticmethod
    def optimize_system_performance():
        """Optimize system performance for M3 Pro MacBook"""
        try:
            # Set process priority to high for better performance
            os.nice(-10)  # Higher priority
            
            # Optimize for M3 Pro architecture
            # Set environment variables for better performance
            os.environ['PYTHONUNBUFFERED'] = '1'
            os.environ['OMP_NUM_THREADS'] = '8'  # M3 Pro has 8 performance cores
            os.environ['MKL_NUM_THREADS'] = '8'
            
            # Configure psutil for better resource monitoring
            psutil.cpu_percent(interval=None)  # Initialize CPU monitoring
            
            print("🚀 System optimized for M3 Pro MacBook")
            print(f"💻 CPU Cores: {psutil.cpu_count()}")
            print(f"🧠 Memory: {psutil.virtual_memory().total // (1024**3)} GB")
            
        except Exception as e:
            print(f"⚠️ System optimization warning: {e}")

    @staticmethod
    def monitor_system_resources():
        """Monitor system resources and adjust performance accordingly"""
        try:
            # Get current CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            
            # Adjust performance based on system load
            if cpu_percent > 80 or memory_percent > 85:
                print(f"⚠️ High system load - CPU: {cpu_percent}%, Memory: {memory_percent}%")
                return False  # Reduce processing
            elif cpu_percent > 60 or memory_percent > 70:
                print(f"📊 Moderate system load - CPU: {cpu_percent}%, Memory: {memory_percent}%")
                return True   # Normal processing
            else:
                return True   # Full performance
        except:
            return True  # Default to full performance if monitoring fails
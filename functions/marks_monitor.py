import subprocess

class MarksMonitor:
    def __init__(self):
        self.monitor_marks_process = None  # Track the running monitor marks process

    def start_monitor_marks(self):
        """
        Run the external monitor marks script
        """
        try:
            # Run the monitor_marks.py script in the background
            self.monitor_marks_process = subprocess.Popen([
                "/Users/kavan/Desktop/egov_is_hacked/egovENV/bin/python",
                "/Users/kavan/Desktop/egov_is_hacked/monitor_marks.py"
            ])
            print("✅ Monitor marks script started successfully")
            return True
        except Exception as e:
            print(f"❌ Error running monitor marks script: {e}")
            return False

    def stop_monitor_marks(self):
        """
        Stop the running monitor marks script if it's active
        """
        if self.monitor_marks_process and self.monitor_marks_process.poll() is None:
            # Process is still running, terminate it
            try:
                import signal
                self.monitor_marks_process.terminate()  # Try graceful termination first
                self.monitor_marks_process.wait(timeout=2)  # Wait up to 2 seconds for process to finish
                print("✅ Monitor marks script stopped successfully")
                return True
            except subprocess.TimeoutExpired:
                # Process didn't terminate in time, force kill it
                try:
                    self.monitor_marks_process.kill()  # Force kill the process
                    self.monitor_marks_process.wait()  # Wait for it to be cleaned up
                    print("✅ Monitor marks script force stopped")
                    return True
                except Exception as e:
                    print(f"❌ Error stopping monitor marks script: {e}")
                    return False
            except Exception as e:
                print(f"❌ Error stopping monitor marks script: {e}")
                return False
        else:
            print("❌ No active monitor marks process to stop")
            return False

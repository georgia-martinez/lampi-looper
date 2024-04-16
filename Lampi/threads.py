import threading
import time

# Define a function that performs some task in a loop
def task(flag):
    while not flag.is_set():  # Check the flag state
        print("Task is running...")
        time.sleep(1)

# Main program
def main():
    # Create a threading.Event object to act as the flag
    stop_flag = threading.Event()

    # Create a thread for the task function
    task_thread = threading.Thread(target=task, args=(stop_flag,))
    task_thread.start()

    # Let the task run for some time
    time.sleep(5)

    # Set the flag to stop the task
    stop_flag.set()

    # Wait for the task thread to finish
    task_thread.join()

    print("Task stopped.")

if __name__ == "__main__":
    main()
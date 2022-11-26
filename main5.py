# start two python processes, main3.py and main4.py
# main3.py and main4.py will run in parallel

# import the multiprocessing module
import multiprocessing
import subprocess

# define a function for the thread
def print_cube():
    """
    function to print cube of given num
    """
    subprocess.call(["python", "main3.py"])

# define a function for the thread
def print_square():
    """
    function to print square of given num
    """
    subprocess.call(["python", "main4.py"])

if __name__ == "__main__":
    # creating processes
    p1 = multiprocessing.Process(target=print_square)
    p2 = multiprocessing.Process(target=print_cube)

    # starting process 1
    p1.start()
    # starting process 2
    p2.start()

    # wait until process 1 is finished
    p1.join()
    # wait until process 2 is finished
    p2.join()

    # both processes finished
    print("Done!")
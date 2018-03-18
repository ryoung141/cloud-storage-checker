import requests
import time
import pyspeedtest
import sys
import os


def googleTest(benchmark):
    print("\n------ GOOGLE TEST ------")
    t = time.time()

    r = requests.get("https://drive.google.com/uc?export=download&id=1iTq9a-g4G3lc56cD0WceNnS3WWq98spO")
    end_t = time.time() - t
    print("Download finished in: " + str(end_t) + " seconds")

    open("test", "wb").write(r.content)
    st = os.stat("test")
    print("Size of file downloaded: " + str(st.st_size))

    drive_rate = st.st_size / end_t
    print("Download rate: " + str(drive_rate / 1000000.0) + " MB/s")

    if(drive_rate >= benchmark):
        print("Your connection to Google is good-to-go.")
    else:
        print("A discrepancy of size " + str((benchmark - drive_rate) / 1000000.0) + " MB/s has been detected with your connection to Google")


def facebookTest(benchmark):
    print("\n------ FACEBOOK TEST ------")
    t = time.time()

    r = requests.get("https://www.facebook.com/facebook/?brand_redir=103274306376166")
    end_t = time.time() - t
    print("Download finished in: " + str(end_t) + " seconds")

    open("test", "wb").write(r.content)
    st = os.stat("test")
    print("Size of file downloaded: " + str(st.st_size))

    fb_rate = st.st_size / end_t
    print("Download rate: " + str(fb_rate / 1000000.0) + " MB/s")

    if(fb_rate >= benchmark):
        print("Your connection to Facebook is good-to-go.")
    else:
        print("A discrepancy of size " + str((benchmark - fb_rate) / 1000000.0) + " MB/s has been detected with you connection to Facebook")


def standardTest(benchmark):
    print("\n------ PICSUM TEST ------")
    t = time.time()

    r = requests.get("https://picsum.photos/5000")
    end_t = time.time() - t
    print("Download finished in: " + str(end_t) + " seconds")

    open("test", "wb").write(r.content)
    st = os.stat("test")
    print("Size of file downloaded: " + str(st.st_size))

    st_rate = st.st_size / end_t
    print("Download rate: " + str(st_rate / 1000000.0) + " MB/s")

    if(st_rate >= benchmark):
        print("Your connection to Picsum is good-to-go.")
    else:
        print("A discrepancy of size " + str((benchmark - st_rate) / 1000000.0) + " MB/s has been detected with your connection to Picsum")


#returns benchmark avg after number of iterations
def benchmarkGenerator(iterations):
    st = pyspeedtest.SpeedTest()
    benchmark = 0
    for x in range(0, int(iterations)):
        benchmark += st.download()

    benchmark = benchmark / int(iterations)
    return benchmark

#used to find the ideal number of iterations to get the most accurate benchmark
def benchmarkGeneratorTest():
    for x in range(1, 100):
        ret = benchmarkGenerator(x)
        print(str(ret / 8000000.0) + " MB/s with " + str(x) + " iterations.")

#applies margin of error to the passed benchmark, chosen to be 20% for now
def marginOfError(benchmark):
    return(benchmark - (benchmark * .2))

def main(iterations):
    st = pyspeedtest.SpeedTest()
    benchmark = 0

    #want to do 10 iterations and avg them out to get a good average speed
    for x in range(0, int(iterations)):
        benchmark += st.download()
    benchmark = benchmark / (int(iterations))
    print(benchmark)

    #convert b/s to MB/s
    benchmark = benchmark / 8
    print("The benchmark speed is: " + str(benchmark / 1000000.0) + " MB/s")

    benchmark = marginOfError(benchmark)
    print("The speed we're testing is: " + str(benchmark / 1000000.0) + " MB/s\n")

    facebookTest(benchmark)
    standardTest(benchmark)
    googleTest(benchmark)
    os.remove("test")



# benchmarkGeneratorTest() <--- used to find optimal number of iterations
main(sys.argv[1])
    
import random
import simpy
import math
import matplotlib.pyplot as plt

RANDOM_SEED = 42
NUM_QUEUE = 2
NUM_DOCTORS = 2
T_INTER = 6
MIN_TREAT = 5
MAX_TREAT = 10
SIM_TIME = 300

WaitTime = dict()
ArrivalTime = dict()

def analyze(data):

    def min1(data):
        x = 1000.0
        for i in data:
            inum = float(i)
            if inum < x:
                x = inum
        return x

    def max1(data):
        x=0
        for i in data:
            inum = float(i)
            if inum > x:
                x = inum
        return x

    def median1(data):
        n = len(data)
        if n % 2 == 1:
            return sorted(data)[n//2]
        else:
            return sum(sorted(data)[n//2-1:n//2+1])/2.0

    def mean1(data):
        n = len(data)
        x = sum(data)
        avg = x / n
        return avg

    def stddev(data):
        mean = float(sum(data)) / len(data)
        return math.sqrt(float(reduce(lambda x, y: x + y, map(lambda x: (x - mean) ** 2, data))) / len(data))

    minval = min1(data)
    maxval = max1(data)
    median = round(median1(data), 2)
    mean = round(mean1(data), 2)
    std = round(stddev(data), 2)
    lngth = len(data)

    return [minval, maxval, median, mean, std, lngth]

class Clinic(object):

    def __init__(self, env, num_doctors):
        self.env = env
        self.docroom = [simpy.Resource(env, 1) for i in range(NUM_DOCTORS)]


    def treat(self, patient):
        x = random.uniform(MIN_TREAT, MAX_TREAT)
        yield self.env.timeout(x)

def patient(env, name, cl, i):

    arrive = env.now
    ArrivalTime[name] = arrive
    print('Patient %d arrives at the clinic at %.2f.' % (name, arrive))
    with cl.docroom[i].request() as request:
        yield request

        wait = env.now - arrive
        waiting = env.now
        yield env.process(cl.treat(name))

        treatment = env.now - waiting
        print('Patient %d enter doctor room %d after %.2f time and leaves after spending %.2f time in doctor room' % (name, i, wait, treatment))
        WaitTime[name] = wait

def setup(env, num_doctors, t_inter, num_queue):

    clinic = Clinic(env, num_doctors)

    # Create patients
    for i in range(4):
        env.process(patient(env, i, clinic, random.randint(0, NUM_QUEUE - 1)))

    while True:
        yield env.timeout(random.randint(t_inter - 2, t_inter + 2))
        i += 1
        env.process(patient(env, i, clinic, random.randint(0, NUM_QUEUE- 1)))

def chart(data, mean):
    plt.figure(1)
    plt.plot(data, 'r.')
    plt.plot([0, 400],[mean, mean], 'c-')
    plt.legend(['Czas oczekiwania', 'Srednia oczekiwania'])
    plt.gca().set_xlim([0, 60])
    plt.xlabel('Numer pacjenta')
    plt.ylabel('Wait time')
    plt.title("Wykres")
    plt.savefig("fig1.png")
    plt.show()

# Setup
print('Przychodnia')
random.seed(RANDOM_SEED)

# Create an environment
env = simpy.Environment()
env.process(setup(env, NUM_DOCTORS, T_INTER, NUM_QUEUE))

# Execute
env.run(until=SIM_TIME)
print "czas oczekiwania: " , WaitTime

keys, values = WaitTime.keys(), WaitTime.values()
k = ArrivalTime.values()
w = analyze(values)
x = analyze(k)

print "Data: "
print "#     ", \
    "{:>7}".format("Doctors"), "\t", \
    "{:>7}".format("Queues"), "\t", \
    "{:>7}".format("Min"), "\t", \
    "{:>7}".format("Max"), "\t", \
    "{:>7}".format("Median"), "\t", \
    "{:>7}".format("Mean"), "\t", \
    "{:>7}".format("Std"), "\t", \
    "{:>7}".format("Clients in"), "\t", \
    "{:>7}".format("Clients out"), "\t"
print "Data:", \
    "{:7}".format(NUM_DOCTORS), "\t", \
    "{:7}".format(NUM_QUEUE), "\t", \
    "{:7}".format(w[0]), "\t", \
    "{:7}".format(round(w[1], 2)), "\t", \
    "{:7}".format(w[2]), "\t", \
    "{:7}".format(w[3]), "\t", \
    "{:7}".format(w[4]), "\t", \
    "{:7}".format(x[5]), "\t", \
    "{:7}".format(w[5]), "\t"

chart(values, w[3])
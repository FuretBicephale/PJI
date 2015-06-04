from optparse import OptionParser
from brian2 import *
from random import gauss

### Parser
parser = OptionParser()
parser.add_option("-s", "--supervised", action="store_true",
    help='''Specify the kind of learning (supervised or not). Value = True or False''',
    default=False)

(options, args) = parser.parse_args()

try :
    supervised = options.supervised
except :
    print "Error : Invalid argument. See help for more informations."
    parser.print_help()
    exit(False)

### Input neurons - 2 pixels with 2 states (ON/OFF).
nbPixels = 2;
nbPixelStates = 2;

# Movements
down = [1, 2]
up = [3, 0]
time = [1, 1] # Duree mouvement : 0 * ms

# Learning
indices = (down + up) * 20
times = time + [i + j for j in range(2, 80, 2) for i in time]
# Temps entre deux mouvement : 2 * ms
# Periode d'un mouvement : 4 * ms

# Test for success
indices += (down + up) * 3
times += [i + j for j in range(90, 102, 2) for i in time]

times *= ms
input = SpikeGeneratorGroup(nbPixels * nbPixelStates, indices, times)

### Output neurons - We want to know if the movement is ascending or descending
nbOutput = 2

tLeak = 1.5*ms # Leak time (> Duree mouvement)
if(supervised):
    tRefrac = 1*ms # Minimum time between two presynaptics spikes (> Inhibition, < Periode)
else:
    tRefrac = 3.5*ms
tInhib = 1.5*ms # Minimum time before an inhibited spike can receive presynaptics spikes agains (= Temps entre deux mouvements)

# Neurons model
if not supervised:
    eqs = '''dv/dt = -v/tLeak : volt (unless refractory)
             thresh : volt
             refrac : second
             lastInhib : second'''
else:
    eqs = '''dv/dt = -v/tLeak : volt (unless refractory)
             thresh : volt
             refrac : second'''

# threshold = 1100*volt # Neurons send a spike when this threshold is reached
reset = 0*volt # Initial neurons value

output = NeuronGroup(nbOutput, eqs, threshold='v + dt*(v/tLeak) >= thresh', reset='v=reset', refractory='refrac')
output.refrac = tRefrac

### Synapses - Each input is linked to each output
wInitAverage = 0.500*volt # Initial synaptic weight values
wInitDeviation = 0.200*volt
wMax = 1.000*volt # Maximum Synaptic weight
wMin = 0.001*volt # Minimum synaptic weight

aPre = 0.100*volt # Alpha values for presynaptics spikes
aPost = 0.050*volt # Apha values for postsynaptics spikes
bPre = 0*volt # Beta values for presynaptics spikes
bPost = 0*volt # Beta values for postsynaptics spikes

tLTP = 1*ms # Maximum time between post and pre spikes to launch a LTP

# ltpCondition is true if the synapse deals with a Potentiation, false if it's a Depression
synapsesModel = '''w : volt
                   dwPre = aPre * exp(-bPre*(w-wMin/wMax-wMin)) : volt
                   dwPost = aPost * exp(-bPost*(wMax-w/wMax-wMin)) : volt
                   tPre : second
                   tPost : second
                   ltpCondition = (tPost - tPre) >= (0 * second) and (tPost - tPre) <= tLTP : 1'''
if not supervised:
    preEqs = '''tPre = t
                v = v * (t - lastInhib < tInhib and lastInhib != 0 * ms) + (v * exp(-(t-lastupdate)/tLeak) + w) *  (t - lastInhib >= tInhib or lastInhib == 0 * ms)'''
else:
    preEqs = '''tPre = t
                v = v + w'''
# If ltpCondition is False then it's equals to 0, 1 otherwise
# So dwPre * (ltpCondition) = 0 if ltpCondition is false, dwPre otherwise
# And dwPost * (ltpCondition != 1) = 0 if ltpCondition is true (== 0), dwPost otherwise
postEqs = '''tPost = t
             w = clip(w + dwPre * ltpCondition, wMin, wMax)
             w = clip(w - dwPost * (ltpCondition == 0), wMin, wMax)'''
synapses = Synapses(input, target=output, model=synapsesModel, pre=preEqs, post=postEqs)
synapses.connect(True) # Connecting every neurons of the first layer to every neurons of the second one

# Initialize synaptic weight with a gauss distribution
if(supervised):
    synapses.w = wInitAverage
else:
    for i in range(nbPixels * nbPixelStates):
        for  j in range(nbOutput):
            synapses.w[i,j] = clip(
                gauss(wInitAverage, wInitDeviation),
                wMin,
                wMax)

if(supervised):
    # output.thresh = min(synapses.w[1, 0] + synapses.w[2, 0], synapses.w[1, 1] + synapses.w[2, 1])
    output.thresh = 0.500 * volt
else:
    output.thresh = 0.600 * volt

if not supervised:
    # Inhibition
    inhibition = Synapses(output, target=output, model='w : volt', pre='''
        lastInhib = lastInhib * (1 - int(not_refractory)) + t * int(not_refractory)''')
    inhibition.connect("i != j") # Every neurons of the layer are connected to each other
    inhibition.w = wInitAverage
else:
    # Supervised learning input
    learningIndices = [0, 1] * 20
    learningTimes = [(time[0] - 0.5) + j for j in range(0, 80, 2)] * ms

    learningInput = SpikeGeneratorGroup(nbOutput, learningIndices, learningTimes)
    learningSynapses = Synapses(learningInput, target=output, model='w : volt', pre='''v = thresh + dt * thresh/tLeak''')
    learningSynapses.connect("i == j")
    learningSynapses.w = wInitAverage

# Monitor
record = SpikeMonitor(output) # Record output layer spikes
recordInput = SpikeMonitor(input) # Record input layer spikes
stateRecord = StateMonitor(output, ('v', 'refrac'), record = True) # Record the state of each neurons of the output layer
synapsesRecord = StateMonitor(synapses, ('w'), record = True) # Record the state of each synapses

# Save the state of the network
store()

# Run
print ''
timeRun = 110*ms
run(timeRun, report='stdout')
nbTry = 1

# Verify if the system has learned the pattern
learned = True
if(len(record.i) < 4):
    learned = False
else:
    for i in range(1, 5):
        if(record.i[len(record.i) - i] == record.i[len(record.i) - (i+1)] or
                record.t[len(record.t) - i] == record.t[len(record.t) - (i+1)]):
            learned = False

# Rerun until the learning is good
while(not learned):

    # Display simulation plot
    # plot(stateRecord.t/ms, [output.thresh[0] for i in range(len(stateRecord.t))], '--', label='threshold')
    # for i in range(nbOutput) :
    #     plot(stateRecord.t/ms, stateRecord.v[i]/volt, label=i)
    # legend()
    # show()

    # Restore initial network
    restore()
    nbTry = nbTry + 1

    # Initialize synaptic weight with a gauss distribution
    if(supervised):
        synapses.w = wInitAverage
    else:
        for i in range(nbPixels * nbPixelStates):
            for  j in range(nbOutput):
                synapses.w[i,j] = clip(
                    gauss(wInitAverage, wInitDeviation),
                    wMin,
                    wMax)

    # if(supervised):
    #     # output.thresh = min(synapses.w[1, 0] + synapses.w[2, 0], synapses.w[1, 1] + synapses.w[2, 1])
    #     output.thresh = 600 * volt
    # else:
    #     output.thresh = 600 * volt

    # Rerun
    print ''
    print 'The learning was wrong. Re-running the simulation'
    run(timeRun, report='stdout')

    # Re-Verify if the system has learned the pattern
    learned = True
    if(len(record.i) < 4):
        learned = False
    else:
        for i in range(1, 5):
            if(record.i[len(record.i) - i] == record.i[len(record.i) - (i+1)] or
                    record.t[len(record.t) - i] == record.t[len(record.t) - (i+1)]):
                learned = False

# Display simulation plot
plot(stateRecord.t/ms, [output.thresh[0] for i in range(len(stateRecord.t))], '--', label='threshold')
for i in range(nbOutput) :
    plot(stateRecord.t/ms, stateRecord.v[i]/volt, label=i)
legend()
show()

# print synapses.w[0,0]
# print synapses.w[0,1]
# print synapses.w[1,0]
# print synapses.w[1,1]
# print synapses.w[2,0]
# print synapses.w[2,1]
# print synapses.w[3,0]
# print synapses.w[3,1]

# Second simulation
nbPixels = 3

down2 = [1, 4]
up2 = [5, 0]
down3 = [3, 4]
up3 = [5, 2]
faux_positif = [3, 5]
up_down = [0, 3, 4]

# Movements
indices = up + down + down2 + up2 + down3 + up3 + up + faux_positif + up_down # Up - Down - Down - Up - Down - Up - Up
times = time + [i + j for j in range(2, 16, 2) for i in time] + [18, 18, 18]
times *= ms

inputTest = SpikeGeneratorGroup(nbPixels * nbPixelStates, indices, times)

### Output neurons
nbOutput = (nbPixels-1) * 2;

# Neurons model
eqsTest = '''
    dv/dt = -v/tLeak : volt
    thresh : volt'''

outputTest = NeuronGroup(nbOutput, eqsTest, threshold='v + dt*(v/tLeak) >= thresh', reset='v=reset')
outputTest.thresh = 2.900 * volt

### Synapses

synapsesModelTest = '''w : volt'''
preEqsTest = '''v = v + w'''
synapsesTest = Synapses(inputTest, target=outputTest, model=synapsesModelTest, pre=preEqsTest)

for i in range(nbPixels):
    if(i != nbPixels - 1):
        synapsesTest.connect([i*2, i*2, i*2+1, i*2+1], [i*2, i*2+1, i*2, i*2+1])
        synapsesTest.w[i*2, i*2] = synapses.w[0, 0] * 2
        synapsesTest.w[i*2, i*2+1] = synapses.w[0, 1] * 2
        synapsesTest.w[i*2+1, i*2] = synapses.w[1, 0] * 2
        synapsesTest.w[i*2+1, i*2+1] = synapses.w[1, 1] * 2
    for j in range(i):
        synapsesTest.connect([i*2, i*2, i*2+1, i*2+1], [j*2, j*2+1, j*2, j*2+1])
        synapsesTest.w[i*2, j*2] = synapses.w[2, 0]
        synapsesTest.w[i*2, j*2+1] = synapses.w[2, 1]
        synapsesTest.w[i*2+1, j*2] = synapses.w[3, 0]
        synapsesTest.w[i*2+1, j*2+1] = synapses.w[3, 1]

# Initialize synaptic weight with a gauss distribution
for i in range(nbPixels * nbPixelStates):
    for  j in range(nbOutput):
        synapses.w[i,j] = clip(
            gauss(wInitAverage, wInitDeviation),
            wMin,
            wMax)

print ''
print 'Simulation without learning'
timeRun = 20*ms

stateRecordTest = StateMonitor(outputTest, ('v'), record = True)

net = Network()
net.add(inputTest)
net.add(outputTest)
net.add(synapsesTest)
net.add(stateRecordTest)

net.run(timeRun, report='stdout')

# Display simulation plot
plot(stateRecordTest.t/ms, [outputTest.thresh[0] for i in range(len(stateRecordTest.t))], '--', label='threshold')
for i in range(nbOutput) :
    plot(stateRecordTest.t/ms, stateRecordTest.v[i]/volt, label=i)
legend()
show()

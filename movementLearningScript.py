from optparse import OptionParser
from brian2 import *
from random import gauss

### Parser
parser = OptionParser()
parser.add_option("-i", "--inhibition",
    help='''Specify inhibition time in ms. Required if not supervised.''')
parser.add_option("-l", "--leak",
    help='''Specify leak time in ms. Required.''')
parser.add_option("-n", "--number",
    help='''Specify number of learning test iterations.\r\n
        100 iterations by defaults, integers only.''',
    default=100)
parser.add_option("-r", "--refraction",
    help='''Specify refraction time in ms. Required.''')
parser.add_option("-s", "--supervised", action="store_true",
    help='''Specify the kind of learning (supervised or not). Value = True or False''',
    default=False)

(options, args) = parser.parse_args()

try :
    supervised = options.supervised

    if not supervised:
        tInhib = float(options.inhibition) * ms

    tLeak = float(options.leak) * ms
    tRefrac = float(options.refraction) * ms
    nIter = int(options.number)

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
time = [1, 1]

# Learning
indices = (down + up) * 20
times = time + [i + j for j in range(2, 80, 2) for i in time]

# Test for success
indices += (down + up) * 3
times += [i + j for j in range(90, 102, 2) for i in time]

times *= ms
input = SpikeGeneratorGroup(nbPixels * nbPixelStates, indices, times)

### Output neurons - We want to know if the movement is ascending or descending
nbOutput = 2

# threshold = 500*volt # Neurons send a spike when this threshold is reached
reset = 0*volt # Initial neurons value

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

output = NeuronGroup(nbOutput, eqs, threshold='v + dt*(v/tLeak) >= thresh',
    reset='v=reset', refractory='refrac')
output.refrac = tRefrac

### Synapses - Each input is linked to each output
wInitAverage = 0.800*volt # Initial synaptic weight values
wInitDeviation = 0.150*volt
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
                   ltpCondition = (tPost - tPre) >= (0 * second) and (tPost - tPre) <= tLTP : 1
                   apprentissage : 1'''

if not supervised:
    preEqs = '''tPre = t
                v = v * (t - lastInhib < tInhib and lastInhib != 0 * ms) + (v * exp(-(t-lastupdate)/tLeak) + w) * (t - lastInhib >= tInhib or lastInhib == 0 * ms)'''
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
    output.thresh = 1.000 * volt

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
timeRun = 110*ms
nbSuccess = 0
for i in range(nIter):
    print '''\r\n
        Simulation {}
        \r\n'''.format(i)
    run(timeRun, report='stdout')

    # Verify if the system has learned the pattern
    learned = True
    if(len(record.i) < 4):
        print len(record.i)
        learned = False
    else:
        for i in range(1, 5):
            print(record.i[len(record.i) - i], " ", record.t[len(record.t) - i])
            if(record.i[len(record.i) - i] == record.i[len(record.i) - (i+1)] or
                    record.t[len(record.t) - i] == record.t[len(record.t) - (i+1)]):
                learned = False

    if(learned):
        nbSuccess = nbSuccess + 1

    # Restore for next iteration
    restore()

    # Re-initialize synaptic weight with a gauss distribution
    if(not supervised):
        for i in range(nbPixels * nbPixelStates):
            for  j in range(nbOutput):
                synapses.w[i,j] = clip(
                    gauss(wInitAverage, wInitDeviation),
                    wMin,
                    wMax)

# Results
print ''
print 'Configuration :'
print ''
print ''
print '* Leak = ', tLeak
print '* Refraction = ', tRefrac
if not supervised:
    print '* Inhibition = ', tInhib
print ''
print ''
print '* Init weight = ', wInitAverage
print '* Init weight deviation = ', wInitDeviation
print '* Max weight = ', wMax
print '* Min weight = ', wMin
print ''
print ''
print '* LTP = ', tLTP
print '* a (Post) = ', aPost
print '* b (Post) = ', bPost
print '* a (Pre) = ', aPre
print '* b (Pre) = ', bPre
print ''
print ''
print '* Number of iterations = ', nIter
print '* Success count = ', nbSuccess

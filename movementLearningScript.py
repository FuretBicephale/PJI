from optparse import OptionParser
from brian2 import *
from random import gauss

### Parser
parser = OptionParser()
parser.add_option("-i", "--inhibition",
    help='''Specify inhibition time in ms. Required.''')
parser.add_option("-l", "--leak",
    help='''Specify leak time in ms. Required.''')
parser.add_option("-n", "--number",
    help='''Specify number of learning test iterations.\r\n
        100 iterations by defaults, integers only.''',
    default=100)
parser.add_option("-r", "--refraction",
    help='''Specify refraction time in ms. Required.''')

(options, args) = parser.parse_args()

try :
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
down = [0, 1, 2, 3]
up = [2, 3, 0, 1]
time = [1, 2, 2, 3] # One movement last 2 seconds

# Learning
indices = down * 20 + up * 20
times = time + [i + j for j in range(5, 200, 5) for i in time] # 3 seconds between 2 movements

# Test for success
indices += (down + up) * 3
times += [i + j for j in range(210, 240, 5) for i in time]

times *= ms
input = SpikeGeneratorGroup(nbPixels * nbPixelStates, indices, times)

### Output neurons - We want to know if the movement is ascending or descending
nbOutput = 2;

# Neurons model
eqs = '''dv/dt = -v/tLeak : volt (unless refractory)
         refrac : second
         lastInhib : second'''

threshold = 500*volt # Neurons send a spike when this threshold is reached
reset = 0*volt # Initial neurons value

output = NeuronGroup(nbOutput, eqs, threshold='v>=threshold', reset='v=reset', refractory='refrac')
output.refrac = tRefrac

### Synapses - Each input is linked to each output
wInitAverage = 500*volt # Initial synaptic weight values
wInitDeviation = 150*volt
wMax = 1000*volt # Maximum Synaptic weight
wMin = 1*volt # Minimum synaptic weight

aPre = 100*volt # Alpha values for presynaptics spikes
aPost = 50*volt # Apha values for postsynaptics spikes
bPre = 0*volt # Beta values for presynaptics spikes
bPost = 0*volt # Beta values for postsynaptics spikes

tLTP = 2*ms # Maximum time between post and pre spikes to launch a LTP

# ltpCondition is true if the synapse deals with a Potentiation, false if it's a Depression
synapsesModel = '''w : volt
                   dwPre = aPre * exp(-bPre*(w-wMin/wMax-wMin)) : volt
                   dwPost = aPost * exp(-bPost*(wMax-w/wMax-wMin)) : volt
                   tPre : second
                   tPost : second
                   ltpCondition = (tPost - tPre) >= (0 * second) and (tPost - tPre) <= tLTP : 1
                   apprentissage : 1'''
preEqs = '''tPre = t
            v = v * (t - lastInhib < tInhib and lastInhib != 0 * ms) + (v * exp(-(t-lastupdate)/tLeak) + w) * (t - lastInhib >= tInhib or lastInhib == 0 * ms)
            refrac = tRefrac * int(not_refractory) + refrac * (1 - int(not_refractory))'''
# If ltpCondition is False then it's equals to 0, 1 otherwise
# So dwPre * (ltpCondition) = 0 if ltpCondition is false, dwPre otherwise
# And dwPost * (ltpCondition != 1) = 0 if ltpCondition is true (== 0), dwPost otherwise
postEqs = '''tPost = t
             w = clip(w + dwPre * ltpCondition * apprentissage, wMin, wMax)
             w = clip(w - dwPost * (ltpCondition == 0) * apprentissage, wMin, wMax)'''
synapses = Synapses(input, target=output, model=synapsesModel, pre=preEqs, post=postEqs)
synapses.connect(True) # Connecting every neurons of the first layer to every neurons of the second one

# Initialize synaptic weight with a gauss distribution
for i in range(nbPixels * nbPixelStates):
    for  j in range(nbOutput):
        synapses.w[i,j] = clip(
            gauss(wInitAverage, wInitDeviation),
            wMin,
            wMax)

# Inhibition
inhibition = Synapses(output, model='w : volt', pre='lastInhib = t * int(not_refractory)')
inhibition.connect("i != j") # Every neurons of the layer are connected to each other
inhibition.w = wInitAverage

# Monitor
record = SpikeMonitor(output) # Record output layer spikes

# Save the state of the network
store()

# Run
timeRun = 240*ms
nbSuccess = 0
for i in range(nIter):
    print '''\r\n
        Simulation {}
        \r\n'''.format(i)
    run(timeRun, report='stdout')

    # Verify if the system has learned the pattern
    learned = True
    for i in range(1, 5):
        if(record.i[len(record.i) - i] == record.i[len(record.i) - (i+1)] or
                record.t[len(record.t) - i] == record.t[len(record.t) - (i+1)]):
            learned = False

    if(learned):
        nbSuccess = nbSuccess + 1

    # Restore for next iteration
    restore()

    # Re-initialize synaptic weight with a gauss distribution
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
print '* Threshold = ', threshold
print '* Reset = ', reset
print ''
print ''
print '* Leak = ', tLeak
print '* Refraction = ', tRefrac
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

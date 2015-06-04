from optparse import OptionParser
from random import randint, gauss

from brian2 import *

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
parser.add_option("--ltp",
    help='''Specify ltp time in ms. Required.''')
parser.add_option("-t", "--threshold",
    help='''Specify threshold value in volt. Required.''')

(options, args) = parser.parse_args()

try :
    tInhib = float(options.inhibition) * ms
    tLeak = float(options.leak) * ms
    tRefrac = float(options.refraction) * ms
    nIter = int(options.number)
    tLTP = float(options.ltp) * ms
    threshold = float(options.threshold) * volt

except :
    print "Error : Invalid argument. See help for more informations."
    parser.print_help()
    exit(False)

### Input neurons - 2 pixels with 2 states (ON/OFF).
nbPixels = 4;
nbPixelStates = 2;

# Movements
up = [7, 4] + [i - j for j in range(2, (nbPixels - 1) * 2, 2) for i in [7, 4]]
down = [1, 2] + [i + j for j in range(2, (nbPixels - 1) * 2, 2) for i in [1, 2]]
time = [1, 1, 3, 3, 5, 5]

# Learning
nbMotifs = 500
indices = []
times = time + [i + j for j in range(10, nbMotifs * 10, 10) for i in time]
for i in range(nbMotifs):
    motif = randint(0, 2)
    if i % 2 == 0:
        indices += up
    else:
        indices += down

indices += up + down
new_times = [[times[len(times) - 1] + i] * 2 for i in range(20, 26, 2)] + [[times[len(times) - 1] + i] * 2 for i in range(40, 46, 2)]
times += [i for sublist in new_times for i in sublist]
times *= ms

input = SpikeGeneratorGroup(nbPixels * nbPixelStates, indices, times)

### Output neurons - We want to know if the movement is ascending or descending
nbOutput = (nbPixels - 1) * 2

# Neurons model
eqs = '''dv/dt = -v/tLeak : volt (unless refractory)
         lastInhib : second'''

output = NeuronGroup(nbOutput, eqs, threshold='v > threshold',
    reset='v = 0*volt', refractory=tRefrac)

### Synapses - Each input is linked to each output
wInitAverage = 0.800*volt # Initial synaptic weight values
wInitDeviation = 0.150*volt
wMax = 1.000*volt # Maximum Synaptic weight
wMin = 0.000*volt # Minimum synaptic weight

aPre = 0.100*volt # Alpha values for presynaptics spikes
aPost = 0.050*volt # Apha values for postsynaptics spikes
bPre = 0*volt # Beta values for presynaptics spikes
bPost = 0*volt # Beta values for postsynaptics spikes

# ltpCondition is true if the synapse deals with a Potentiation, false if it's a Depression
synapsesModel = '''w : volt
                   dwPre = aPre * exp(-bPre*(w-wMin/wMax-wMin)) : volt
                   dwPost = aPost * exp(-bPost*(wMax-w/wMax-wMin)) : volt
                   tPre : second
                   tPost : second
                   ltpCondition = tPost > tPre and (tPost - tPre) <= tLTP : 1'''

preEqs = '''tPre = t
            v = v * (t - lastInhib < tInhib and lastInhib != 0 * ms) + (v + w) * (t - lastInhib >= tInhib or lastInhib == 0 * ms)'''

# If ltpCondition is False then it's equals to 0, 1 otherwise
# So dwPre * (ltpCondition) = 0 if ltpCondition is false, dwPre otherwise
# And dwPost * (ltpCondition != 1) = 0 if ltpCondition is true (== 0), dwPost otherwise
postEqs = '''tPost = t
             w = clip(w + dwPre * (tPre != 0 * second and ltpCondition), wMin, wMax)
             w = clip(w - dwPost * (tPre == 0 * second or ltpCondition == 0), wMin, wMax)'''
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
inhibition = Synapses(output, target=output, model='', pre='''
    lastInhib = t''')
inhibition.connect("i != j") # Every neurons of the layer are connected to each other

# Monitors
record = SpikeMonitor(output) # Record output layer spikes
recordInput = SpikeMonitor(input) # Record input layer spikes
stateRecord = StateMonitor(output, 'v', record = True) # Record the state of each neurons of the output layer
synapsesRecord = StateMonitor(synapses, 'w', record = True)

# Run
print ''
timeRun = times[len(times) - 1] + 10*ms
run(timeRun, report='stdout')

# print ''
# print 'First layer'
# print 'count = ', record.count
# print 'spikes = ', record.num_spikes
# print record.it
#
# print ''
# print 'Input'
# print 'count = ', recordInput.count
# print 'spikes = ', recordInput.num_spikes
# print recordInput.it

# Display simulation plot
# figure(1)
# for i in range(nbOutput) :
#     subplot(2, 4, i+1)
#     plot(stateRecord.t/ms, [threshold] * len(stateRecord.t), '--', label='threshold')
#     plot(stateRecord.t/ms, stateRecord.v[i]/volt, label=i)
#     legend()

# figure(2)
plot(stateRecord.t/ms, [threshold for i in range(len(stateRecord.t))], '--', label='threshold')
for i in range(nbOutput) :
    plot(stateRecord.t/ms, stateRecord.v[i]/volt, label=i)
legend()

# figure(3)
# for j in range(nbOutput):
#     subplot(2, 4, j+1)
#     for i in range(nbPixels * nbPixelStates):
#         plot(synapsesRecord.t/ms, synapsesRecord.w[i * nbOutput + j]/volt, label=i * nbOutput + j)
#     legend()
show()

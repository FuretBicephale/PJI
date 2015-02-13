from brian2 import *

# Input neurons
indices = range(4) * 2 # 4 neurons
times = [time/2.0 for time in range(1, 9)] * ms # Each neurons generate a spike at i ms (i = neurons index)
input = SpikeGeneratorGroup(4, indices, times)

# Neurones
nbPx = 4 # Number of pixels on the image
nbNeuronsPerPx = 1 # Number of neurons per pixel
N = nbPx * nbNeuronsPerPx # Total number of neurons
tLeak = 5*ms
eqs = 'dv/dt = -v/tLeak : volt' # Neurons model
threshold = 800*volt # Neurons send a spike when this threshold is reached
reset = 0*volt # Initial neurons value

firstLayer = NeuronGroup(N, eqs, threshold='v>=threshold', reset='v=reset')

# Synapses
wInit = 800*volt # Initial synaptic weight values
wMax = 1000*volt # Maximum Synaptic weight
wMin = 1*volt # Minimum synaptic weight

aPre = 100*volt # Alpha values for presynaptics spikes
aPost = 50*volt # Apha values for postsynaptics spikes
bPre = 0*volt # Beta values for presynaptics spikes
bPost = 0*volt # Beta values for postsynaptics spikes

tRefrac = 10*ms # Minimum time between two presynaptics spikes
tInhib = 1.5*ms # Minimum time before an inhibited spike can receive presynaptics spikes agains
tTLP = 2*ms # Maximum time between post and pre spikes to launch a LTP

synapsesModel = '''w : volt
                   dwPre = aPre * exp(-bPre*(w-wMin/wMax-wMin)) : volt
                   dwPost = aPost * exp(-bPost*(wMax-w/wMax-wMin)) : volt
                   tPre : second
                   tPost : second
                   ltpCondition = (tPost - tPre) >= (0 * second) and (tPost - tPre) <= tTLP : 1'''
preEqs = '''tPre = t
            v = v * exp(-(t-lastupdate)/tLeak) + w'''
postEqs = '''tPost = t
             w = w + dwPre * (ltpCondition)
             w = w - dwPost * (ltpCondition != 1)'''
synapses = Synapses(input, target=firstLayer, model=synapsesModel, pre=preEqs, post=postEqs)
synapses.connect('i == j') # Connect each neuron of the input layer to the same index neuron of the output layer
synapses.w = wInit # Initialize synaptic weight

# Inhibition
inhibition = Synapses(firstLayer)
# For each pixel of the image, we link every neurons of this pixel with inhibitory synapses
for n in xrange(0, N, nbNeuronsPerPx):
    neuronsOfPx = range(n, n + nbNeuronsPerPx)
    # We connect each neurons between the first neuron of the pixel and the last one
    inhibition.connect('i != j and n <= i and i < nbNeuronsPerPx and n <= j and j < nbNeuronsPerPx')

# Monitor
record = SpikeMonitor(firstLayer) # Record output layer spikes
recordInput = SpikeMonitor(input) # Record input layer spikes
stateRecord = StateMonitor(firstLayer, 'v', record = True) # Record the state of each neurons of the output layer
synapsesRecord = StateMonitor(synapses, True, record = True) # Record the state of each synapses

# Run
print ''
run(5*ms, report='stdout')

# End
print ''
print 'First layer'
print 'count = ', record.count
print 'spikes = ', record.num_spikes
print record.it

print ''
print 'Input'
print 'count = ', recordInput.count
print 'spikes = ', recordInput.num_spikes
print recordInput.it

print ''
print 'First layer state'
print 'v = ', stateRecord.v


print ''
print 'Synapses state'
print 'w = ', synapsesRecord.w
# print 'dwPre = ', synapsesRecord.dwPre
# print 'dwPost = ', synapsesRecord.dwPost

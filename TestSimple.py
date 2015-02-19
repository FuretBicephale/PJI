from brian2 import *

# Input neurons
indices = range(4) * 3 # 4 neurons
times = [time/2.0 for time in range(1, 13)] * ms # Each neurons generate a spike at i ms (i = neurons index)
input = SpikeGeneratorGroup(4, indices, times)

# Neurones
nbPx = 4 # Number of pixels on the image
nbNeuronsPerPx = 1 # Number of neurons per pixel
N = nbPx * nbNeuronsPerPx # Total number of neurons

tLeak = 5*ms # Leak time
tRefrac = 10*ms # Minimum time between two presynaptics spikes
tInhib = 1.5*ms # Minimum time before an inhibited spike can receive presynaptics spikes agains

eqs = '''dv/dt = -v/tLeak : volt (unless refractory)
         refrac : second''' # Neurons model
threshold = 800*volt # Neurons send a spike when this threshold is reached
reset = 0*volt # Initial neurons value

firstLayer = NeuronGroup(N, eqs, threshold='v>=threshold', reset='v=reset', refractory='refrac')
firstLayer.refrac = tRefrac

# Synapses
wInit = 800*volt # Initial synaptic weight values
wMax = 1000*volt # Maximum Synaptic weight
wMin = 1*volt # Minimum synaptic weight

aPre = 100*volt # Alpha values for presynaptics spikes
aPost = 50*volt # Apha values for postsynaptics spikes
bPre = 0*volt # Beta values for presynaptics spikes
bPost = 0*volt # Beta values for postsynaptics spikes

tTLP = 2*ms # Maximum time between post and pre spikes to launch a LTP

# ltpCondition is true if the synapse deal with a Potentiation, false if it's a Depression
synapsesModel = '''w : volt
                   dwPre = aPre * exp(-bPre*(w-wMin/wMax-wMin)) : volt
                   dwPost = aPost * exp(-bPost*(wMax-w/wMax-wMin)) : volt
                   tPre : second
                   tPost : second
                   ltpCondition = (tPost - tPre) >= (0 * second) and (tPost - tPre) <= tTLP : 1'''
preEqs = '''tPre = t
            v = v * exp(-(t-lastupdate)/tLeak) + w
            refrac = tRefrac * int(not_refractory) + refrac * (1 - int(not_refractory))'''
# If ltpCondition is False then it's equals to 0, 1 otherwise
# So dwPre * (ltpCondition) = 0 if ltpCondition is false, dwPre otherwise
# And dwPost * (ltpCondition != 1) = 0 if ltpCondition is true (== 0), dwPost otherwise
postEqs = '''tPost = t
             w = clip(w + dwPre * (ltpCondition), wMin, wMax)
             w = clip(w - dwPost * (ltpCondition != 1), wMin, wMax)'''
synapses = Synapses(input, target=firstLayer, model=synapsesModel, pre=preEqs, post=postEqs)
synapses.connect('i == j') # Connect each neuron of the input layer to the same index neuron of the output layer
synapses.w = wInit # Initialize synaptic weight

# Inhibition
inhibition = Synapses(firstLayer, pre='refrac = tInhib * int(not_refractory) + refrac * (1 - int(not_refractory))')
inhibition.connect('i != j')
# For each pixel of the image, we link every neurons of this pixel with inhibitory synapses
# for n in xrange(0, N, nbNeuronsPerPx):
    # neuronsOfPx = range(n, n + nbNeuronsPerPx)
    # We connect each neurons between the first neuron of the pixel and the last one
    # inhibition.connect('i != j and n <= i and i < nbNeuronsPerPx and n <= j and j < nbNeuronsPerPx')

# Monitor
record = SpikeMonitor(firstLayer) # Record output layer spikes
recordInput = SpikeMonitor(input) # Record input layer spikes
stateRecord = StateMonitor(firstLayer, ('v', 'refrac'), record = True) # Record the state of each neurons of the output layer
synapsesRecord = StateMonitor(synapses, ('w', 'dwPre', 'dwPost'), record = True) # Record the state of each synapses

# Run
print ''
run(10*ms, report='stdout')

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

# print ''
# print 'Synapses state'
# print 'w = ', synapsesRecord.w
# print 'dwPre = ', synapsesRecord.dwPre
# print 'dwPost = ', synapsesRecord.dwPost

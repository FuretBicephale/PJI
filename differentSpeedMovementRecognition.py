import os, pickle, genParser, genInput, genLayer, genGraph
from brian2 import *

prefs['codegen.target'] = 'numpy'

# Input
nbPixels = 7
nbPixelStates = 2
nbPatterns = 2 * 600
input = genInput.genAlternateVerticalMovementsAlternateSpeed(nbPixels, nbPixelStates, nbPatterns, 0)

layer = genLayer.genNeurons((nbPixels - 1) * 3)
layer.thresh = 1*volt
layer.tLeak = 1*ms
layer.tRefrac = (2 * (2 * (nbPixels-2) + max(0, ((nbPixels-3)/2)*2)) + 30) * ms
layer.tInhib = 1*ms

print layer.tRefrac

wAverage = 0.800*volt
wDeviation = 0.150*volt
wMax = 1.000*volt
wMin = 0.001*volt

aPre = 0.05*volt
aPost = 0.025*volt
bPre = 0*volt
bPost = 0*volt

synapses = genLayer.genSynapses(input, nbPixels*nbPixelStates, layer,
    (nbPixels - 1) * 4, True, wAverage, wDeviation, wMin, wMax)
synapses.tLTP = 1*ms

inhibition = genLayer.genInhibition(layer)

# Monitors
stateRecord = StateMonitor(layer, ('v', 'thresh', 'deltaThresh'), record = True) # Record the state of each neurons of the layer layer
recordInput = SpikeMonitor(input) # Record input layer spikes
spikeLayer = SpikeMonitor(layer)

net = Network()
net.add(input)
net.add(layer)
net.add(synapses)
net.add(inhibition)
net.add(stateRecord)
net.add(recordInput)
net.add(spikeLayer)

timeRun = (nbPatterns/2 * (3 * (nbPixels-2) + 19) - 4) * ms
print timeRun

# Run
print ''
net.run(timeRun/2, report='stdout')

plot(zeros(nbPixels*nbPixelStates), arange(nbPixels*nbPixelStates), 'ok', ms=10)
genGraph.visualise_synapses(synapses, 0, 1)
show()

genGraph.visualise_spike(spikeLayer)

layer.apprentissage = 0
layer.thresh -= 0.1*volt
# layer.tRefrac = 0 * ms

output = genLayer.genNeurons(4)
output.thresh = 1.5 * volt
output.tLeak = (nbPixels-1) * ms
output.tRefrac = (2 * (nbPixels-2) + 2 * max(0, ((nbPixels-3)/2)*2) + 30) * ms
output.tInhib = 9 * ms

synapsesOutput = genLayer.genSynapses(layer, (nbPixels - 1) * 3, output,
    4, True, wAverage, wDeviation, wMin, wMax)
synapsesOutput.tLTP = (2 * (nbPixels - 2) + 1) * ms

inhibitionOutput = genLayer.genInhibition(output)

# Monitors
stateRecordOutput = StateMonitor(output, ('v', 'thresh', 'deltaThresh'), record = True) # Record the state of each neurons of the layer layer
spikeLayerOutput = SpikeMonitor(output)

net.add(output)
net.add(synapsesOutput)
net.add(inhibitionOutput)
net.add(stateRecordOutput)
net.add(spikeLayerOutput)

# input = genInput.genAlternateVerticalMovementsAlternateSpeed(nbPixels, nbPixelStates, nbPatterns * 2)

# Run
print ''
net.run(timeRun/2, report='stdout')

genGraph.visualise_network([synapses, synapsesOutput])
genGraph.visualise_spike(spikeLayerOutput)

output.apprentissage = 0
output.thresh = output.lastSuccessfulThresh - 0.4*volt
output.deltaThresh = 0*volt
# output.tRefrac = 0 * ms

patterns = genInput.createPatterns(nbPixels, 1)
patterns2 = genInput.createPatterns(nbPixels, 2)
indexes = []
time = [i + j for j in range(0, (nbPixels - 1) * 2, 2) for i in[1, 1]]
time += [i + j for j in range((nbPixels - 1) * 2 + 8, (nbPixels - 1) * 3 + 8, 2) for i in[1, 1]]

pattern_length = time[len(time) - 1] + 9
times = time + [i + j for j in range(pattern_length, 6 * pattern_length, pattern_length) for i in time]

indexes += patterns['up']
indexes += patterns2['up']
indexes += patterns['down']
indexes += patterns2['down']

i = len(indexes)
indexes += patterns['up']
del indexes[i]
del times[i]

i = len(indexes)
indexes += patterns2['up']
del indexes[i]
del times[i]

i = len(indexes)
indexes += patterns['down']
del indexes[i]
del times[i]

i = len(indexes)
indexes += patterns2['down']
del indexes[i]
del times[i]

i = len(indexes)
indexes += patterns['up']
del indexes[i]
del indexes[i]
del times[i]
del times[i]

i = len(indexes)
indexes += patterns2['up']
del indexes[i]
del indexes[i]
del times[i]
del times[i]

i = len(indexes)
indexes += patterns['down']
del indexes[i]
del indexes[i]
del times[i]
del times[i]

i = len(indexes)
indexes += patterns2['down']
del indexes[i]
del indexes[i]
del times[i]
del times[i]

input.set_spikes(indexes, times * ms + timeRun)

print ''
print 'Without learning'
net.run(6 * pattern_length * ms, report='stdout')

figure(1)
for j in range(len(stateRecord.v)) :
    plot(stateRecord.t/ms, (stateRecord.thresh[j] + stateRecord.deltaThresh[j])/volt, '--', label='threshold')
    plot(stateRecord.t/ms, stateRecord.v[j]/volt, label=j)

legend()

figure(2)
for j in range(len(stateRecordOutput.v)) :
    plot(stateRecordOutput.t/ms, (stateRecordOutput.thresh[j] + stateRecordOutput.deltaThresh[j])/volt, '--', label='threshold')
    plot(stateRecordOutput.t/ms, stateRecordOutput.v[j]/volt, label=j)

legend()
show()
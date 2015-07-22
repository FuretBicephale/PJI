import os, pickle, genParser, genInput, genLayer, genGraph
from brian2 import *

prefs['codegen.target'] = 'numpy'

# Input
nbPixels = 6
nbPixelStates = 2
nbPatterns = 4 * 300
input = genInput.genTwoColumnsMovements(nbPixels, nbPixelStates, nbPatterns, 0)

layer = genLayer.genNeurons(nbPixels - 2)
layer.thresh = 1*volt
layer.tLeak = 0.5*ms
layer.tRefrac = ((nbPixels - 4) * 2 + 9) * ms
layer.tInhib = 1*ms

wAverage = 0.800*volt
wDeviation = 0.150*volt
wMax = 1.000*volt
wMin = 0.001*volt

aPre = 0.1*volt
aPost = 0.05*volt
bPre = 0*volt
bPost = 0*volt

synapses = genLayer.genSynapses(input, nbPixels*nbPixelStates, layer,
    nbPixels - 2, True, wAverage, wDeviation, wMin, wMax)
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

timeRun = (nbPatterns * (nbPixels - 4 + 5)) * ms
print timeRun

# Run
print ''
net.run(timeRun/3, report='stdout')

plot(zeros(nbPixels*nbPixelStates), arange(nbPixels*nbPixelStates), 'ok', ms=10)
genGraph.visualise_synapses(synapses, 0, 1)
show()

genGraph.visualise_spike(spikeLayer)

layer.apprentissage = 0
layer.thresh = layer.lastSuccessfulThresh
layer.deltaThresh = 0*volt
# layer.tRefrac = 0 * ms

output = genLayer.genNeurons(2)
output.thresh = 1.5 * volt
output.tLeak = (nbPixels-1) * ms
output.tRefrac = (nbPixels - 4 + 5) * ms
output.tInhib = 4 * ms

synapsesOutput = genLayer.genSynapses(layer, nbPixels - 2, output,
    2, True, wAverage, wDeviation, wMin, wMax)
synapsesOutput.tLTP = (nbPixels - 4 + 1) * ms

inhibitionOutput = genLayer.genInhibition(output)

# Monitors
stateRecordOutput = StateMonitor(output, ('v', 'thresh', 'deltaThresh'), record = True) # Record the state of each neurons of the layer layer
spikeLayerOutput = SpikeMonitor(output)

net.add(output)
net.add(synapsesOutput)
net.add(inhibitionOutput)
net.add(stateRecordOutput)
net.add(spikeLayerOutput)

input = genInput.genAlternateVerticalMovementsAlternateSpeed(nbPixels, nbPixelStates, nbPatterns * 2)

# Run
print ''
net.run(timeRun/3, report='stdout')

genGraph.visualise_network([synapses, synapsesOutput])
genGraph.visualise_spike(spikeLayerOutput)

output.apprentissage = 0
output.thresh = output.lastSuccessfulThresh
output.deltaThresh = 0*volt
# output.tRefrac = 0 * ms

input = genInput.genAlternateVerticalMovementsAlternateSpeed(nbPixels, nbPixelStates, nbPatterns * 3)

print ''
print 'Without learning'
net.run(timeRun/3, report='stdout')

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
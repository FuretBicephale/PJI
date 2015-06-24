import os, pickle, genParser, genInput, genLayer
from brian2 import *

# # Parser
# parser = genParser.genParser()
# args = genParser.getArgs(parser)
# tInhib = args['tInhib']
# tLeak = args['tLeak']
# tRefrac = args['tRefrac']
# tLTP = args['tLTP']
# threshold = args['threshold']

# Input
nbPixels = 7
nbPixelStates = 2
nbPatterns = 100
input = genInput.genAlternateVerticalMovements(nbPixels, nbPixelStates, nbPatterns)
# if args['randomPattern']:
#     input = genInput.genRandomVerticalMovements(nbPixels, nbPixelStates, nbPatterns)
# else:
#     input = genInput.genAlternateVerticalMovements(nbPixels, nbPixelStates, nbPatterns)

layer = genLayer.genNeurons((nbPixels - 1) * 2)
layer.thresh = 1.1*volt
layer.tLeak = 0.5*ms
layer.tRefrac = (2 * ((nbPixels-1) * 2 + 4) - 1) * ms
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
    (nbPixels - 1) * 2, True, wAverage, wDeviation, wMin, wMax)
synapses.tLTP = 1*ms

inhibition = genLayer.genInhibition(layer)

# Monitors
stateRecord = StateMonitor(layer, ('v', 'thresh'), record = True) # Record the state of each neurons of the layer layer
recordInput = SpikeMonitor(input) # Record input layer spikes
# record = SpikeMonitor(layer) # Record layer layer spikes
# synapsesRecord = StateMonitor(synapses, 'w', record = True)

net = Network()
net.add(input)
net.add(layer)
net.add(synapses)
net.add(inhibition)
net.add(stateRecord)
net.add(recordInput)

timeRun = (nbPatterns * 10 + 10)/4 * ms

# Run
print ''
# print 'Simulation {} - {}'.format(i+1, i * timeRun/40)
net.run(timeRun, report='stdout')

# Synapses weight save
# try:
#     folderPath = os.getcwd() + "/weights"
#     if not os.path.exists(folderPath):
#         os.mkdir(folderPath)
#     assert os.path.isdir(folderPath)
# except:
#     print "Erreur lors de la creation du dossier de sauvegarde"
#     exit(14)
#
# nameTemp = folderPath + "/file" + ("%04d"%(i,)) + ".spw"
# wi = []
# for wn in synapses.w:
#     wi.append(wn)
# with open(nameTemp, 'wb') as fichier:
#     mon_pick = pickle.Pickler(fichier)
#     mon_pick.dump(wi)

# Display simulation plot

# figure(1)
# for i in range((nbPixels - 1) * 2) :
#     plot(stateRecord.t/ms, stateRecord.thresh[i]/volt, '--', label='threshold {}'.format(i))
#     plot(stateRecord.t/ms, stateRecord.v[i]/volt, label=i)
# legend()
#
# show()

layerTab = []
synapsesTab = []
inhibitionTab = []
stateRecordTab = []

layerTab.append(layer)
synapsesTab.append(synapses)
inhibitionTab.append(inhibition)
stateRecordTab.append(stateRecord)

nbNeurons = (nbPixels - 1) * 2
need2SynapsesGroup = False
nextNeed2SynapsesGroup = False
i = 1

while(nbNeurons != 4 and (nbNeurons != 2 or not nextNeed2SynapsesGroup)):

    previousNbNeurons = nbNeurons
    need2SynapsesGroup = nextNeed2SynapsesGroup

    if(nbNeurons % 4 == 0):
        nbNeurons /= 2
        nextNeed2SynapsesGroup = False
    else:
        nbNeurons = (nbNeurons-2) / 2
        nextNeed2SynapsesGroup = True

    layerTab.append(genLayer.genNeurons(nbNeurons))
    layerTab[i].thresh = 1.1*volt
    layerTab[i].tLeak = layerTab[i-1].tLeak[0] + 2*ms
    layerTab[i].tRefrac = layerTab[i-1].tRefrac[0] - 2*ms
    layerTab[i].tInhib = 1*ms

    synapsesTab.append(genLayer.genSynapses(layerTab[i-1], previousNbNeurons,
        layerTab[i], nbNeurons, True, wAverage, wDeviation, wMin, wMax))
    synapsesTab[i].tLTP = synapsesTab[i-1].tLTP[0] + 2*ms

    if(need2SynapsesGroup):
        layerTab[i].activated = 0
        synapsesTab.append(genLayer.genSynapses(layerTab[i-2], previousNbNeurons*2 + 2,
            layerTab[i], nbNeurons, True, wAverage, wDeviation, wMin, wMax, needActivation=True))
        synapsesTab[i].tLTP = synapsesTab[i-1].tLTP[0] + 2*ms

    inhibitionTab.append(genLayer.genInhibition(layerTab[i]))
    stateRecordTab.append(StateMonitor(layerTab[i], ('v', 'thresh'), record = True))

    net.add(layerTab[i])
    net.add(synapsesTab[i])
    net.add(inhibitionTab[i])
    net.add(stateRecordTab[i])

    print ''
    print 'layer {} learning'.format(i+1)
    net.run(timeRun, report='stdout')
    i += 1

# layer_2 = genLayer.genNeurons(2)
# layer_2.thresh = 1.1*volt
# layer_2.tLeak = 3*ms
# layer_2.tRefrac = 17*ms
# layer_2.tInhib = 1*ms
#
# synapses_2 = genLayer.genSynapses(layer, (nbPixels - 1) * 2, layer_2, 2, True,
#     wAverage, wDeviation, wMin, wMax)
#
# synapses_2.tLTP = 3 * ms
#
# inhibitions_2 = genLayer.genInhibition(layer_2)
#
# stateRecord_2 = StateMonitor(layer_2, ('v', 'thresh'), record = True)
#
# net.add(layer_2)
# net.add(synapses_2)
# net.add(inhibitions_2)
# net.add(stateRecord_2)

# print ''
# print 'Second layer learning'
# net.run(timeRun, report='stdout')

# figure(2)
# for i in range(2) :
#     plot(stateRecord_2.t/ms, stateRecord_2.thresh[i]/volt, '--', label='threshold {}'.format(i))
#     plot(stateRecord_2.t/ms, stateRecord_2.v[i]/volt, label=i)
# legend()
#
# show()

output = genLayer.genNeurons(2)
output.thresh = 1.1*volt
output.tLeak = layerTab[len(layerTab)-1].tLeak + 2*ms
output.tRefrac = layerTab[len(layerTab)-1].tRefrac - 2*ms
output.tInhib = 5*ms

synapses_output = genLayer.genSynapses(layerTab[len(layerTab)-1], nbNeurons, output,
    2, True, wAverage, wDeviation, wMin, wMax)
synapses_output.tLTP = synapsesTab[len(synapsesTab)-1].tLTP[0] + 2*ms

if(nextNeed2SynapsesGroup):
    output.activated = 0
    synapses_output_2 = genLayer.genSynapses(layerTab[len(layerTab)-2],
        nbNeurons*2 + 2, output, 2, True, wAverage, wDeviation, wMin, wMax, needActivation=True)
    synapses_output_2.tLTP = synapsesTab[len(synapsesTab)-1].tLTP[0] + 2*ms
    net.add(synapses_output_2)

inhibition_output = genLayer.genInhibition(output)

stateRecord_output = StateMonitor(output, ('v', 'thresh'), record = True)

net.add(output)
net.add(synapses_output)
net.add(inhibition_output)
net.add(stateRecord_output)

print ''
print 'Last layer learning'
net.run(timeRun, report='stdout')

# figure(2)
# for i in range(2) :
#     plot(stateRecord_2.t/ms, stateRecord_2.thresh[i]/volt, '--', label='threshold {}'.format(i))
#     plot(stateRecord_2.t/ms, stateRecord_2.v[i]/volt, label=i)
# legend()
#
# show()

# layer.tRefrac = 0*ms
# layer.tInhib = 0*ms
# inhibition.connect(False)

# layer_2.tRefrac = 0*ms
# layer_2.tInhib = 0*ms
# inhibitions_2.connect(False)

for i in range(len(layerTab)):
    layerTab[i].tRefrac = 0*ms
    layerTab[i].tInhib = 0*ms
    inhibitionTab[i].connect(False)

output.tRefrac = 0*ms
output.tInhib = 0*ms
inhibition_output.connect(False)

print ''
print 'Without learning'
net.run(timeRun * 4, report='stdout')

for i in range(len(layerTab)):
    figure(i)
    plot(stateRecordTab[i].t/ms, stateRecordTab[i].thresh[0]/volt, '--', label='threshold')
    for j in range(len(stateRecordTab[i].v)) :
        plot(stateRecordTab[i].t/ms, stateRecordTab[i].v[j]/volt, label=j)
    legend()

figure(len(layerTab))
plot(stateRecord_output.t/ms, stateRecord_output.thresh[0]/volt, '--', label='threshold')
for i in range(2) :
    plot(stateRecord_output.t/ms, stateRecord_output.v[i]/volt, label=i)
legend()

show()

# figure(3)
# for i in range(nbOutput) :
#     subplot(2, 4, i+1)
#     plot(stateRecord.t/ms, [threshold] * len(stateRecord.t), '--', label='threshold')
#     plot(stateRecord.t/ms, stateRecord.v[i]/volt, label=i)
#     legend()

# figure(4)
# plot(stateRecord_2.t/ms, [threshold for i in range(len(stateRecord_2.t))], '--', label='threshold')
# for i in range(2) :
#     plot(stateRecord_2.t/ms, stateRecord_2.v[i]/volt, label=i)
# legend()

# figure(5)
# for j in range(nbOutput):
#     subplot(2, 4, j+1)
#     for i in range(nbPixels * nbPixelStates):
#         plot(synapsesRecord.t/ms, synapsesRecord.w[i * nbOutput + j]/volt, label=i * nbOutput + j)
#     legend()

import os, pickle, genParser, genInput, genLayer, genGraph
from brian2 import *

prefs['codegen.target'] = 'numpy'

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
nbPatterns = 4 * 100
input = genInput.genAlternateVerticalMovements(nbPixels, nbPixelStates, nbPatterns)
# if args['randomPattern']:
#     input = genInput.genRandomVerticalMovements(nbPixels, nbPixelStates, nbPatterns)
# else:
#     input = genInput.genAlternateVerticalMovements(nbPixels, nbPixelStates, nbPatterns)

layer = genLayer.genNeurons((nbPixels - 1) * 2)
layer.thresh = 1*volt
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
stateRecord = StateMonitor(layer, ('v', 'thresh', 'deltaThresh'), record = True) # Record the state of each neurons of the layer layer
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

timeRun = (nbPatterns/4 * (nbPixels-1) * 2 + 4) * ms

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
i = 1

while(nbNeurons != 2 and nbNeurons != 4 and nbNeurons != 6):

    previousNbNeurons = nbNeurons

    if(nbNeurons % 4 == 0):
        nbNeurons /= 2

        layerTab.append(genLayer.genNeurons(nbNeurons))
        layerTab[i].thresh = 1*volt
        layerTab[i].tLeak = layerTab[i-1].tLeak[0] + 2*ms
        layerTab[i].tRefrac = layerTab[i-1].tRefrac[0] - 2*ms
        layerTab[i].tInhib = 1*ms

        synapsesTab.append(genLayer.genSynapses(layerTab[i-1], previousNbNeurons,
            layerTab[i], nbNeurons, True, wAverage, wDeviation, wMin, wMax))
        synapsesTab[i].tLTP = synapsesTab[i-1].tLTP[0] + 2*ms

    else:
        nbNeurons = (nbNeurons-2) / 2

        layerTab.append(genLayer.genNeurons(nbNeurons))
        layerTab[i].thresh = 1*volt
        layerTab[i].tLeak = layerTab[i-1].tLeak[0] + 4*ms
        layerTab[i].tRefrac = layerTab[i-1].tRefrac[0] - 4*ms
        layerTab[i].tInhib = 1*ms

        synapsesTab.append(genLayer.genSynapses(layerTab[i-1], previousNbNeurons,
            layerTab[i], nbNeurons, True, wAverage, wDeviation, wMin, wMax))
        synapsesTab[i].tLTP = synapsesTab[i-1].tLTP[0] + 4*ms

    inhibitionTab.append(genLayer.genInhibition(layerTab[i]))
    stateRecordTab.append(StateMonitor(layerTab[i], ('v', 'thresh', 'deltaThresh'), record = True))

    net.add(layerTab[i])
    net.add(synapsesTab[i])
    net.add(inhibitionTab[i])
    net.add(stateRecordTab[i])

    input = genInput.genAlternateVerticalMovements(nbPixels, nbPixelStates, nbPatterns * (i+1))

    print ''
    print 'layer {} learning'.format(i+1)
    net.run(timeRun, report='stdout')

    i += 1

if(nbNeurons != 2):
    if(nbNeurons % 4 == 0):
        output = genLayer.genNeurons(2)
        output.thresh = 1*volt
        output.tLeak = layerTab[len(layerTab)-1].tLeak[0] + 2*ms
        output.tRefrac = layerTab[len(layerTab)-1].tRefrac[0] - 2*ms
        output.tInhib = 5*ms

        synapses_output = genLayer.genSynapses(layerTab[len(layerTab)-1], nbNeurons, output,
            2, True, wAverage, wDeviation, wMin, wMax)
        synapses_output.tLTP = synapsesTab[len(synapsesTab)-1].tLTP[0] + 2*ms

    else:
        output = genLayer.genNeurons(2)
        output.thresh = 1*volt
        output.tLeak = layerTab[len(layerTab)-1].tLeak[0] + 4*ms
        output.tRefrac = layerTab[len(layerTab)-1].tRefrac[0] - 6*ms
        output.tInhib = 4*ms

        synapses_output = genLayer.genSynapses(layerTab[len(layerTab)-1], nbNeurons, output,
            2, True, wAverage, wDeviation, wMin, wMax)
        synapses_output.tLTP = synapsesTab[len(synapsesTab)-1].tLTP[0] + 6*ms

    inhibition_output = genLayer.genInhibition(output)

    stateRecord_output = StateMonitor(output, ('v', 'thresh', 'deltaThresh'), record = True)
    stateRecordTab.append(stateRecord_output)

    net.add(output)
    net.add(synapses_output)
    net.add(inhibition_output)
    net.add(stateRecord_output)

    input = genInput.genAlternateVerticalMovements(nbPixels, nbPixelStates, nbPatterns * (i+1))

    print output.tRefrac

    print ''
    print 'Last layer learning'
    net.run(timeRun, report='stdout')

    i += 1

    synapsesTab.append(synapses_output)
    inhibitionTab.append(inhibition_output)
    layerTab.append(output)

genGraph.visualise_network(synapsesTab)

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
    layerTab[i].apprentissage = 0
    layerTab[i].tRefrac /= 2

# output.tRefrac = 0*ms
# output.tInhib = 0*ms
# inhibition_output.connect(False)

input = genInput.genAlternateVerticalMovements(nbPixels, nbPixelStates, nbPatterns * (i+1))

print ''
print 'Without learning'
net.run(timeRun, report='stdout')

genGraph.visualise_network(synapsesTab)

for i in range(len(layerTab)):
    figure(i)
    for j in range(len(stateRecordTab[i].v)) :
        plot(stateRecordTab[i].t/ms, (stateRecordTab[i].thresh[j] + stateRecordTab[i].deltaThresh[j])/volt, '--', label='threshold')
        plot(stateRecordTab[i].t/ms, stateRecordTab[i].v[j]/volt, label=j)
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

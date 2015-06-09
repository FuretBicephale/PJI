import os, pickle, genParser, genInput, genLayer
from brian2 import *

# Parser
parser = genParser.genParser()
args = genParser.getArgs(parser)
tInhib = args['tInhib']
tLeak = args['tLeak']
tRefrac = args['tRefrac']
tLTP = args['tLTP']
threshold = args['threshold']

# Input
nbPixels = 4
nbPixelStates = 2
nbPatterns = 500
if args['randomPattern']:
    input = genInput.genRandomVerticalMovements(nbPixels, nbPixelStates, nbPatterns)
else:
    input = genInput.genAlternateVerticalMovements(nbPixels, nbPixelStates, nbPatterns)

output = genLayer.genNeurons((nbPixels - 1) * 2, tRefrac)

wAverage = 0.700*volt
wDeviation = 0.100*volt
wMax = 1.000*volt
wMin = 0.000*volt

aPre = 0.1*volt
aPost = 0.05*volt
bPre = 0*volt
bPost = 0*volt

synapses = genLayer.genSynapses(input, nbPixels*nbPixelStates, output,
    (nbPixels - 1) * 2, True, wAverage, wDeviation, wMin, wMax)

inhibition = genLayer.genInhibition(output)

# Monitors
stateRecord = StateMonitor(output, 'v', record = True) # Record the state of each neurons of the output layer
# record = SpikeMonitor(output) # Record output layer spikes
# recordInput = SpikeMonitor(input) # Record input layer spikes
# synapsesRecord = StateMonitor(synapses, 'w', record = True)

timeRun = (nbPatterns * 10 + 10)*ms

for i in range(40):
    # Run
    print ''
    run(timeRun/40, report='stdout')

    # Synapses weight save
    try:
        folderPath = os.getcwd() + "/weights"
        if not os.path.exists(folderPath):
            os.mkdir(folderPath)
        assert os.path.isdir(folderPath)
    except:
        print "Erreur lors de la creation du dossier de sauvegarde"
        exit(14)

    nameTemp = folderPath + "/file" + ("%04d"%(i,)) + ".spw"
    wi = []
    for wn in synapses.w:
        wi.append(wn)
    with open(nameTemp, 'wb') as fichier:
        mon_pick = pickle.Pickler(fichier)
        mon_pick.dump(wi)

# Display simulation plot

figure(1)
plot(stateRecord.t/ms, [threshold for i in range(len(stateRecord.t))], '--', label='threshold')
for i in range(nbOutput) :
    plot(stateRecord.t/ms, stateRecord.v[i]/volt, label=i)
legend()

# figure(2)
# for i in range(nbOutput) :
#     subplot(2, 4, i+1)
#     plot(stateRecord.t/ms, [threshold] * len(stateRecord.t), '--', label='threshold')
#     plot(stateRecord.t/ms, stateRecord.v[i]/volt, label=i)
#     legend()

# figure(3)
# plot(stateRecord_2.t/ms, [threshold for i in range(len(stateRecord_2.t))], '--', label='threshold')
# for i in range(2) :
#     plot(stateRecord_2.t/ms, stateRecord_2.v[i]/volt, label=i)
# legend()

# figure(4)
# for j in range(nbOutput):
#     subplot(2, 4, j+1)
#     for i in range(nbPixels * nbPixelStates):
#         plot(synapsesRecord.t/ms, synapsesRecord.w[i * nbOutput + j]/volt, label=i * nbOutput + j)
#     legend()

show()

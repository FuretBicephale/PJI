from optparse import OptionParser
from random import randint, gauss, random

from brian2 import *

tInhib = 0 * ms
tLeak = 0 * ms
tRefrac = 0 * ms
tLTP = 0 * ms
threshold = 0 * volt

### Input neurons - 2 pixels with 2 states (ON/OFF).
nbPixels = 4;
nbPixelStates = 2;

# Movements
up = [7, 4] + [i - j for j in range(2, (nbPixels - 1) * 2, 2) for i in [7, 4]]
down = [1, 2] + [i + j for j in range(2, (nbPixels - 1) * 2, 2) for i in [1, 2]]
time = [1, 1, 3, 3, 5, 5]

# Learning
nbMotifs = 75
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

### Output neurons - We want to know if the movement is ascending or descending
nbOutput = (nbPixels - 1) * 2

# Neurons model
eqs = '''dv/dt = -v/tLeak : volt (unless refractory)
         lastInhib : second'''

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

def getScore(recordInput, recordOutput):
    score = 0
    tIn = recordInput.t[len(recordInput.t)-12:]
    tOut = []
    for i in range(len(recordOutput.t)):
        if recordOutput.t[len(recordOutput.t) - (i + 1)] < tIn[0]:
            break
        else:
            tOut.insert(0, recordOutput.t[len(recordOutput.t) - (i + 1)])
    for i in range(len(tIn)):
        nbAnswer = 0
        for j in range(len(tOut)):
            if i == len(tIn)-1:
                if tOut[j] >= tIn[i]:
                    nbAnswer += 1
            else:
                if tOut[j] >= tIn[i+1]:
                    break
                if tOut[j] >= tIn[i] and tOut[j] < tIn[i+1]:
                    nbAnswer += 1
        if nbAnswer == 0:
            score -= 5
        elif nbAnswer == 1:
            score += 10
    indicesOut = recordOutput.i[len(recordOutput.i) - len(tOut):]
    for i in range(6):
        if indicesOut.tolist().count(i) == 0:
            score -= 5
        elif indicesOut.tolist().count(i) == 1:
            score += 10
    return score

# Run
nbIndividus = 5
nbTests = 5
timeRun = times[len(times) - 1] + 10*ms
score = [0 for i in range(nbIndividus)]
config = [0 for i in range(nbIndividus)]

for i in range(nbIndividus):
    score[i] = 0

    tInhib = random() * 5 * ms
    tLeak = random() * 5 * ms
    tRefrac = random() * 20 * ms
    tLTP = random() * 5 * ms
    threshold = random() * 2 * volt

    config[i] = [tInhib, tLeak, tRefrac, tLTP, threshold]

    input = SpikeGeneratorGroup(nbPixels * nbPixelStates, indices, times)

    output = NeuronGroup(nbOutput, eqs, threshold='v > threshold',
        reset='v = 0*volt', refractory=tRefrac)

    synapses = Synapses(input, target=output, model=synapsesModel, pre=preEqs, post=postEqs)
    synapses.connect(True) # Connecting every neurons of the first layer to every neurons of the second one

    # Inhibition
    inhibition = Synapses(output, target=output, model='', pre  ='''
        lastInhib = t''')
    inhibition.connect("i != j") # Every neurons of the layer are connected to each other

    # Monitors
    record = SpikeMonitor(output) # Record output layer spikes
    recordInput = SpikeMonitor(input) # Record input layer spikes
    stateRecord = StateMonitor(output, 'v', record = True) # Record the state of each neurons of the output layer
    synapsesRecord = StateMonitor(synapses, 'w', record = True)

    net = Network()
    net.add(input)
    net.add(output)
    net.add(synapses)
    net.add(inhibition)
    net.add(record)
    net.add(recordInput)
    net.add(stateRecord)
    net.add(synapsesRecord)

    net.store("synapse")

    for j in range(nbTests):

        # Initialize synaptic weight with a gauss distribution
        for k in range(nbPixels * nbPixelStates):
            for l in range(nbOutput):
                synapses.w[k,l] = clip(
                    gauss(wInitAverage, wInitDeviation),
                    wMin,
                    wMax)
        print ''
        net.run(timeRun, report='stdout')
        score[i] += getScore(recordInput, record)
        net.restore("synapse")

print "Generation 1"
print config
print score

for m in range(5):
    new_score = score
    new_score.sort(reverse=True)
    new_config = []
    new_config += [config[score.index(new_score[0])]]
    score.remove(new_score[0])
    new_config += [config[score.index(new_score[1])]]
    new_config += new_config

    croisement_index = randint(0, 5)
    new_config[2][croisement_index] = new_config[1][croisement_index]
    new_config[3][croisement_index] = new_config[0][croisement_index]

    config[0] = new_config[0]
    config[1] = new_config[1]
    config[2] = new_config[2]
    config[3] = new_config[3]

    tInhib = random() * 10 * ms
    tLeak = random() * 5 * ms
    tRefrac = (random() * 10  + 10) * ms
    tLTP = random() * 3 * ms
    threshold = (random() + 1) * volt

    config[4] = [tInhib, tLeak, tRefrac, tLTP, threshold]

    score = [0 for i in range(nbIndividus)]

    for i in range(nbIndividus):
        score[i] = 0

        tInhib = config[i][0]
        tLeak = config[i][1]
        tRefrac = config[i][2]
        tLTP = config[i][3]
        threshold = config[i][4]

        input = SpikeGeneratorGroup(nbPixels * nbPixelStates, indices, times)

        output = NeuronGroup(nbOutput, eqs, threshold='v > threshold',
            reset='v = 0*volt', refractory=tRefrac)

        synapses = Synapses(input, target=output, model=synapsesModel, pre=preEqs, post=postEqs)
        synapses.connect(True) # Connecting every neurons of the first layer to every neurons of the second one

        # Inhibition
        inhibition = Synapses(output, target=output, model='', pre  ='''
            lastInhib = t''')
        inhibition.connect("i != j") # Every neurons of the layer are connected to each other

        # Monitors
        record = SpikeMonitor(output) # Record output layer spikes
        recordInput = SpikeMonitor(input) # Record input layer spikes
        stateRecord = StateMonitor(output, 'v', record = True) # Record the state of each neurons of the output layer
        synapsesRecord = StateMonitor(synapses, 'w', record = True)

        net = Network()
        net.add(input)
        net.add(output)
        net.add(synapses)
        net.add(inhibition)
        net.add(record)
        net.add(recordInput)
        net.add(stateRecord)
        net.add(synapsesRecord)

        net.store("synapse")

        for j in range(nbTests):

            # Initialize synaptic weight with a gauss distribution
            for k in range(nbPixels * nbPixelStates):
                for l in range(nbOutput):
                    synapses.w[k,l] = clip(
                        gauss(wInitAverage, wInitDeviation),
                        wMin,
                        wMax)
            print ''
            net.run(timeRun, report='stdout')
            score[i] += getScore(recordInput, record)
            net.restore("synapse")

    print "Generation {}".format(m + 2)
    print score
    print config

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
# plot(stateRecord.t/ms, [threshold for i in range(len(stateRecord.t))], '--', label='threshold')
# for i in range(nbOutput) :
#     plot(stateRecord.t/ms, stateRecord.v[i]/volt, label=i)
# legend()

# figure(3)
# for j in range(nbOutput):
#     subplot(2, 4, j+1)
#     for i in range(nbPixels * nbPixelStates):
#         plot(synapsesRecord.t/ms, synapsesRecord.w[i * nbOutput + j]/volt, label=i * nbOutput + j)
#     legend()
# show()

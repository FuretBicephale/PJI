from brian2 import *

### Input neurons - 2 pixels with 2 states (ON/OFF).
nbPixels = 2;
nbPixelStates = 2;

# Movements
down = [0, 1, 2, 3]
up = [2, 3, 0, 1]
time = [1, 2, 2, 3] # One movement last 2 seconds

# Learning
indices = (down + up) * 50
times = time + [i + j for j in range(5, 500, 5) for i in time] # 3 seconds between 2 movements

# After learning
indices += (up + down + down + up) * 25
times += [i + j for j in range(510, 1010, 5) for i in time]

times *= ms
input = SpikeGeneratorGroup(nbPixels * nbPixelStates, indices, times)

### Output neurons - We want to know if the movement is ascending or descending
nbOutput = 2;

tLeak = 5*ms # Leak time
tRefrac = 4*ms # Minimum time between two presynaptics spikes
tInhib = 3*ms # Minimum time before an inhibited spike can receive presynaptics spikes agains

# Neurons model
eqs = '''dv/dt = -v/tLeak : volt (unless refractory)
         refrac : second
         lastInhib : second'''

threshold = 800*volt # Neurons send a spike when this threshold is reached
reset = 0*volt # Initial neurons value

output = NeuronGroup(nbOutput, eqs, threshold='v>=threshold', reset='v=reset', refractory='refrac')
output.refrac = tRefrac

### Synapses - Each input is linked to each output
wInitAverage = 500*volt # Initial synaptic weight values
wInitDeviation = 200*volt
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

# Initialize synaptic weight randomly between wMin and wMax
synapses.w = '(rand() * wInitDeviation) + (wInitAverage - wInitDeviation/2)'
synapses.apprentissage = 1

# Inhibition
inhibition = Synapses(output, model='w : volt', pre='lastInhib = t * int(not_refractory)')
inhibition.connect("i != j") # Every neurons of the layer are connected to each other
inhibition.w = wInitAverage

# Monitor
record = SpikeMonitor(output) # Record output layer spikes
recordInput = SpikeMonitor(input) # Record input layer spikes
stateRecord = StateMonitor(output, ('v', 'refrac'), record = True) # Record the state of each neurons of the output layer
synapsesRecord = StateMonitor(synapses, ('w', 'dwPre', 'dwPost'), record = True) # Record the state of each synapses

# Run
print ''
timeRun = 500*ms
run(timeRun, report='stdout')

# End
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
#
# print ''
# print 'First layer state'
# print 'v = ', stateRecord.v
#
# print ''
# print 'Synapses state'
# print 'w = ', synapsesRecord.w
# print 'dwPre = ', synapsesRecord.dwPre
# print 'dwPost = ', synapsesRecord.dwPost

# plot(stateRecord.t/ms, [threshold for i in range(len(stateRecord.t))], '--', label='threshold')
# for i in range(nbOutput) :
#     plot(stateRecord.t/ms, stateRecord.v[i]/volt, label=i)
# legend()
# show()

# Second simulation
inhibition.connect(False) # Disconnect inhibition
synapses.apprentissage = 0

print ''
timeRun = 510*ms
run(timeRun, report='stdout')

plot(stateRecord.t/ms, [threshold for i in range(len(stateRecord.t))], '--', label='threshold')
for i in range(nbOutput) :
    plot(stateRecord.t/ms, stateRecord.v[i]/volt, label=i)
legend()
show()

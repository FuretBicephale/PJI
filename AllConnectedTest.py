from brian2 import *

# Input neurons
indices = [0, 0, 1, 1, 2, 2, 3, 3] * 10 # 4 neurons
times = [time for time in range(1, len(indices) * 2, 2)] * ms # Each neurons generate a spike at i ms (i = neurons index)
input = SpikeGeneratorGroup(4, indices, times)

# Neurones
nbPx = 8 # Number of pixels on the image
nbSynapsesPerPx = 2 # Number of synapses per pixel

tLeak = 5*ms # Leak time
tRefrac = 10*ms # Minimum time between two presynaptics spikes
tInhib = 2*ms # Minimum time before an inhibited spike can receive presynaptics spikes agains

eqs = '''dv/dt = -v/tLeak : volt (unless refractory)
         refrac : second
         lastInhib : second''' # Neurons model
threshold = 800*volt # Neurons send a spike when this threshold is reached
reset = 0*volt # Initial neurons value

firstLayer = NeuronGroup(nbPx, eqs, threshold='v>=threshold', reset='v=reset', refractory='refrac')
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
            v = v * (t - lastInhib < tInhib and lastInhib != 0 * ms) + (v * exp(-(t-lastupdate)/tLeak) + w) * (t - lastInhib >= tInhib or lastInhib == 0 * ms)
            refrac = tRefrac * int(not_refractory) + refrac * (1 - int(not_refractory))'''
# If ltpCondition is False then it's equals to 0, 1 otherwise
# So dwPre * (ltpCondition) = 0 if ltpCondition is false, dwPre otherwise
# And dwPost * (ltpCondition != 1) = 0 if ltpCondition is true (== 0), dwPost otherwise
postEqs = '''tPost = t
             w = clip(w + dwPre * (ltpCondition), wMin, wMax)
             w = clip(w - dwPost * (ltpCondition != 1), wMin, wMax)'''
synapses = Synapses(input, target=firstLayer, model=synapsesModel, pre=preEqs, post=postEqs)
synapses.connect(True, n=nbSynapsesPerPx) # Connecting every neurons of the first layer to every neurons of the second one
synapses.w = '(rand() * wMax) + wMin' # Initialize synaptic weight randomly between wMin and wMax

# Inhibition
inhibition = Synapses(firstLayer, model='w : volt', pre='lastInhib = t * int(not_refractory)')
inhibition.connect("i != j") # Every neurons of the layer are connected to each other
inhibition.w = wInit

# Monitor
record = SpikeMonitor(firstLayer) # Record output layer spikes
recordInput = SpikeMonitor(input) # Record input layer spikes
stateRecord = StateMonitor(firstLayer, ('v', 'refrac'), record = True) # Record the state of each neurons of the output layer
synapsesRecord = StateMonitor(synapses, ('w', 'dwPre', 'dwPost'), record = True) # Record the state of each synapses

# Run
print ''
timeRun = 200*ms
run(timeRun, report='stdout')

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

plot(stateRecord.t/ms, [threshold for i in range(len(stateRecord.t))], '--', label='threshold')
for i in range(nbPx) :
    plot(stateRecord.t/ms, stateRecord.v[i]/volt, label=i)
legend()
show()

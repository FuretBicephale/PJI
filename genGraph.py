from brian2 import *

def visualise_synapses(synapses, source, target):
    nbTarget = len(synapses.target)
    plot(ones(nbTarget) * target, arange(nbTarget), 'ok', ms=10)

    for i, j, w in zip(synapses.i, synapses.j, synapses.w):
        plot([source, target], [i, j], '-', lw=w/volt, color=(1 - w/volt, 1 - w/volt, 1 - w/volt, 1))

def visualise_network(synapsesTab):
   
    nbSource = len(synapsesTab[0].source)
    plot(zeros(nbSource), arange(nbSource), 'ok', ms=10)

    i = 1

    for synapses in synapsesTab:
        visualise_synapses(synapses, i-1, i)
        i += 1

    xticks(range(i), range(i))
    ylabel('Neuron index')
    xlim(-0.1, i)
    ylim(-1, nbSource)

    show()

def visualise_spike(spikeMonitor):
    plot(spikeMonitor.t/ms, spikeMonitor.i, '.k')

    xlabel('Time (ms)')
    ylabel('Neuron')
    
    show()
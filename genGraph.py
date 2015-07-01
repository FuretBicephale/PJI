from brian2 import *

def visualise_synapses(synapses, source, target):
    nbTarget = len(synapses.target)
    plot(ones(nbTarget) * target, arange(nbTarget), 'ok', ms=10)

    for i, j, w in zip(synapses.i, synapses.j, synapses.w):
        if(w == 1*volt):
            shape = '-r'
            weight = 1
        else:
            shape = '-k'
            weight = 0.1
        plot([source, target], [i, j], shape, lw=weight)

def visualise_network(synapsesTab):
    i = 0
    for synapses in synapsesTab:
        if i == 0:
            nbSource = len(synapses.source)
            plot(zeros(nbSource), arange(nbSource), 'ok', ms=10)
        else:
            visualise_synapses(synapses, i-1, i)
        i += 1

    xticks(range(i), range(i))
    ylabel('Neuron index')
    xlim(-0.1, i)
    ylim(-1, nbSource)

    show()

# PJI

### Requirements
* Python 2.7
* Brian2 Simulator

### Launch
Type "python TestSimple.py" in a command line

### TestSimple.py
Creates a neuronal system with spikes where a first layer generates spikes to a second layer. The first layer contains four neurons and is connected to a second layer of 8 neurons. Each neurons of the first layer is connected to two neurons of the second layer without two neurons of the first layer connected to a same neuron of the second one. There is also inhibition synapses between neurons of the second layer.

The output displays each layer spikes, second layer values and synapses weight.

### AllConnectedTest.py
This script is very similar to TestSimple : it creates a neuronal system with two layer connected to each other and one of them sending spikes to the other. The main difference is that each neuron of the first layer is connected to each neuron of the second one with random synapse weight.

The output displays the same values as TestSimple. It also displays plots with second layer's neurons voltage.

### 2pxMovementRecognition
Creates a neuronal system able to recognize a vertical movement between 2 pixels.

Currently, the synapses weight are randomly defined between two defined values. Because of this randomness, the recognition doesn't always works.

### movementLearningScript
This script is very similar to 2pxMovementRecognition except it takes parameters at execution to init some variables.
The parameters are the following :
*-i or --inhibition = Specify inhibition time in ms. Required.
*-l or --leak = Specify leak time in ms. Required.
*-n or --number = Specify number of learning test iterations. 100 iterations by defaults, integers only.
*-r or --refraction = Specify refraction time in ms. Required.
At end of execution, it will print the number of successful tries

import inspect
import logging
import os

from YAMLLoader import YAMLLoader
from core.ConfigurationManager.ConfigurationChecker import ConfigurationChecker
from core.Models.Brain import Brain
from core.Models.Event import Event
from core.Models.Neuron import Neuron
from core.Models.Order import Order
from core.Models.Synapse import Synapse

logging.basicConfig()
logger = logging.getLogger("jarvis")


class BrainLoader(YAMLLoader):

    def __init__(self, filepath=None):
        self.brain_file_path = filepath
        if filepath is None:
            self.brain_file_path = self._get_root_brain_path()
        # self.filePath = "../../" + self.fileName
        YAMLLoader.__init__(self, self.brain_file_path)

    def get_config(self):
        return YAMLLoader.get_config(self)

    def get_brain(self):
        """
        return a brain object from YAML settings
        :return: Brain object
        :rtype: Brain
        """
        # get the brain with dict
        dict_brain = self.get_config()
        # create a new brain
        brain = Brain()
        # create list of Synapse
        synapses = list()
        for synapses_dict in dict_brain:
            # print synapses_dict
            if ConfigurationChecker().check_synape_dict(synapses_dict):
                # print "synapses_dict ok"
                name = synapses_dict["name"]
                neurons = self._get_neurons(synapses_dict["neurons"])
                signals = self._get_signals(synapses_dict["signals"])
                new_synapse = Synapse(name=name, neurons=neurons, signals=signals)
                synapses.append(new_synapse)
        brain.synapses = synapses
        brain.brain_file = self.brain_file_path
        # check that no synapse have the same name than another
        if ConfigurationChecker().check_synapes(synapses):
            return brain
        return None

    @staticmethod
    def _get_neurons(neurons_dict):
        """
        Get a list of Neuron object from a neuron dict
        :param neurons_dict:
        :return:
        """
        neurons = list()
        for neuron_dict in neurons_dict:
            if isinstance(neuron_dict, dict):
                if ConfigurationChecker().check_neuron_dict(neuron_dict):
                    # print "Neurons dict ok"
                    for neuron_name in neuron_dict:

                        name = neuron_name
                        parameters = neuron_dict[name]
                        # print parameters
                        new_neuron = Neuron(name=name, parameters=parameters)
                        neurons.append(new_neuron)
            else:
                # the neuron does not have parameter
                if ConfigurationChecker().check_neuron_dict(neuron_dict):
                    new_neuron = Neuron(name=neuron_dict)
                    neurons.append(new_neuron)

        return neurons

    def _get_signals(self, signals_dict):
        # print signals_dict
        signals = list()
        for signal_dict in signals_dict:
            if ConfigurationChecker().check_signal_dict(signal_dict):
                # print "Signals dict ok"
                event_or_order = self._get_event_or_order_from_dict(signal_dict)
                signals.append(event_or_order)

        return signals

    @staticmethod
    def _get_event_or_order_from_dict(signal_or_event_dict):

        if 'event' in signal_or_event_dict:
            # print "is event"
            event = signal_or_event_dict["event"]
            if ConfigurationChecker.check_event_dict(event):
                return Event(period=event)

        if 'order' in signal_or_event_dict:
            order = signal_or_event_dict["order"]
            if ConfigurationChecker.check_order_dict(order):
                return Order(sentence=order)

    @staticmethod
    def _get_root_brain_path():
        """
        Return the full path of the default brain file
        :return:
        """
        # get current script directory path. We are in /an/unknown/path/jarvis/core/ConfigurationManager
        cur_script_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        # get parent dir. Now we are in /an/unknown/path/jarvis
        parent_dir = os.path.normpath(cur_script_directory + os.sep + os.pardir + os.sep + os.pardir)
        brain_path = parent_dir + os.sep + "brain.yml"
        logger.debug("Real brain.yml path: %s" % brain_path)
        if os.path.isfile(brain_path):
            return brain_path
        raise IOError("Default brain.yml file not found")




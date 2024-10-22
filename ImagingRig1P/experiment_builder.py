from abc import ABC, abstractmethod
from typing import Tuple

import nidaqmx.system._collections
import nidaqmx.system._collections.physical_channel_collection
import numpy as np
import numpy.typing

import nidaqmx
from nidaqmx.constants import AcquisitionType, ProductCategory, LineGrouping
from nidaqmx.constants import LoggingMode, LoggingOperation, READ_ALL_AVAILABLE
import nidaqmx.system

from nptdms import TdmsFile

from . import params

class Experiment():

    def __init__(self, do_data: dict, logfilename: str, sample_rate: int = 10000, duration: int = 10,
                 ):
        """_summary_

        Args:
            sample_rate (int, optional): Sample rate of NI DAQ in Hz. Defaults to 10000.
            duration (int, optional): Duration of the experiment in seconds. Defaults to 100.
        """
        
        #TODO add logging configurations
        self._logfilename = logfilename
        # check parent directory exists

        # check disk space

        # ensure file extension in tdms
        
        
        # 
        self._sample_rate = sample_rate
        self._duration = duration
        self._n_samples = int(sample_rate*duration)


        # check digital outputs are in correct format
        for chan_name, data in do_data.items():
            self._check_do_name(chan_name)
            self._check_do_data(data)
        self._do_dict = {chan_name: data>0 for chan_name, data in do_data.items()}

        # copy digital output to analog inputs
        self._analog_inputs = [k for k in self._do_dict.keys()]
        # add camera output
        self._analog_inputs.append('camera_output')
        
        




    def _check_do_name(self, name):
        """_summary_

        Args:
            name (_type_): _description_

        Raises:
            Exception: _description_
        """
        if name in set(params.DIGITAL_OUTPUTS.keys()):
            return
        else:
            raise Exception ###


    def _check_do_data(self, arr):
        """_summary_

        Args:
            arr (_type_): _description_
        """
        assert isinstance(arr,np.ndarray) ###
        assert arr.shape[0] == self._n_samples ####
        if ((arr==0).sum() + (arr==1).sum() != arr.shape[0]): 
            Warning ####
        

    def run_tasks(self):
        """_summary_
        """

        do_names = [params.DIGITAL_OUTPUTS[name] for name in self._do_dict.keys()]
        do_data = np.zeros([len(self._do_dict),self._n_samples])==0
        for i, v in enumerate(self._do_dict.values()):
            do_data[i,:] = v
        # do_data = do_data>0
        # do_data = np.array([v for v in self._do_dict.values()])

        with nidaqmx.Task('analog_inputs') as ai_task, nidaqmx.Task('digital_outputs') as do_task:


            ## set up analog input task
            for ai_name in self._analog_inputs:
                ai_task.ai_channels.add_ai_voltage_chan(params.ANALOG_INPUTS[ai_name])

            ai_task.timing.cfg_samp_clk_timing(self._sample_rate, sample_mode=AcquisitionType.FINITE,
                                               samps_per_chan = self._n_samples)
            
            ai_task.in_stream.configure_logging(self._logfilename, LoggingMode.LOG_AND_READ, 
                                                operation=LoggingOperation.CREATE_OR_REPLACE)
            
            ## set up 
            for do_name in do_names:
                print(do_name)
                do_task.do_channels.add_do_chan(do_name, line_grouping=LineGrouping.CHAN_PER_LINE)
            do_task.timing.cfg_samp_clk_timing(self._sample_rate, sample_mode=AcquisitionType.FINITE,
                                               samps_per_chan=self._n_samples)
            
            # send digital data to NIDAQ
            print(do_data.shape)
            do_task.write(do_data, auto_start=False)

            # simultaneously start digital outputs and analog inputs
            do_task.start()
            ai_task.read(READ_ALL_AVAILABLE)


            

    def load_tdms(self):

        tdms_file = tdms_file.read(self._logfilename)
        

        

        








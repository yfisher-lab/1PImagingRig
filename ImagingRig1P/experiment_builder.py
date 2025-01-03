from abc import ABC, abstractmethod
from typing import Tuple
import pathlib

import nidaqmx.system._collections
import nidaqmx.system._collections.physical_channel_collection
import numpy as np
import numpy.typing
import pandas as pd
import cloudpickle

import nidaqmx
from nidaqmx.constants import AcquisitionType, ProductCategory, LineGrouping
from nidaqmx.constants import LoggingMode, LoggingOperation, READ_ALL_AVAILABLE
import nidaqmx.system
import nidaqmx.task.channels

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
        self._logfilename = pathlib.Path(logfilename)
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

        self.pkl_dir = None
        
        
    @property
    def analog_inputs(self):
        return self._analog_inputs



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
            print(name)
            raise Exception ###


    def _check_do_data(self, arr):
        """_summary_

        Args:
            arr (_type_): _description_
        """
        assert isinstance(arr,np.ndarray) ###
        assert arr.shape[0] == self._n_samples, f"{arr.shape[0]}, {self._n_samples}"
        if ((arr==0).sum() + (arr==1).sum() != arr.shape[0]): 
            Warning ####
        

    def run_tasks(self):
        """_summary_
        """

        do_names = [params.DIGITAL_OUTPUTS[name] for name in self._do_dict.keys()]
        do_data = np.zeros([len(self._do_dict),self._n_samples])==0
        for i, v in enumerate(self._do_dict.values()):
            do_data[i,:] = v
       

        with nidaqmx.Task('analog_inputs') as ai_task, nidaqmx.Task('digital_outputs') as do_task:

            ## set up analog input task
            for ai_name in self._analog_inputs:
                ai_task.ai_channels.add_ai_voltage_chan(params.ANALOG_INPUTS[ai_name],
                                                        terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)
            # for i, _ in enumerate(self._analog_inputs):
            #     ai_task.ai_channels[i].ai_lowpass_enable=True
            #     ai_task.ai_channels[i].ai_lowpass_cutoff_freq = self._sample_rate/4

            ai_task.timing.cfg_samp_clk_timing(self._sample_rate, sample_mode=AcquisitionType.FINITE,
                                               samps_per_chan = self._n_samples)
            
            ai_task.in_stream.configure_logging(self._logfilename, LoggingMode.LOG_AND_READ, 
                                                operation=LoggingOperation.CREATE_OR_REPLACE)
            
            ## set up 
            for do_name in do_names:
                do_task.do_channels.add_do_chan(do_name, line_grouping=LineGrouping.CHAN_PER_LINE)
            do_task.timing.cfg_samp_clk_timing(self._sample_rate, sample_mode=AcquisitionType.FINITE,
                                               samps_per_chan=self._n_samples)
            
            # send digital data to NIDAQ
            print(do_data.shape)
            do_task.write(do_data, auto_start=False)

            # simultaneously start digital outputs and analog inputs
            do_task.start()
            ai_task.read(READ_ALL_AVAILABLE, timeout=self._duration+5)


            

    def tdms_to_dataframe(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        tdms_file = TdmsFile.read(self._logfilename)
        analog_inputs = tdms_file['analog_inputs']

        df = {}
        for i, ai_name in enumerate(self._analog_inputs):
            channel = analog_inputs[params.ANALOG_INPUTS[ai_name]]
            if i==0:
                df['time']= channel.time_track()
            df[ai_name] = channel.data[:]
        return pd.DataFrame.from_dict(df)

        
    def save_dataframe(self,dataframe, scan_info, **kwargs):
        """_summary_

        Args:
            dataframe (_type_): _description_
            scan_info (_type_): _description_
        """
        self.pkl_dir = self._logfilename.with_suffix('.pkl')
        save_dict = {'dataframe': dataframe,
                     'scan_info': scan_info}
        for k,v in kwargs.items():
            save_dict[k]=v
        with open(self.pkl_dir, 'wb') as f:
            cloudpickle.dump(save_dict, f)
        

        


        








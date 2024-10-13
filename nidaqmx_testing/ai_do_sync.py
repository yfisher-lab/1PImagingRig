"""Example of analog input and output synchronization.

This example demonstrates how to continuously acquire and
generate data at the same time, synchronized with one another.
"""

from typing import Tuple

import nidaqmx.system._collections
import nidaqmx.system._collections.physical_channel_collection
import numpy as np
import numpy.typing

import nidaqmx
from nidaqmx.constants import AcquisitionType, ProductCategory, LineGrouping
import nidaqmx.system


def get_terminal_name_with_dev_prefix(task: nidaqmx.Task, terminal_name: str) -> str:
    """Gets the terminal name with the device prefix.

    Args:
        task: Specifies the task to get the device name from.
        terminal_name: Specifies the terminal name to get.

    Returns:
        Indicates the terminal name with the device prefix.
    """
    for device in task.devices:
        if device.product_category not in [
            ProductCategory.C_SERIES_MODULE,
            ProductCategory.SCXI_MODULE,
        ]:
            return f"/{device.name}/{terminal_name}"

    raise RuntimeError("Suitable device not found in task.")

devname = 'Dev1'
# DIGITAL OUTPUTS
# Camera trig
do_cam_trig = 'port0/line0'
# CoolLED triggers
do_led365 = 'port0/line1'
do_led450 = 'port0/line2'
do_led550 = 'port0/line3'
d0_led635 = 'port0/line4'
# PV850 pump trigger
do_pump = 'port0/line5'

# ANALOG OUTPUTS
# Camera trig
ai_cam_trig = 'ai0'
ai_cam_output = 'ai6'
# CoolLED triggers, recording
ai_led365 = 'ai1'
ai_led450 = 'ai2'
ai_led550 = 'ai3'
ai_led635 = 'ai4'
# PV850 pump output
ai_pump = 'ai5'





def main():

    with nidaqmx.Task() as ai_task, nidaqmx.Task() as do_task:

        # set analog input channels
        ai_task.ai_channels.add_ai_voltage_chan('Dev1/ai0')

        #  edit this to discrete amount of  time
        ai_task.timing.cfg_samp_clk_timing(1000.0, sample_mode=AcquisitionType.CONTINUOUS)

        do_task.do_channels.add_do_chan('Dev1/port0/line0', line_grouping=LineGrouping.CHAN_PER_LINE)
        do_task.timing.cfg_samp_clk_timing(1000.0, sample_mode=AcquisitionType.CONTINUOUS)



# 
with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
    task.timing.cfg_samp_clk_timing(1000.0, sample_mode=AcquisitionType.FINITE, samps_per_chan=10)
    task.in_stream.configure_logging("TestData.tdms", LoggingMode.LOG_AND_READ, operation=LoggingOperation.CREATE_OR_REPLACE)
    data = task.read(READ_ALL_AVAILABLE)
    print("Acquired data: [" + ", ".join(f"{value:f}" for value in data) + "]")
# 
from nptdms import TdmsFile
with TdmsFile.read("TestData.tdms") as tdms_file:
  for group in tdms_file.groups():
    for channel in group.channels():
      data = channel[:]
      print("data: [" + ", ".join(f"{value:f}" for value in data) + "]")

# https://github.com/ni/nidaqmx-python/blob/master/examples/synchronization/multi_function/ai_ao_sync.py
def main():
    """Continuously acquires and generate data at the same time."""
    total_read = 0
    number_of_samples = 1000

    with nidaqmx.Task() as ai_task, nidaqmx.Task() as ao_task:

        def callback(task_handle, every_n_samples_event_type, number_of_samples, callback_data):
            """Callback function for reading signals."""
            nonlocal total_read
            read = ai_task.read(number_of_samples_per_channel=number_of_samples)
            total_read += len(read)
            print(f"Acquired data: {len(read)} samples. Total {total_read}.", end="\r")

            return 0

        ai_task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
        ai_task.timing.cfg_samp_clk_timing(1000.0, sample_mode=AcquisitionType.CONTINUOUS)
        ai_task.register_every_n_samples_acquired_into_buffer_event(1000, callback)
        terminal_name = get_terminal_name_with_dev_prefix(ai_task, "ai/StartTrigger")

        ao_task.ao_channels.add_ao_voltage_chan("Dev1/ao0")
        ao_task.timing.cfg_samp_clk_timing(1000.0, sample_mode=AcquisitionType.CONTINUOUS)
        ao_task.triggers.start_trigger.cfg_dig_edge_start_trig(terminal_name)

        actual_sampling_rate = ao_task.timing.samp_clk_rate
        print(f"Actual sampling rate: {actual_sampling_rate:g} S/s")

        ao_data, _ = generate_sine_wave(
            frequency=10.0,
            amplitude=1.0,
            sampling_rate=actual_sampling_rate,
            number_of_samples=number_of_samples,
        )

        ao_task.write(ao_data)
        ao_task.start()
        ai_task.start()

        input("Acquiring samples continuously. Press Enter to stop.\n")

        ai_task.stop()
        ao_task.stop()

        print(f"\nAcquired {total_read} total samples.")





if __name__=="__main__":
    device = nidaqmx.system.Device('Dev1')
    print(device.do_lines)
    for channel in device.do_lines:
        print(channel.name)
    
    # for device in nidaqmx.system.System.local().devices:
    #     print(device)
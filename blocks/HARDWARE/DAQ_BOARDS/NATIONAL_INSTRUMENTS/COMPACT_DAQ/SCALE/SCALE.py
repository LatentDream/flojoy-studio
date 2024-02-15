from typing import Literal
from flojoy import flojoy, DeviceConnectionManager, Vector
import nidaqmx
from nidaqmx._task_modules.channels import AIChannel, AOChannel, CIChannel, COChannel, DIChannel, DOChannel
import logging
from nidaqmx.constants import ChannelType
import numpy as np


@flojoy(deps={"nidaqmx": "0.9.0"})
def SCALE(
    task_name: str,
    data: Vector,
    scale_type: Literal[
        "Voltage",
        "Current",
        "Electrical to Physical",
        "Physical to Electrical",
    ] = "Current",
) -> Vector:

    task: nidaqmx.Task = DeviceConnectionManager.get_connection(task_name).get_handle()
    channels_to_read = task.in_stream.channels_to_read
    nb_chan = len(channels_to_read)
    channel_type = channels_to_read.chan_type
    logging.info(f"Task {task_name} has {nb_chan} channels of type {channel_type}")

    if channel_type == ChannelType.ANALOG_INPUT:
        for channel in channels_to_read:
            coeff = channel.ai_dev_scaling_coeff
            coeff.reverse()
            poly = np.poly1d(coeff)
            data = Vector(poly(data.v))
    else:
        NotImplemented(f"Channel type {channel_type} not supported yet!")

    return data

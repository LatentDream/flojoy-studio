from typing import Literal, DeviceConnectionManager, Vector
from flojoy import flojoy
from flojoy.data_container import Vector
import nidaqmx
from nidaqmx._task_modules.channels import AIChannel, AOChannel, CIChannel, COChannel, DIChannel, DOChannel
import logging


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

    for chan in task.ai_channels:
        coeff = chan.pwr_current_dev_scaling_coeff
        logging.info(f"Channel {chan.name} has scaling coefficient {coeff}")  
        
    return data

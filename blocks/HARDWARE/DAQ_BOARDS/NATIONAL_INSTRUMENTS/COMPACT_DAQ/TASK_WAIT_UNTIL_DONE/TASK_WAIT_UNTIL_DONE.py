from flojoy import flojoy, DataContainer, NIDAQmxConnection
import nidaqmx
from typing import Optional


@flojoy(deps={"nidaqmx": "0.9.0"}, inject_connection=True)
def TASK_WAIT_UNTIL_DONE(
    connection: NIDAQmxConnection,
    timeout: float = 10.0,
    default: Optional[DataContainer] = None,
) -> Optional[DataContainer]:
    """Waits for the measurement or generation to complete.

    Use this method to ensure that the specified operation is complete before you stop the task.

    This instrument will likely only be compatible with Windows systems due to
    NI driver availablity. To use the instrument you must install the runtime:

    https://www.ni.com/en/support/downloads/drivers/download.ni-daq-mx.html
    

    Parameters
    ----------
    connection : NIDAQmxDevice
        The first input channel for which a created task has been initialized.
    timeout : float
        Specifies the maximum amount of time in seconds to wait for the measurement or generation to complete. This method returns an error if the time elapses.

    Returns
    -------
    Optional[DataContainer]
        Return the input
    """

    task: nidaqmx.task.Task = connection.get_handle()
    task.wait_until_done(timeout=timeout)
    return default

from flojoy import flojoy, DataContainer, NIDAQmxDevice, DeviceConnectionManager
from typing import Optional, Literal
import nidaqmx


@flojoy(deps={"nidaqmx": "0.9.0"})
def CREATE_TASK_ANALOG_INPUT_STRAIN_GAGE(
    cDAQ_start_channel: NIDAQmxDevice,
    cDAQ_end_channel: NIDAQmxDevice,
    min_val: float = -0.001,
    max_val: float = 0.001,
    units: Literal["STRAIN"] = "STRAIN",
    strain_config: Literal[
        "Full brige 1",
        "Full brige 2",
        "Full brige 3",
        "Half brige 1",
        "Half brige 2",
        "Quarter brige 1",
        "Quarter brige 2",
    ] = "Full brige 1",
    voltage_excitation_source: Literal[
        "None",
        "External",
        "Internal"
    ] = "Internal",
    voltage_excitation_value: float = 2.5,
    default: Optional[DataContainer] = None,
    gage_factor: float = 2.0,
    initial_bridge_voltage: float = 0.0,
    nominal_gage_resistance: float = 350.0,
    poisson_ratio: float = 0.3,
    lead_wire_resistance: float = 0.0,
) -> Optional[DataContainer]:
    """Creates a task with (a) channel(s) to measure strain.

    Compatible with National Instruments compactDAQ devices. The device must have a strain input channel.
    Tested on a simulated NI-9236 module.

    Parameters
    ----------
    cDAQ_start_channel : NIDAQmxDevice
        The device and channel to read from.
    cDAQ_end_channel : NIDAQmxDevice
        To read from only one channel, set this to the same as cDAQ_start_channel. To read from multiple channels, set this to the last channel you want to read from.
    min_val : float
        Specifies in **units** the minimum value you expect to measure.
    max_val : float
        Specifies in **units** the maximum value you expect to measure.
    units : Literal
        The units to use to return strain measurements.
    strain_config : Literal
        Specifies information about the bridge configuration and measurement.
    voltage_excit_source : Literal
        Specifies information about the bridge configuration and measurement.
    voltage_excit_val : float
        Specifies information about the bridge configuration and measurement.
    gage_factor : float
        Contains information about the strain gage and measurement.
    initial_bridge_voltage : float
        Specifies information about the bridge configuration and measurement.
    nominal_gage_resistance : float
        Contains information about the strain gage and measurement.
    poisson_ratio : float
        Contains information about the strain gage and measurement.
    lead_wire_resistance : float
        Specifies information about the bridge configuration and measurement.

    Returns
    -------
    Optional[DataContainer]
        None
    """

    # Build the physical channels strin
    name, address = cDAQ_start_channel.get_id().split('/')
    if cDAQ_end_channel:
        _, address_end = cDAQ_end_channel.get_id().split('/')
        address = f"{address}:{address_end[2:]}"
    physical_channels = f"{name}/{address}"

    units = nidaqmx.constants.StrainUnits.STRAIN  # TODO: Support custom scale
    strain_config = {
        "Full brige 1": nidaqmx.constants.StrainGageBridgeType.FULL_BRIDGE_I,
        "Full brige 2": nidaqmx.constants.StrainGageBridgeType.FULL_BRIDGE_II,
        "Full brige 3": nidaqmx.constants.StrainGageBridgeType.FULL_BRIDGE_III,
        "Half brige 1": nidaqmx.constants.StrainGageBridgeType.HALF_BRIDGE_I,
        "Half brige 2": nidaqmx.constants.StrainGageBridgeType.HALF_BRIDGE_II,
        "Quarter brige 1": nidaqmx.constants.StrainGageBridgeType.QUARTER_BRIDGE_I,
        "Quarter brige 2": nidaqmx.constants.StrainGageBridgeType.QUARTER_BRIDGE_II,
    }[strain_config]

    voltage_excitation_source = {
        "None": nidaqmx.constants.ExcitationSource.NONE,
        "External": nidaqmx.constants.ExcitationSource.EXTERNAL,
        "Internal": nidaqmx.constants.ExcitationSource.INTERNAL
    }[voltage_excitation_source]

    task = nidaqmx.Task()
    DeviceConnectionManager.register_connection(cDAQ_start_channel, task, lambda task: task.__exit__(None, None, None))
    task.ai_channels.add_ai_strain_gage_chan(
        physical_channels,
        min_val=min_val,
        max_val=max_val,
        units=units,
        strain_config=strain_config,
        voltage_excit_source=voltage_excitation_source,
        voltage_excit_val=voltage_excitation_value,
        gage_factor=gage_factor,
        initial_bridge_voltage=initial_bridge_voltage,
        nominal_gage_resistance=nominal_gage_resistance,
        poisson_ratio=poisson_ratio,
        lead_wire_resistance=lead_wire_resistance,
    )

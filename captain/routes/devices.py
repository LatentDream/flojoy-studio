from fastapi import APIRouter
from captain.services.hardware import get_device_finder
from captain.types.devices import DeviceInfo

router = APIRouter(tags=["devices"])

import logging
@router.get("/devices")
async def get_devices() -> dict[str, str] | DeviceInfo:
    device_finder = get_device_finder()
    logging.info("Getting devices")
    logging.info(device_finder.get_nidaqmx_devices())
    return DeviceInfo(
        cameras=device_finder.get_cameras(),
        serialDevices=device_finder.get_serial_devices(),
        visaDevices=device_finder.get_visa_devices(),
        nidaqmxDevices=device_finder.get_nidaqmx_devices(),
    )

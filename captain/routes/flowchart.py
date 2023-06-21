import asyncio
from http.client import HTTPException
import json
from fastapi import APIRouter, Request, Response
import yaml
import time
from captain.types.flowchart import (
    PostCancelFC,
    PostWFC,
    WorkerSuccessResponse,
    WorkerFailedResponse,
)
from captain.utils.flowchart_utils import (
    create_topology,
    running_topology
)
from captain.utils.redis_dao import RedisDao
from captain.utils.config import manager
from captain.utils.status_codes import STATUS_CODES
from captain.types.worker import WorkerJobResponse

router = APIRouter(tags=["flowchart"])


"""
FRONT-END CLIENT ACCESSED END-POINTS
______________________________________

These end-points are accessed by the front-end client. They are used to
initiate processes on the back-end.
"""


@router.post("/cancel_fc", summary="cancel flowchart")
async def cancel_fc(fc: PostCancelFC):

    running_topology.cancel()
    msg = {
        "SYSTEM_STATUS": STATUS_CODES["RUN_PRE_JOB_OP"],
        "jobsetId": fc.jobsetId,
        "FAILED_NODES": "",
        "RUNNING_NODES": "",
    }
    asyncio.create_task(manager.ws.broadcast(json.dumps(msg)))


@router.post("/wfc", summary="write and run flowchart")
async def write_and_run_flowchart(request: PostWFC):

    global running_topology

    # connect to Redis and write the flowchart
    redis_client = RedisDao()

    # create the topology
    running_topology = create_topology(json.loads(request.fc), redis_client)

    # create message for front-end
    msg = {
        "SYSTEM_STATUS": STATUS_CODES["RUN_PRE_JOB_OP"],
        "jobsetId": request.jobsetId,
        "FAILED_NODES": "",
        "RUNNING_NODES": "",
    }
    asyncio.create_task(manager.ws.broadcast(json.dumps(msg)))

    # run the flowchart
    asyncio.create_task(running_topology.run())


"""
BACK-END CLIENT ACCESSED END-POINTS
_____________________________________

These end-points are accessed by the back-end client. They are used to implement
the event driven paradigm of the back-end. Workers that run jobs will poll these to 
signal a job has been finished.
"""

@router.post("/worker_response", summary="worker response")
async def worker_response(request: Request): # TODO figure out way to use Pydantic model, for now use type Request otherwise does not work???? 

    print("Received a response from a worker")

    request_json = await request.json()
    # print(request_dict)
    request_dict = json.loads(request_json)
    request_dict["type"] = "worker_response"

    # forward response from worker to the front-end
    asyncio.create_task(manager.ws.broadcast(json.dumps(request_dict)))
    if "NODE_RESULTS" in request_dict:
        job_id: str = request_dict.get('NODE_RESULTS', {}).get('id', None)
        print(f"{job_id} finished at {time.time()}")
        asyncio.create_task(running_topology.handle_finished_job(request_dict)) # type: ignore

    return Response(status_code=200)


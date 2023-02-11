from flojoy import reactflow_to_networkx
import sys
import os
import json
import yaml
from rq.job import Job
import traceback
import warnings
import matplotlib.cbook
import requests
from dotenv import dotenv_values
import networkx as nx

from collections import defaultdict

warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

from services.job_service import JobService
from FUNCTIONS.LOADERS import *
from FUNCTIONS.SIGNAL_PROCESSING import *
from FUNCTIONS.ARRAY_AND_MATRIX import *
from FUNCTIONS.TIMERS import *
from FUNCTIONS.CONDITIONALS import *
from FUNCTIONS.LOOPS import *
from FUNCTIONS.SIMULATIONS import *
from FUNCTIONS.ARITHMETIC import *
from FUNCTIONS.VISORS import *
from common.CONSTANTS import KEY_ALL_JOBEST_IDS

stream = open('STATUS_CODES.yml', 'r')
STATUS_CODES = yaml.safe_load(stream)

job_service = JobService('flojoy')
q = job_service.queue
print('queue flojoy isEmpty? ', q.is_empty())

conditional_nodes = defaultdict(lambda: {})


def get_port():
    try:
        p = dotenv_values('.env')['REACT_APP_BACKEND_PORT']
    except:
        p = '8000'
    return p


port = get_port()


def send_to_socket(data):
    requests.post('http://localhost:'+port +
                  '/worker_response', json=json.dumps(data))


def dump(data):
    return json.dumps(data)


def get_job_id(job_key: str, redis_key: str) -> str | None:
    try:
        all_jobs = job_service.get_redis_obj(redis_key)
        job_id = all_jobs[job_key]
    except Exception:
        print("Job Id doesn't exist", Exception, traceback.format_exc())
        return None
    return job_id


def report_failure(job, connection, type, value, traceback):
    print(job, connection, type, value, traceback)


def get_loop_status(r_obj, node_id=None, loop_info=False):
    special_type_jobs = r_obj['SPECIAL_TYPE_JOBS'] if 'SPECIAL_TYPE_JOBS' in r_obj else {
    }

    print("special_type_jobs: ", special_type_jobs)
    print("node id: ", node_id)

    if len(special_type_jobs) == 0:
        if loop_info:
            return False, 0, 0
        return False

    print(special_type_jobs['LOOP'][node_id]
          if node_id in special_type_jobs['LOOP'] else 'False')

    loop_status = len(special_type_jobs) and \
        len(special_type_jobs['LOOP']
            ) if 'LOOP' in special_type_jobs else False

    loop_status = loop_status and len(
        special_type_jobs['LOOP'][node_id]) if node_id in special_type_jobs['LOOP'] else False

    print('Loop Status: ', loop_status)

    current_iteration = 0
    initial_value = 0
    loop_ongoing = False

    if loop_status:
        loop_ongoing = special_type_jobs['LOOP'][node_id]['status'] == 'ongoing' if (
            loop_status and 'status' in special_type_jobs['LOOP'][node_id]) else False
        loop_finished = special_type_jobs['LOOP'][node_id]['status'] == 'finished' if (
            loop_status and 'status' in special_type_jobs['LOOP'][node_id]) else False
        if loop_ongoing or loop_finished:
            current_iteration = special_type_jobs['LOOP'][node_id]['params']['current_iteration']
            initial_value = special_type_jobs['LOOP'][node_id]['params']['initial_value']
    if not loop_info:
        return loop_ongoing
    return loop_status, current_iteration, initial_value


def check_loop_type(node_serial, cmd, node_id, edge_info, DG, r_obj):
    is_part_of_loop, is_part_of_loop_body, is_part_of_loop_end, is_eligible = False, False, False, None
    loop_id = ""

    if len(list(DG.predecessors(node_serial))) == 0:
        return is_part_of_loop, not is_part_of_loop_body, is_part_of_loop_end, is_eligible

    if cmd == "LOOP":
        return True, True, False, is_eligible

    for value in edge_info[node_id]:

        for key, val in value.items():

            if key == 'source' and 'LOOP' in val:
                loop_id = val
                is_part_of_loop = True
            if key == 'sourceHandle':
                if val == 'body':
                    is_part_of_loop_body = True
                if val == 'end':
                    is_part_of_loop_end = True
    if is_part_of_loop_end:

        status = get_loop_status(r_obj, node_id=loop_id)

        print("status: ", status)

        if status:
            is_eligible = False
        else:
            is_eligible = True
    return is_part_of_loop, is_part_of_loop_body, is_part_of_loop_end, is_eligible


def check_if_default_node_part_of_loop(node_serial, enqued_job_list, DG):
    # loop_status = get_loop_status(r_obj)
    is_eligible_to_enqueue = True
    for p in DG.predecessors(node_serial):
        if p not in enqued_job_list:
            return not is_eligible_to_enqueue  # must wait for next cycle
    return is_eligible_to_enqueue


def is_eligible_on_condition(node_serial, direction, DG, edge_info, get_job_id, all_job_key, current_conditional):
    id = DG.nodes[node_serial]['id']
    if len(list(DG.predecessors(node_serial))) == 1:
        p = list(DG.predecessors(node_serial))[0]
        prev_cmd = DG.nodes[p]['cmd']
        pred_id = DG.nodes[p]['id']
        if prev_cmd == 'CONDITIONAL':
            if current_conditional != pred_id:
                return False
            edge_label = edge_info[id][0]['sourceHandle']
            if edge_label != 'default':
                if edge_label.lower() != str(direction).lower():
                    return False
            return True
    # fetch previous job_ids
    for p in DG.predecessors(node_serial):
        pred_id = DG.nodes[p]['id']
        prev_cmd = DG.nodes[p]['cmd']
        prev_job_id = get_job_id(job_key="{}{}".format(
            prev_cmd, pred_id), redis_key=all_job_key)
        if prev_job_id == None:
            return False
        try:
            job = Job.fetch(prev_job_id, connection=r)
            if prev_cmd == 'CONDITIONAL':
                if current_conditional != pred_id:
                    return False
                for value in edge_info[id]:
                    if value['source'] == pred_id:
                        edge_label = value['sourceHandle']
                        if edge_label != 'default':
                            if edge_label.lower() != str(direction).lower():
                                return False
        except:
            return False
    return True


def get_previous_job_ids(DG, node_serial):
    previous_job_ids = []
    for p in DG.predecessors(node_serial):
        id = DG.nodes[p]['id']
        previous_job_ids.append(id)
    return previous_job_ids


def check_pred_exist_in_current_queue(current_queue, enqued_job_list, node_serial, DG):

    for p in DG.predecessors(node_serial):
        if (p not in current_queue) and (p not in enqued_job_list):
            return False
    return True


class Graph:
    def __init__(self, DG, edge_label_dict):
        self.DG = DG
        self.edges = DG.edges
        self.nodes = DG.nodes
        self.edge_label_dict = edge_label_dict
        self.adjList = {}
        self.make_adjancency_list()

    def get_node_data_by_id(self):
        nodes_by_id = dict()
        for n, nd in self.DG.nodes().items():
            nodes_by_id[n] = nd
        return nodes_by_id

    def make_adjancency_list(self):
        for (src, dest) in self.edges:

            if src not in self.adjList.keys():
                self.adjList[src] = []

            for value in self.edge_label_dict[self.get_node_data_by_id()[dest]['id']]:

                if value['source'] == self.get_node_data_by_id()[src]['id']:
                    sourceHandle = value['sourceHandle']

            self.adjList[src].append({
                'target_node_id': self.get_node_data_by_id()[dest]['id'],
                'src_node_id': self.get_node_data_by_id()[src]['id'],
                'target_node': dest,
                'handle': sourceHandle
            })


def DFS(graph, source, visited, current_loop_nodes, hashmap, get_node_data_by_id):
    # print("source: ", source)
    childs = []
    # print(" get_node_by_id: ", get_node_data_by_id.get(source, "NOt found"))
    cmd = get_node_data_by_id[source]['cmd']
    id = get_node_data_by_id[source]['id']


    if source not in graph.adjList.keys():
        visited[source-1] = True
        return [id]

    body = []
    end = []

    # checking if the source is LOOP type
    if cmd == 'LOOP':

        current_loop_nodes.append(id)

        # find the end & body source Handle
        for value in graph.adjList[source]:
            if value['handle'] == 'body':
                body.append(value['target_node'])
            if value['handle'] == 'end':
                end.append(value['target_node'])

        # traversing the body node first
        for value in body:
            child_node_ids = DFS(graph=graph, source=value, visited=visited,
                                     current_loop_nodes=current_loop_nodes, hashmap=hashmap, get_node_data_by_id=get_node_data_by_id)
            childs = childs + child_node_ids

        # current_loop_nodes.pop()
        # hashmap[id] = current_loop_nodes.copy()

        for value in end:
            if not visited[value-1]:
                child_node_ids = DFS(graph=graph, source=value, visited=visited,
                                     current_loop_nodes=current_loop_nodes, hashmap=hashmap, get_node_data_by_id=get_node_data_by_id)
                childs = childs + child_node_ids

        visited[source-1] = True
    elif cmd == "CONDITIONAL":
        # find the end & body source Handle
        print(" adjlist: ", graph.adjList[source])
        for value in graph.adjList[source]:
            print(" value: ", value)
            output_name = value['handle']
            child_node_ids = DFS(graph=graph, source=value['target_node'], visited=visited,
                                 current_loop_nodes=current_loop_nodes, hashmap=hashmap, get_node_data_by_id=get_node_data_by_id)
            childs = childs + child_node_ids
            conditional_nodes[id][output_name] = child_node_ids

    else:
        for value in graph.adjList[source]:
           
            child_node_ids = DFS(graph=graph, source=value['target_node'], visited=visited,
                                     current_loop_nodes=current_loop_nodes, hashmap=hashmap, get_node_data_by_id=get_node_data_by_id)
            childs = childs + child_node_ids
        # hashmap[id] = current_loop_nodes.copy()
        # visited[source-1] = True
    return [id] + childs


def get_hash_loop(hash_map, get_node_data_by_id, DG):
    hash_map_loop = {}

    for key, value in hash_map.items():
        if len(value) > 0:
            for loop_id in value:
                if loop_id not in hash_map_loop.keys():
                    hash_map_loop[loop_id] = []
                hash_map_loop[loop_id].append(key)

    topological_sorting_list = [get_node_data_by_id[node]['id']
                                for node in list(nx.topological_sort(DG))]

    sorting_order_loopnodes = {}

    for key, nodes in hash_map_loop.items():
        sorting_order = [topological_sorting_list.index(
            node) for node in nodes]
        sorting_order.sort()
        sorting_order_loopnodes[key] = [
            topological_sorting_list[node_id] for node_id in sorting_order]
    return sorting_order_loopnodes


def get_loop_body_nodes(hash_map, loop_nodes):
    sorting_order_loopnodes = loop_nodes
    for key, parents in hash_map.items():
        if 'LOOP' in key and len(parents) > 0:

            for parent in parents:

                parent_loop_nodes = loop_nodes[parent].copy()
                child_loop_nodes = loop_nodes[key].copy()

                for node in child_loop_nodes:
                    parent_loop_nodes.remove(
                        node) if node in parent_loop_nodes else ''

                sorting_order_loopnodes[parent] = parent_loop_nodes

    return sorting_order_loopnodes


def get_conditional_node_id(node_id, loop_body_nodes):
    if node_id not in loop_body_nodes.keys():
        return None
    else:
        loop_body_nodes = loop_body_nodes[node_id]
        return loop_body_nodes[len(loop_body_nodes)-1]


def find_loop_serial_id(node_id, loop_body_nodes, hash_map_topological_sorting):
    for key, nodes in loop_body_nodes.items():
        if node_id in nodes:
            return hash_map_topological_sorting[key]


def get_loop_nodes(node_id, loop_nodes, hash_map_topologicalsorting):
    node_list = []
    for node in loop_nodes[node_id]:
        node_list.append(hash_map_topologicalsorting[node])
    return node_list


def run_old(**kwargs):
    jobset_id = kwargs['jobsetId']
    try:
        fc = kwargs['fc']
        # job id of running node
        my_job_id = kwargs['my_job_id']
        print('running flojoy for jobset id: ', jobset_id)

        jobset_data = job_service.get_redis_obj(jobset_id)
        r.delete('{}_ALL_NODES'.format(jobset_id))

        elems = fc['nodes']
        edges = fc['edges']

        r.set('{}_edges'.format(jobset_id), dump({'edge': edges}))

        # Replicate the React Flow chart in Python's networkx
        convert_reactflow_to_networkx = reactflow_to_networkx(elems, edges)

        # get topological sorting from reactflow_to_networx function imported from flojoy package
        topological_sorting = list(
            convert_reactflow_to_networkx['topological_sort'])

        nodes_by_id = convert_reactflow_to_networkx['getNode']()

        DG = convert_reactflow_to_networkx['DG']

        edge_info = convert_reactflow_to_networkx['edgeInfo']

        graph = Graph(DG, edge_info)
        visited = [False] * len(list(DG.nodes))

        # finding the source of dfs tree
        dfs_source = []
        for node in DG.nodes:
            if len(list(DG.predecessors(node))) == 0:
                dfs_source.append(node)

        hash_map = {}
        current_loop_nodes = []
        for source in dfs_source:
            DFS(graph=graph, source=source, visited=visited,
                current_loop_nodes=current_loop_nodes, hashmap=hash_map, get_node_data_by_id=nodes_by_id)

        hash_map_by_loop = get_hash_loop(hash_map, nodes_by_id, DG)
        loop_body_nodes = get_loop_body_nodes(
            hash_map, hash_map_by_loop.copy())

        loop_nodes = defaultdict()
        enqued_job_list = []
        loop_ongioing_list = []
        redis_env = ""
        current_conditional = ""

        r.set(jobset_id, dump({}))

        print('\n')
        print('All Nodes in topological sorting:')
        print('\n')
        topological_sorting_by_node_id = {}
        for node_serial in topological_sorting:
            id = nodes_by_id[node_serial]['id']
            if node_serial not in topological_sorting_by_node_id:
                topological_sorting_by_node_id[id] = node_serial
            print(node_serial, nodes_by_id[node_serial]
                  ['cmd'], id)

        while len(topological_sorting) != 0:
            print("Topological Order: ", topological_sorting)
            node_serial = topological_sorting.pop(0)
            cmd = nodes_by_id[node_serial]['cmd']
            func = getattr(globals()[cmd], cmd)
            ctrls = nodes_by_id[node_serial]['ctrls']
            node_id = nodes_by_id[node_serial]['id']

            print("Node ID: ", node_id)
            print("\n")

            job_id = node_id
            s = ' '.join([STATUS_CODES['JOB_IN_RQ'], cmd.upper()])
            jobset_data = job_service.get_redis_obj(jobset_id)
            prev_jobs = job_service.get_redis_obj(all_jobs_key)

            special_type_jobs = jobset_data.get(
                'SPECIAL_TYPE_JOBS', {})  # TODO: rename SPECIAL_TYPE_JOBS

            is_eligible_to_enqueue = False  # TODO: Check if it is necessary

            # current_loop = loop_ongioing_list[len(loop_ongioing_list)-1] if len(loop_ongioing_list) > 0 else ""

            is_part_of_loop, is_part_of_loop_body, is_part_of_loop_end, is_eligible = check_loop_type(
                node_serial, cmd, node_id, edge_info, DG, jobset_data)

            if is_part_of_loop:

                if is_part_of_loop_body:
                    is_eligible_to_enqueue = True
                    # loop_nodes[current_loop].append(
                    #     node_serial) if node_serial not in loop_nodes[current_loop] and is_part_of_loop_body else node_serial

                elif is_part_of_loop_end:
                    is_eligible_to_enqueue = is_eligible
                    # loop_nodes[current_loop] = []
                    # if cmd == 'LOOP' and ('LOOP' not in special_type_jobs):
                    #     is_eligible_to_enqueue = True
                    #     loop_nodes[current_loop] = []

                    # elif len(special_type_jobs) == 0:
                    #     is_eligible_to_enqueue = True
                    #     loop_nodes[current_loop] = []

            else:

                is_eligible_to_enqueue = check_if_default_node_part_of_loop(
                    node_serial, enqued_job_list, DG)

                if is_eligible_to_enqueue:
                    # loop_nodes[current_loop].append(
                    #     node_serial) if node_serial not in loop_nodes[current_loop] else node_serial
                    pass
            if is_eligible_to_enqueue != True:
                print("Skipping: ", node_id)

            if len(special_type_jobs):

                if 'LOOP' in special_type_jobs:
                    loop_jobs = special_type_jobs['LOOP'].copy()

                    # current_loop = loop_ongioing_list[len(loop_ongioing_list)-1]
                    # if cmd == 'LOOP' and node_id != current_loop: # integrating nested loop feature
                    #     topological_sorting.append(node_serial)
                    #     continue

                    # if cmd != 'CONDITIONAL':
                    #     if cmd == 'LOOP' and node_id not in loop_jobs:

                    #         conditional_node_id = get_conditional_node_id(node_id,loop_body_nodes)
                    #         intial_value = cmd+"_"+nodes_by_id[node_serial]['label']+"_initial_count"
                    #         total_iteration = cmd + "_"+nodes_by_id[node_serial]['label']+"_iteration_count"
                    #         step = cmd + "_"+ nodes_by_id[node_serial]['label']+"_step"

                    #         loop_job = {
                    #             node_id: {
                    #                 "status": "ongoing",
                    #                 "is_loop_body_execution_finished": False,
                    #                 "params": {
                    #                     "initial_value": int(ctrls[intial_value]['value']),
                    #                     "total_iterations": int(ctrls[total_iteration]["value"]),
                    #                     "current_iteration": int(ctrls[intial_value]['value']), # TODO: Identify where this is set on each iteration
                    #                     "step": int(ctrls[step]['value'])
                    #                 },
                    #                 "conditional_node":conditional_node_id
                    #             }
                    #         }
                    #         loop_jobs.update(loop_job)
                    #         redis_env = dump({
                    #             **r_obj,'SYSTEM_STATUS':s,
                    #             'SPECIAL_TYPE_JOBS':{
                    #                 'LOOP':loop_jobs
                    #             }
                    #         })

                    #     else:
                    #         redis_env = dump({
                    #             **r_obj, 'SYSTEM_STATUS': s,
                    #             'SPECIAL_TYPE_JOBS': {
                    #                 **special_type_jobs,
                    #             }
                    #         })
                    # else:
                    #     check_inputs = True if len(
                    #         nodes_by_id[node_serial]['inputs']) else False

                    #     if check_inputs:
                    #         redis_env = dump({
                    #             **r_obj, 'SYSTEM_STATUS': s,
                    #             'SPECIAL_TYPE_JOBS': {
                    #                 **special_type_jobs,
                    #                 'CONDITIONAL': {
                    #                     "direction": True
                    #                 }
                    #             }
                    #         })
                    #         current_conditional = node_id
                    #     else:
                    #         redis_env = dump({
                    #             **r_obj, 'SYSTEM_STATUS': s,
                    #             'SPECIAL_TYPE_JOBS': {
                    #                 **special_type_jobs,
                    #             }
                    #         })
                    #         if is_eligible_to_enqueue:
                    #             loop_serial_id = find_loop_serial_id(node_id,loop_body_nodes,topological_sorting_by_node_id)
                    #             topological_sorting = [loop_serial_id] + topological_sorting

                    if cmd == 'LOOP' and node_id in special_type_jobs['LOOP']:

                        print(jobset_data)

                        if len(special_type_jobs['LOOP']) and special_type_jobs['LOOP'][node_id]['status'] == 'ongoing':
                            loop_nodes = get_loop_nodes(
                                node_id, hash_map_by_loop, topological_sorting_by_node_id)
                            topological_sorting = loop_nodes + topological_sorting
                        else:
                            del loop_jobs[node_id]

                            redis_env = dump({
                                **jobset_data, 'SYSTEM_STATUS': s,
                                'SPECIAL_TYPE_JOBS': {} if len(loop_jobs) == 0 else {'LOOP': loop_jobs}
                            })

                if 'CONDITIONAL' in special_type_jobs:
                    direction = special_type_jobs['CONDITIONAL']['direction']

                    status = is_eligible_on_condition(node_serial=node_serial, direction=direction,
                                                      DG=DG, edge_info=edge_info, get_job_id=get_job_id, all_job_key=all_jobs_key,
                                                      current_conditional=current_conditional)

                    if not status:
                        continue

                    # if cmd == 'LOOP':

                    #     intial_value = cmd+"_"+nodes_by_id[node_serial]['label']+"_initial_count"
                    #     total_iteration = cmd + "_"+nodes_by_id[node_serial]['label']+"_iteration_count"
                    #     step = cmd + "_"+ nodes_by_id[node_serial]['label']+"_step"

                    #     loop_jobs = {
                    #             node_id:{
                    #             "status": "ongoing",
                    #             "is_loop_body_execution_finished": False,
                    #             "params": {
                    #                 "initial_value": int(ctrls[intial_value]['value']),
                    #                 "total_iterations": int(ctrls[total_iteration]["value"]),
                    #                 "current_iteration": int(ctrls[intial_value]['value']),
                    #                 "step": int(ctrls[step]['value'])
                    #             }
                    #         }
                    #     }

                    #     redis_env = dump({
                    #         **r_obj, 'SYSTEM_STATUS': s,
                    #         'SPECIAL_TYPE_JOBS': {
                    #             'LOOP': loop_jobs
                    #         }
                    #     })

                    #     loop_ongioing_list.append(node_id)
                    #     loop_nodes[node_id] = []
                    #     # topological_sorting.append(node_serial)

                    if cmd == 'CONDITIONAL':
                        check_inputs = True if len(
                            nodes_by_id[node_serial]['inputs']) else False

                        if check_inputs:
                            redis_env = dump({
                                **jobset_data, 'SYSTEM_STATUS': s,
                                'SPECIAL_TYPE_JOBS': {
                                    **special_type_jobs,
                                    'CONDITIONAL': {
                                        "direction": True
                                    }
                                }
                            })
                            current_conditional = node_id
                        else:
                            redis_env = dump({
                                **jobset_data, 'SYSTEM_STATUS': s,
                                'SPECIAL_TYPE_JOBS': {
                                    **special_type_jobs,
                                }
                            })
                    else:
                        redis_env = dump({
                            **jobset_data, 'SYSTEM_STATUS': s,
                            'SPECIAL_TYPE_JOBS': {
                                **special_type_jobs
                            }
                        })

            else:
                if cmd == 'LOOP':
                    conditional_node_id = get_conditional_node_id(
                        node_id, loop_body_nodes)

                    intial_value = cmd+"_" + \
                        nodes_by_id[node_serial]['label']+"_initial_count"
                    total_iteration = cmd + "_" + \
                        nodes_by_id[node_serial]['label']+"_iteration_count"
                    step = cmd + "_" + \
                        nodes_by_id[node_serial]['label']+"_step"

                    loop_jobs = {
                        node_id: {
                            "status": "ongoing",
                            "is_loop_body_execution_finished": False,
                            "params": {
                                "initial_value": int(ctrls[intial_value]['value']),
                                "total_iterations": int(ctrls[total_iteration]["value"]),
                                "current_iteration": int(ctrls[intial_value]['value']),
                                "step": int(ctrls[step]['value'])
                            },
                            "conditional_node": conditional_node_id
                        }
                    }

                    redis_env = dump({
                        **jobset_data, 'SYSTEM_STATUS': s,
                        'SPECIAL_TYPE_JOBS': {
                            **special_type_jobs,
                            'LOOP': loop_jobs
                        }
                    })

                    loop_ongioing_list.append(node_id)
                    loop_nodes[node_id] = []
                    # topological_sorting.append(node_serial)

                elif cmd == 'CONDITIONAL':
                    conditional_jobs = {
                        "direction": True
                    }

                    redis_env = dump({
                        **jobset_data, 'SYSTEM_STATUS': s,
                        'SPECIAL_TYPE_JOBS': {
                            **special_type_jobs,
                            'CONDITIONAL': conditional_jobs
                        }
                    })
                    current_conditional = node_id
                else:
                    redis_env = dump({
                        **jobset_data, 'SYSTEM_STATUS': s,
                        "SPECIAL_TYPE_JOBS": {
                            **special_type_jobs
                        }
                    })

            if is_eligible_to_enqueue:

                '''Enqueue'''
                if len(list(DG.predecessors(node_serial))) == 0:

                    q.enqueue(func,
                              job_timeout='3m',
                              on_failure=report_failure,
                              job_id=job_id,
                              kwargs={'ctrls': ctrls, 'jobset_id': jobset_id,
                                      'node_id': nodes_by_id[node_serial]['id']},
                              result_ttl=500)
                    enqued_job_list.append(node_serial)

                else:
                    # loop_node_list = [] if loop_nodes == defaultdict() else loop_nodes[current_loop]
                    previous_job_ids = get_previous_job_ids(cmd=cmd, DG=DG, get_job_id=get_job_id, loop_nodes=loop_body_nodes,
                                                            node_id=node_id, node_serial=node_serial, nodes_by_id=nodes_by_id,
                                                            r_obj=jobset_data, all_jobs_key=all_jobs_key)

                    print("previous Jobs Ids: ", previous_job_ids)

                    q.enqueue(func,
                              job_timeout='3m',
                              on_failure=report_failure,
                              job_id=job_id,
                              kwargs={'ctrls': ctrls,
                                      'previous_job_ids': previous_job_ids,
                                      'jobset_id': jobset_id, 'node_id': nodes_by_id[node_serial]['id']},
                              depends_on=previous_job_ids,
                              result_ttl=500)
                    enqued_job_list.append(node_serial)

                    # if cmd == 'LOOP' and current_loop == node_id and json.loads(redis_env)['SPECIAL_TYPE_JOBS'] == {}:
                    #     del loop_nodes[current_loop]
                    #     loop_ongioing_list.pop()

                r.set(jobset_id, redis_env)
                r.set(all_jobs_key, dump({
                    **prev_jobs, str(cmd)+str(node_id): job_id
                }))
                r.lpush('{}_ALL_NODES'.format(jobset_id), node_id)
                if cmd == 'CONDITIONAL':
                    # if is_part_of_loop:
                    while True:
                        job = Job.fetch(job_id, connection=r)
                        if job.get_status() == 'finished':
                            break
            else:
                check = check_pred_exist_in_current_queue(
                    topological_sorting, enqued_job_list, node_serial, DG)

                if check:
                    topological_sorting.append(node_serial)
        r.lrem('{}_watch'.format(jobset_id), 1, my_job_id)
        return
    except Exception:
        send_to_socket({
            'jobsetId': jobset_id,
            'SYSTEM_STATUS': 'Failed to run Flowchart script on worker... ',
        })
        print('Watch.py run error: ', Exception, traceback.format_exc())


def run(**kwargs):
    jobset_id = kwargs['jobsetId']
    print('running flojoy for jobset id: ', jobset_id)
    try:
        fc = kwargs['fc']
        flojoy_watch_job_id = kwargs['flojoy_watch_job_id']

        elems = fc['nodes']
        edges = fc['edges']

        job_service.add_to_redis_obj(f'{jobset_id}_edges', {'edge': edges})

        # Replicate the React Flow chart in Python's networkx
        networkx_obj = reactflow_to_networkx(elems, edges)
        topological_sorting = list(networkx_obj['topological_sort'])
        node_dict = networkx_obj['getNode']()
        DG = networkx_obj['DG']
        edge_info = networkx_obj['edgeInfo']
        
        preprocess_graph(DG=DG, edge_info=edge_info, node_dict=node_dict)
        print(" conditional output nodes: ", conditional_nodes)
        
        for node in conditional_nodes.items():
            for child_ids in node.items():
                for child_id in child_ids:
                    try:
                        topological_sorting.remove(child_id)
                    except Exception:
                        pass
            
        
        while len(topological_sorting) != 0:
            print("Topological Order: ", topological_sorting)
            node_serial = topological_sorting.pop(0)
            cmd = node_dict[node_serial]['cmd']
            func = getattr(globals()[cmd], cmd)
            ctrls = node_dict[node_serial]['ctrls']
            job_id = node_id = node_dict[node_serial]['id']
            # s = ' '.join([STATUS_CODES['JOB_IN_RQ'], cmd.upper()])
            # jobset_data = job_service.get_jobset_data(jobset_id)
            # prev_jobs = job_service.get_redis_obj(KEY_ALL_JOBEST_IDS)
            previous_job_ids = get_previous_job_ids(DG=DG, node_serial=node_serial)
            
            job_service.enqueue_job(
                func=func,
                jobset_id=jobset_id,
                job_id=job_id,
                previous_job_ids=previous_job_ids,
                ctrls=ctrls
            )
            job_service.add_job(job_id=job_id, jobset_id=jobset_id)
            if cmd == 'CONDITIONAL':
                job_result={}
                while True:
                    job = job_service.fetch_job(job_id=job_id)
                    if job.get_status() == 'finished':
                        job_result = job.result
                        break
                print(" conditional result: ", job_result)
                direction = job_result.get("direction")
                nodes_to_enqueue = conditional_nodes[node_id][direction]
                topological_sorting = nodes_to_enqueue + topological_sorting
                

        notify_jobset_finished(jobset_id, flojoy_watch_job_id)
        return
    except Exception:
        send_to_socket({
            'jobsetId': jobset_id,
            'SYSTEM_STATUS': 'Failed to run Flowchart script on worker... ',
        })
        print('Watch.py run error: ', Exception, traceback.format_exc())


def notify_jobset_finished(jobset_id, my_job_id):
    job_service.redis_dao.remove_item_from_list('{}_watch'.format(jobset_id), my_job_id)

def preprocess_graph(DG, edge_info, node_dict):
    graph = Graph(DG, edge_info)
    visited = [False] * len(list(DG.nodes))

    # finding the source of dfs tree
    dfs_source = []
    for node in DG.nodes:
        if len(list(DG.predecessors(node))) == 0:
            dfs_source.append(node)

    hash_map = {}
    current_loop_nodes = []
    for source in dfs_source:
        DFS(graph=graph, source=source, visited=visited,
            current_loop_nodes=current_loop_nodes, hashmap=hash_map, get_node_data_by_id=node_dict)

    hash_map_by_loop = get_hash_loop(hash_map, node_dict, DG)
    loop_body_nodes = get_loop_body_nodes(
        hash_map, hash_map_by_loop.copy())


   
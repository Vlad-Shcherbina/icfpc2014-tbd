import logging

import json
import requests
import pprint

log = logging.getLogger(__name__)

def run_do(map, lm_ai, ghost_ais, url):
  return json.loads(
    requests.post(url, data=json.dumps({'map': map, 'lambda': lm_ai, 'ghost_ais': ghost_ais})).text )


def run(map, lm_ai, ghost_ais):
  return run_do(map, lm_ai, ghost_ais, 'http://localhost:52014/run')

def run_maze(map, lm_ai, ghost_ais): 
  return run_do(map, lm_ai, ghost_ais, 'http://localhost:52014/run/maze')

def run_stats(map, lm_ai, ghost_ais): 
  return run_do(map, lm_ai, ghost_ais, 'http://localhost:52014/run/stats')

if __name__ == "__main__":
  logging.basicConfig(level=logging.WARNING)
  log.setLevel(logging.DEBUG)
  pp = pprint.PrettyPrinter(indent=2)
  map = """#########
#\.o.=..#
#.      #
#########
"""
  lm_ai = """LDC  0
LDF  4
CONS
RTN
LDC  0
LDC  1
CONS
RTN
"""
  ghost_ais=["""mov a,255  
mov b,0    
mov c,255  
           
inc c      
jgt 7,[c],a
           
mov a,[c]  
mov b,c    
jlt 3,c,3  

mov a,b    
int 0

int 3      
int 6      
inc [b]    
hlt"""]
  log.debug(pp.pformat(run_maze(map, lm_ai, ghost_ais)))

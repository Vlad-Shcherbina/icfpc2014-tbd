refc: icfpc-2014 reference implementation client
===

Dependencies:

```
pacman -S phantomjs
pip2 install tornado requests
```

Running:

```
setsid python2 ./server.py
setsid phantomjs ./phucking.js http://localhost:62014
```

Getting data:
```
POST json with fields "map", "lambda" and at least "g1ai" (AI for the first ghost)
to either 

 + http://localhost:52014/run (gives all the details for each step: maze state, ticks, score, lives and final internal state)
 + http://localhost:52014/run/maze (gives maze and statistics for each step)
 + http://localhost:52014/run/stats (gives only statistics: ticks, score, lives)

TODO:
 + Client for LMCPU simul

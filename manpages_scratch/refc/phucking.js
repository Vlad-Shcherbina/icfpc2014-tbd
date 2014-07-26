var page = require('webpage').create()
var server = require('webserver').create()
var system = require('system')
var port = 52014
var url
if (system.args.length !== 2) {
  console.log('Usage: phucking.js target_url')
  phantom.exit(1)
}
g_page = page.open(url, function(status) {
});

var run_handle = function(req, res) {
  return run_handle_do(["maze", "state", "final"], req, res)
}

var runmaze_handle = function(req, res) {
  return run_handle_do(["maze", "state"], req, res)
}

var runstats_handle = function(req, res) {
  return run_handle_do(["state"], req, res)
}

var run_handle_do = function(interests, req, res) {
  var handle_do = function(interests, post, res) {
    if(!post.map || !post.lambda || !post.ghost_ais || post.ghost_ais.length === 0) {
      throw "Not enough keys"
    }
    try {
      page.open(url, function() {
        var bigdata = page.evaluate(function(args) {
          var interests = args.interests
          var post      = args.post
          var result    = []
          document.getElementById('map').value = post.map
          document.getElementById('lambda').value = post.lambda
          
          document.getElementById('g1ai').value = post.ghost_ais[0]
          if(post.ghost_ais[1]) { document.getElementById('g2ai').value = post.ghost_ais[1]; }
          if(post.ghost_ais[2]) { document.getElementById('g3ai').value = post.ghost_ais[2]; }
          if(post.ghost_ais[3]) { document.getElementById('g4ai').value = post.ghost_ais[3]; }
          load()
          if(document.getElementById('status').textContent !== "Program Loaded") {
            return document.getElementById('status').textContent
          }
          while(!state.gameOver && !state.gameWin) {
            dump = {}
            step();
            if(interests.indexOf('maze') >= 0) {
              dump['maze'] = document.getElementById('maze').textContent;
            }
            if(interests.indexOf('state') >= 0) {
              var stateString = '{"' + document.getElementById('state').textContent . trim()
                                                                                   . replace(/\n/g, ',')
                                                                                   . replace(/\s/g, '')
                                                                                   . replace(/,/g,  ',"')
                                                                                   . replace(/:/g,  '":')
                                    + '}'; // кто упоротый, я упоротый?
              var stateJson   = JSON.parse(stateString)
              dump['state']   = stateJson
            }
            result.push(dump)
          }
          if(interests.indexOf('final') >= 0) {
            return {result: result, final: state};
          } else {
            return {result: result};
          }
        }, {post: post, interests: interests})
        res.statusCode = 200
        res.write(JSON.stringify(bigdata))
        res.close()
        return
      })
    } catch (_e) {
      res.statusCode = 404
      res.write(JSON.stringify({error: "Expected properly formed POST, got some bullshit"}))
      res.close()
      return
    }
  }
  try {
    var postJson = JSON.parse(req.post.trim())
    handle_do(interests, postJson, res)
  } catch(_e) {
    res.statusCode = 404
    res.write(JSON.stringify({error: "Expected POST containing JSON having keys -- map: lambda: g1ai: [g2ai: g3ai: g4ai:]"}))
    res.close()
    return
  }
}

var echo_handle = function(req, res) {
  res.statusCode = 200
  reqQuoted = JSON.stringify(req, null, 4)
  res.write('<pre>' + reqQuoted + '</pre>')
  res.close()
  return
}

url = system.args[1] + '/game.html'
console.log('Opening ', url) 
var listening = server.listen(port, function(req, res) {
  res.headers = {"Cache": "no-cache", "Content-Type": "text/json"}
  if(req.method === "POST" || true) {
    var phi = req.url.replace(/\W/g, '') + '_handle'
    try {
      if(typeof(eval(phi)) === 'function') {
        eval(phi + '(req, res)')
      }
    } catch(_e) {
      res.statusCode = 404
      res.write(JSON.stringify({error: "No such function"}))
      res.close()
    }
  } else {
    res.statusCode = 404
    res.write(JSON.stringify({error: "Expected properly formed POST, got some bullshit"}))
    res.close()
  }
})
if (!listening) {
  console.log("Can't start a server on port " + port);
  phantom.exit();
}

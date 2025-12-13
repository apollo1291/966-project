
var ALL_FEATURES = [
    "circle", "square",
    "red", "blue",
    "solid", "striped",
    "big", "small"
  ];
  
  var featureDim = function(f) {
    if (f === "circle" || f === "square") return "shape";
    if (f === "red" || f === "blue") return "color";
    if (f === "solid" || f === "striped") return "fill";
    if (f === "big" || f === "small") return "size";
  };
  
  var featureSatisfied = function(f, obj) {
    return (obj.shape === f ||
            obj.color === f ||
            obj.fill  === f ||
            obj.size  === f);
  };
  
  var predicts = function(h, obj) {
    return _.every(h, function(f) {
      return featureSatisfied(f, obj);
    });
  };
  
  
  var LAMBDA = 0.7;
  var NOISE  = 0.05;
  
  var logPrior = function(h) {
    return -LAMBDA * h.length;
  };
  
  var logLikelihood = function(h, examples, objectsById) {
    return _.sum(examples, function(ex) {
      var obj = objectsById[ex.object_id];
      var pred = predicts(h, obj) ? 1 : 0;
      return (pred === ex.label)
        ? Math.log(1 - NOISE)
        : Math.log(NOISE);
    });
  };
  
  var logPosterior = function(h, examples, objectsById) {
    return logPrior(h) + logLikelihood(h, examples, objectsById);
  };
  

  
  var usedDims = function(h) {
    return _.uniq(_.map(h, featureDim));
  };
  
  var availableAddFeatures = function(h) {
    var dims = usedDims(h);
    return _.filter(ALL_FEATURES, function(f) {
      return (!_.contains(h, f) &&
              !_.contains(dims, featureDim(f)));
    });
  };
  
  var propose = function(h, pAdd) {
    var adds = availableAddFeatures(h);
    var removes = h;
  
    if (adds.length === 0 && removes.length === 0) {
      return {h: h, move: "none"};
    }
  
    var doAdd;
    if (adds.length === 0) {
      doAdd = false;
    } else if (removes.length === 0) {
      doAdd = true;
    } else {
      doAdd = flip(pAdd);
    }
  
    if (doAdd) {
      var f = uniformDraw(adds);
      return {h: h.concat([f]), move: "additive"};
    } else {
      var f = uniformDraw(removes);
      return {
        h: _.without(h, f),
        move: "subtractive"
      };
    }
  };
  
  
  var runChain = function(trial, pAdd, steps, temperature, objectsById) {
  
    var h = trial.hypothesis.slice();
    var lp = logPosterior(h, trial.examples, objectsById);
  
    repeat(steps, function() {
      var prop = propose(h, pAdd);
      if (prop.move === "none") { return; }
  
      var lp2 = logPosterior(prop.h, trial.examples, objectsById);
      var delta = (lp2 - lp) / temperature;
  
      if (flip(Math.min(1, Math.exp(delta)))) {
        h = prop.h;
        lp = lp2;
      }
    });
  
    var removed = _.difference(trial.hypothesis, h);
    var added   = _.difference(h, trial.hypothesis);
  
    var responseType =
      (removed.length > 0 && added.length === 0) ? "subtractive" :
      (added.length > 0 && removed.length === 0) ? "additive" :
      (added.length > 0 && removed.length > 0) ? "mixed" :
      "nochange";
  
    return responseType;
  };
  

  var runExperiment = function(trials, objectsById,
                              pAdd, steps, temperature, numChains) {
  
    return _.flatten(_.map(trials, function(trial) {
      return repeat(numChains, function() {
        return runChain(trial, pAdd, steps, temperature, objectsById);
      });
    }));
  };
  

  
  var BASELINE = runExperiment(trials, objectsById,
                               0.5, 500, 1.0, 50);
  
  var CUEING = _.map([0.1,0.3,0.5,0.7,0.9], function(p) {
    return runExperiment(trials, objectsById,
                         p, 500, 1.0, 30);
  });
  
  var COG_LOAD_STEPS = _.map([50,150,300,500,800], function(s) {
    return runExperiment(trials, objectsById,
                         0.5, s, 1.0, 30);
  });
  
  var COG_LOAD_TEMP = _.map([1.0,1.5,2.0,3.0], function(t) {
    return runExperiment(trials, objectsById,
                         0.5, 500, t, 30);
  });
  
  
  {
    baseline: BASELINE,
    cueing: CUEING,
    cogSteps: COG_LOAD_STEPS,
    cogTemp: COG_LOAD_TEMP
  }
  
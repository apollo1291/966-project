import React, { useState, useEffect } from 'react';
import './App.css';
import stimuliData from './stimuli.json';
import WelcomeScreen from './components/WelcomeScreen';
import TrialScreen from './components/TrialScreen';
import EndScreen from './components/EndScreen';

function App() {
  const [currentScreen, setCurrentScreen] = useState('welcome'); // 'welcome', 'trial', 'end'
  const [currentTrialIndex, setCurrentTrialIndex] = useState(0);
  const [responses, setResponses] = useState([]);
  const [trialStartTime, setTrialStartTime] = useState(null);
  const [selectedTrials, setSelectedTrials] = useState([]);

  const { objects, trials: allTrials } = stimuliData;

  // Function to randomly select and shuffle trials
  const selectRandomTrials = (allTrials, numTrials = null) => {
    const shuffled = [...allTrials].sort(() => Math.random() - 0.5);
    // If numTrials is specified, select that many; otherwise use all trials in random order
    return numTrials ? shuffled.slice(0, numTrials) : shuffled;
  };

  // Function to determine condition based on trial position
  const getTrialCondition = (trialIndex) => {
    if (trialIndex >= 0 && trialIndex <= 2) return 'normal';
    if (trialIndex >= 3 && trialIndex <= 5) return 'time_pressure';
    if (trialIndex >= 6 && trialIndex <= 8) return 'add_subtract_reminder';
    return 'normal'; // fallback
  };

  const currentTrial = selectedTrials[currentTrialIndex];
  const currentCondition = getTrialCondition(currentTrialIndex);

  useEffect(() => {
    if (currentScreen === 'trial') {
      setTrialStartTime(Date.now());
    }
  }, [currentScreen, currentTrialIndex]);

  const getResponseType = (responseHypothesis, initialHypothesis) => {
    return responseHypothesis.every(feature => initialHypothesis.includes(feature)) ? 'subtractive' : 'additive';
  };

  const startExperiment = () => {
    // Randomly select trials for this participant
    const randomTrials = selectRandomTrials(allTrials);
    setSelectedTrials(randomTrials);

    setCurrentScreen('trial');
    setCurrentTrialIndex(0);
    setResponses([]);
  };

  const submitTrialResponse = (responseHypothesis, rawFeatureChoices) => {
    const reactionTime = Date.now() - trialStartTime;

    const responseData = {
      trial_id: currentTrial.id,
      initial_hypothesis: currentTrial.hypothesis,
      response_hypothesis: responseHypothesis,
      response_type: getResponseType(responseHypothesis, currentTrial.hypothesis),
      condition: currentCondition,
      raw_feature_choices: rawFeatureChoices,
      rt_ms: reactionTime,
      timestamp: new Date().toISOString()
    };

    setResponses(prev => [...prev, responseData]);

    // Move to next trial or end screen
    if (currentTrialIndex < selectedTrials.length - 1) {
      setCurrentTrialIndex(prev => prev + 1);
    } else {
      setCurrentScreen('end');
    }
  };


  const renderCurrentScreen = () => {
    switch (currentScreen) {
      case 'welcome':
        return <WelcomeScreen onStart={startExperiment} />;
      case 'trial':
        return (
          <TrialScreen
            trial={currentTrial}
            condition={currentCondition}
            objects={objects}
            onSubmit={submitTrialResponse}
          />
        );
      case 'end':
        return <EndScreen responses={responses} />;
      default:
        return null;
    }
  };

  return (
    <div className="App">
      {renderCurrentScreen()}
    </div>
  );
}

export default App;

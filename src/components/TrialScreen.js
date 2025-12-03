import React, { useState } from 'react';
import HypothesisDisplay from './HypothesisDisplay';
import ObjectGrid from './ObjectGrid';
import HypothesisEditor from './HypothesisEditor';
import Timer from './Timer';

function TrialScreen({ trial, condition, objects, onSubmit }) {
  const [featureChoices, setFeatureChoices] = useState({
    shape: [],
    color: [],
    fill: [],
    size: []
  });
  const [timeExpired, setTimeExpired] = useState(false);

  const handleFeatureChange = (dimension, value) => {
    setFeatureChoices(prev => ({
      ...prev,
      [dimension]: value
    }));
  };

  const handleSubmit = () => {
    // Convert feature choices to hypothesis array with OR logic
    const responseHypothesis = Object.entries(featureChoices)
      .filter(([key, selections]) => selections.length > 0)
      .flatMap(([key, selections]) => selections);

    onSubmit(responseHypothesis, featureChoices);

    // Clear selections and scroll to top
    setFeatureChoices({
      shape: [],
      color: [],
      fill: [],
      size: []
    });
    setTimeExpired(false);
    window.scrollTo(0, 0);
  };

  const handleTimeUp = () => {
    setTimeExpired(true);
    // Auto-submit when time runs out
    setTimeout(() => {
      handleSubmit();
    }, 500); // Small delay to show time expired state
  };

  // Get objects for this trial
  const trialObjects = trial.examples.map(example => {
    const obj = objects.find(o => o.id === example.object_id);
    return {
      ...obj,
      label: example.label
    };
  });

  return (
    <div className="screen trial-screen">
      {condition === 'time_pressure' && (
        <Timer
          duration={30}
          onTimeUp={handleTimeUp}
          isActive={!timeExpired}
        />
      )}

      <div className="trial-content">
        <div className="trial-header">
          <h2>Trial {trial.id}</h2>
        </div>

        {condition === 'add_subtract_reminder' && (
          <div className="add-subtract-reminder">
            <h4>Remember:</h4>
            <p>You can both ADD new features and SUBTRACT existing features from the hypothesis!</p>
          </div>
        )}

        <HypothesisDisplay hypothesis={trial.hypothesis} />

        <div className="examples-section">
          <h3>Examples:</h3>
          <ObjectGrid objects={trialObjects} />
        </div>

        <div className="editor-section">
          <h3>Revise the hypothesis:</h3>
          {timeExpired && (
            <div style={{ color: 'red', fontWeight: 'bold', marginBottom: '10px' }}>
              Time's up! Submitting your current response...
            </div>
          )}
          <HypothesisEditor
            featureChoices={featureChoices}
            onFeatureChange={handleFeatureChange}
          />
        </div>

        <button
          className="submit-button"
          onClick={handleSubmit}
          disabled={timeExpired}
        >
          {timeExpired ? 'Submitting...' : 'Submit Response'}
        </button>
      </div>
    </div>
  );
}

export default TrialScreen;

import React from 'react';

function HypothesisDisplay({ hypothesis }) {
  const hypothesisText = hypothesis.join(' AND ');

  return (
    <div className="hypothesis-display">
      <h3>Initial Hypothesis:</h3>
      <div className="hypothesis-text">
        {hypothesisText}
      </div>
    </div>
  );
}

export default HypothesisDisplay;

import React from 'react';

function HypothesisEditor({ featureChoices, onFeatureChange }) {
  const featureOptions = {
    shape: ['circle', 'square'],
    color: ['red', 'blue'],
    fill: ['solid', 'striped'],
    size: ['big', 'small']
  };

  const handleCheckboxChange = (dimension, value) => {
    const currentSelections = featureChoices[dimension] || [];
    let newSelections;

    if (currentSelections.includes(value)) {
      // Remove the value if it's already selected
      newSelections = currentSelections.filter(item => item !== value);
    } else {
      // Add the value if it's not selected
      newSelections = [...currentSelections, value];
    }

    onFeatureChange(dimension, newSelections);
  };

  return (
    <div className="hypothesis-editor">
      {Object.entries(featureOptions).map(([dimension, options]) => (
        <div key={dimension} className="feature-group">
          <h4>{dimension.charAt(0).toUpperCase() + dimension.slice(1)}:</h4>
          <div className="checkbox-options">
            {options.map(option => (
              <label key={option} className="checkbox-label">
                <input
                  type="checkbox"
                  name={dimension}
                  value={option}
                  checked={(featureChoices[dimension] || []).includes(option)}
                  onChange={() => handleCheckboxChange(dimension, option)}
                />
                {option}
              </label>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default HypothesisEditor;

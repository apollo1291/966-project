import React from 'react';

function WelcomeScreen({ onStart }) {
  return (
    <div className="screen welcome-screen">
      <div className="welcome-content">
        <h1>Concept Learning Experiment</h1>
        <div className="instructions">
          <p>
            In this experiment, you will see a series of trials. Each trial presents:
          </p>
          <ul>
            <li>An initial hypothesis (a logical rule)</li>
            <li>Several example objects, each labeled as either a member or non-member of a category</li>
          </ul>
          <p>
            Your task is to revise the hypothesis to match the examples by selecting the appropriate features.
          </p>
          <p>
            For each feature dimension (shape, color, fill, size), you can select zero, one, or more options.
          </p>
        </div>
        <button className="start-button" onClick={onStart}>
          Start Experiment
        </button>
      </div>
    </div>
  );
}

export default WelcomeScreen;

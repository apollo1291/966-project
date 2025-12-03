import React, { useState } from 'react';

function EndScreen({ responses }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);

  const submitResults = async () => {
    setIsSubmitting(true);
    setSubmitStatus(null);
    const payload = { responses };
    console.log(payload);
    try {
      const response = await fetch('https://apollo1291--concept-learning-backend-submit.modal.run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        setSubmitStatus('success');
      } else {
        console.error('Response status:', response.status);
        const responseText = await response.text();
        console.error('Response text:', responseText);
        throw new Error(`HTTP ${response.status}: ${responseText}`);
      }
    } catch (error) {
      console.error('Submission failed:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="screen end-screen">
      <div className="end-content">
        <h1>Experiment Complete</h1>
        <p>Thank you for participating in this concept learning experiment!</p>
        <p>You completed {responses.length} trial{responses.length !== 1 ? 's' : ''}.</p>

        <div className="submit-section">
          <p>Please submit your results:</p>
          <button
            onClick={submitResults}
            disabled={isSubmitting}
            className="submit-button"
          >
            {isSubmitting ? 'Submitting...' : 'Submit Results'}
          </button>

          {submitStatus === 'success' && (
            <p className="success-message">✓ Results submitted successfully!</p>
          )}

          {submitStatus === 'error' && (
            <p className="error-message">✗ Submission failed. Please try again or contact the experimenter.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default EndScreen;

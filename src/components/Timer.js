import React, { useState, useEffect } from 'react';

function Timer({ duration = 30, onTimeUp, isActive }) {
  const [timeLeft, setTimeLeft] = useState(duration);

  useEffect(() => {
    if (!isActive || timeLeft <= 0) return;

    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          onTimeUp && onTimeUp();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft, isActive, onTimeUp]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimerClass = () => {
    if (timeLeft <= 10) return 'timer timer-warning';
    if (timeLeft <= 20) return 'timer timer-caution';
    return 'timer timer-normal';
  };

  return (
    <div className={getTimerClass()}>
      {formatTime(timeLeft)}
    </div>
  );
}

export default Timer;

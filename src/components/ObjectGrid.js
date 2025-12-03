import React from 'react';
import ObjectCard from './ObjectCard';

function ObjectGrid({ objects }) {
  return (
    <div className="object-grid">
      {objects.map((obj) => (
        <ObjectCard key={obj.id} object={obj} />
      ))}
    </div>
  );
}

export default ObjectGrid;

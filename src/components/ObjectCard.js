import React from 'react';

function ObjectCard({ object }) {
  const { shape, color, fill, size, label } = object;
  const imageName = `${shape}_${color}_${fill}_${size}.png`;

  return (
    <div className="object-card">
      <div className="object-image">
        <img
          src={`/output_images/${imageName}`}
          alt={`${shape} ${color} ${fill} ${size}`}
          style={{ width: '100%', height: 'auto', maxWidth: '150px' }}
        />
      </div>
      <div className={`object-label ${label === 1 ? 'member' : 'non-member'}`}>
        {label === 1 ? '✔ Member' : '✘ Not a member'}
      </div>
    </div>
  );
}

export default ObjectCard;

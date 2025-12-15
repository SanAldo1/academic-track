import React from 'react';

function Header({ onUpdate }) {
  return (
    <header>
      <div>ACADEMIC TRACK</div>
      <div className="header-right">
        <button className="update" onClick={onUpdate}>Update</button>
        <div className="profile">
          <div className="picicon">
            <i className="fas fa-user"></i>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;

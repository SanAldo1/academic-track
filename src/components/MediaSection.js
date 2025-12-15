import React from 'react';

function MediaSection({ events }) {
  return (
    <section className="media">
      <h2 className="mediaheader">Upcoming events</h2>
      <div className="media-grid">
        {events.length > 0 ? (
          events.map(event => (
            <div className="media-card" key={event.id}>
              <h3>{event.category}</h3>
              <div className="card-date">{event.date}</div>
              <p className="card-desc">{event.description}</p>
              <small>Location: {event.location}</small>
            </div>
          ))
        ) : (
          <p className="no-events">No events for subject</p>
        )}
      </div>
    </section>
  );
}

export default MediaSection;

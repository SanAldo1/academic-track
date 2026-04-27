import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [selectedFilters, setSelectedFilters] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [stats, setStats] = useState(null);

  // categories
  const categories = ['Math', 'Computer Science', 'Literature', 'Physics', 'Art'];

  // Fetch events from backend
  useEffect(() => {
    fetchEvents();
    fetchStats();
  }, []);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/events');
      if (!response.ok) throw new Error('Failed to fetch events');
      const data = await response.json();
      
      // Add IDs to events from backend
      const eventsWithIds = data.map((event, index) => ({
        ...event,
        id: index + 1,
        image: event.image || getDefaultImage(event.category)
      }));
      // sort events, check if backend is running
      setEvents(eventsWithIds);
      setError(null);
    } catch (err) {
      console.error('Error fetching events:', err);
      setError('Failed to load events, check backend server is running.');
    } finally {
      setLoading(false);
    }
  };
// Fetch stats from backend
  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/events/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

// Handle update events ------------------------------------------
  const handleUpdate = async () => {
    try {
      setUpdating(true);
      setError(null);
      
      const response = await fetch('http://localhost:5000/api/events/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Refresh events after update
        await fetchEvents();
        await fetchStats();
        alert(`Successfully updated with ${result.events.length} events!`);
      } else {
        throw new Error(result.message || 'Failed to update events');
      }
    } catch (err) {
      console.error('Error updating events:', err);
      alert('Failed to update events. Please check your backend server and try again.');
    } finally {
      setUpdating(false);
    }
  };
// filter changes ------------------------------------------
  const handleFilterChange = (category) => {
    setSelectedFilters(prev => {
      if (prev.includes(category)) {
        return prev.filter(c => c !== category);
      } else {
        return [...prev, category];
      }
    });
  };

  const filteredEvents = events.filter(event => {
    if (selectedFilters.length > 0 && !selectedFilters.includes(event.category)) {
      return false;
    }
    if (searchQuery && !event.description.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  if (loading) {
    return (
      <div className="App">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading events</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header>
        <div className="header-title">
          <h1>ACADEMIC TRACK</h1>
          {stats && (
            <small className="event-count">
              {stats.total} events across {Object.keys(stats.categories).length} categories
            </small>
          )}
        </div>
        <div className="header-right">
          <button 
            className="update" 
            onClick={handleUpdate}
            disabled={updating}
          >
            {updating ? ' Updating' : 'Update Events'}
          </button>
          <div className="profile">
            <div className="picicon">
              <i className="fas fa-user"></i>
            </div>
          </div>
        </div>
      </header>

      <div className="container">
        <section className="media">
          <h2 className="mediaheader">
            Upcoming Events
            {!loading && filteredEvents.length > 0 && (
              <span className="result-count"> ({filteredEvents.length} events)</span>
            )}
          </h2>
          
          {error && (
            <div className="error-message">
              <p>{error}</p>
              <button onClick={fetchEvents} className="retry-button">Retry</button>
            </div>
          )}
          
          <div className="media-grid"> 
            {filteredEvents.length > 0 ? (
              filteredEvents.map(event => (
                <div className="media-card" key={event.id}>
                  <div className="card-image-container">
                    <img 
                      src={event.image} 
                      alt={event.description}
                      className="card-image"
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = '/default-event.PNG';
                      }}
                    />
                    <div className="category-badge">{event.category}</div>
                  </div>
                  <h3>{event.description}</h3>
                  <div className="card-date">📅 {event.date}</div>
                  <p className="card-desc">
                    {event.description.length > 120 
                      ? event.description.substring(0, 120) + '...' 
                      : event.description}
                  </p>
                  <small className="card-location">📍 {event.location}</small>
                  {event.source_url && (
                    <a 
                      href={event.source_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="source-link"
                    >
                      Learn More →
                    </a>
                  )}
                </div>
              ))
            ) : (
              <p className="no-events">No events found. Try different filters or update events.</p>
            )}
          </div>
        </section>

        <aside className="search">
          <h2>Search Events</h2>
          <input 
            type="text" 
            className="searchbox"
            placeholder="Search by description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />

          <div className="searchfilter">
            <div className="filterheader">Filter by Category</div>
            {categories.map((category, index) => (
              <div className="filteroption" key={index}>
                <input 
                  type="checkbox" 
                  id={`category-${index}`}
                  checked={selectedFilters.includes(category)}
                  onChange={() => handleFilterChange(category)}
                />
                <label htmlFor={`category-${index}`}>
                  {category.toUpperCase()}
                  {stats && stats.categories[category] && (
                    <span className="category-count"> ({stats.categories[category]})</span>
                  )}
                </label>
              </div>
            ))}
          </div>

          {stats && (
            <div className="update-info">
              <small>Last updated: {stats.last_update ? new Date(stats.last_update).toLocaleString() : 'Never'}</small>
            </div>
          )}
        </aside>
      </div>

      <footer>
        <p>Academic Track 2025 - Aldo Sanjuan</p>
      </footer>
    </div>
  );
}

export default App;
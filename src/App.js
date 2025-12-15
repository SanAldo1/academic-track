import logo from './logo.svg';
import React, { useState } from 'react';
import './App.css';

function App() {
  const [selectedFilters, setSelectedFilters] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  /*Start of the events */

  const [events, setEvents] = useState([
    { id: 1, category: 'Math', date: 'March 3, 2026', description: 'IU Indianapolis math contest', location: 'IU Indianapolis School of Science' },
    { id: 2, category: 'Computer Science', date: 'November 3, 2025', description: 'CSforGood Competition', location: 'Castle High School' },
    { id: 3, category: 'Literature', date: 'January 21, 2025', description: 'Indiana Statewide Writing Contest', location: 'harrison county library' },
    { id: 4, category: 'Physics', date: 'February 1, 2025', description: 'IU Northwest Science Olympiad 2025', location: 'IU Northwest' },
    { id: 5, category: 'Math', date: 'February 14, 2026', description: 'Indiana MATHCOUNTS', location: 'Purdue University, Fort Wayne' },
    { id: 6, category: 'Computer Science', date: 'November 17, 2025', description: 'IndySCC', location: 'Saint louis' },
  ]);

  const categories = ['Math', 'Computer Science', 'Literature', 'Physics', ];
// filter checkbox changes here
  const handleFilterChange = (category) => {
    setSelectedFilters(prev => {
      if (prev.includes(category)) {
        return prev.filter(c => c !== category);
      } else {
        return [...prev, category];
      }
    });
  };
// filter events based on checkbox and search bar
  const filteredEvents = events.filter(event => {
    if (selectedFilters.length > 0 && !selectedFilters.includes(event.category)) {
      return false;
    }
    if (searchQuery && !event.description.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });
  /* remember to finish actual personal page to update */
  const handleUpdate = () => {
    alert('Updating events');
  };

  return (
    <div className="App">
      <header>
        <div>ACADEMIC TRACK</div>
        <div className="header-right">
          <button className="update" onClick={handleUpdate}>Update</button>
          <div className="profile">
            <div className="picicon">
              <i className="fas fa-user"></i>
            </div>
          </div>
        </div>
      </header>

      <div className="container">
        <section className="media">
          <h2 className="mediaheader">Upcoming events</h2>
          <div className="media-grid"> 
            {/*check for events */}
            {filteredEvents.length > 0 ? (
              filteredEvents.map(event => (
                <div className="media-card" key={event.id}>
                  <h3>{event.category}</h3>
                  <div className="card-date">{event.date}</div>
                  <p className="card-desc">{event.description}</p>
                  <small>Location: {event.location}</small>
                </div>
              ))
            ) : (
              <p className="no-events">No events found. Try different filters.</p>
            )}
          </div>
        </section>

        <aside className="search">
          <h2>Search events</h2>
          {/*SEARCH BAR HERE */}
          <input 
            type="text" 
            className="searchbox"
            placeholder="Search events..."
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
                  checked={selectedFilters.includes(category)} //check category
                  onChange={() => handleFilterChange(category)} //toggle the category when changed
                />
                <label htmlFor={`category-${index}`}>{category.toUpperCase()}</label>
              </div>
            ))}
          </div>
        </aside>
      </div>

      <footer>
        <p>Academic Track 2025 academic events </p>
      </footer>
    </div>
  );
}

export default App;



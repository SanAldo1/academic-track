import React from 'react';

function SearchSidebar({ 
  categories, 
  selectedFilters, 
  onFilterChange, 
  searchQuery, 
  onSearchChange 
}) {
  return (
    /*SEARCH BAR -------------------------------------- */
    <aside className="search">
      <h2>Search events</h2>
      <input 
        type="text" 
        className="searchbox"
        placeholder="Search events..."
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
      /> 
      <div className="searchfilter">
        <div className="filterheader">Filter by Category</div>
        {categories.map((category, index) => (
          <div className="filteroption" key={index}>
            <input 
              type="checkbox" 
              id={`category-${index}`}
              checked={selectedFilters.includes(category)}
              onChange={() => onFilterChange(category)}
            />
            <label htmlFor={`category-${index}`}>{category.toUpperCase()}</label>
          </div>
        ))}
      </div>
    </aside>
  );
}

export default SearchSidebar;
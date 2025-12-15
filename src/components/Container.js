import React from 'react';
import MediaSection from './MediaSection';
import SearchSidebar from './SearchSidebar'; 

function Container({ 
  events, 
  categories, 
  selectedFilters, 
  onFilterChange, 
  searchQuery, 
  onSearchChange 
}) {
  return (
    <div className="container">
      <MediaSection events={events} />
      <SearchSidebar 
        categories={categories}
        selectedFilters={selectedFilters}
        onFilterChange={onFilterChange}
        searchQuery={searchQuery}
        onSearchChange={onSearchChange}
      />
    </div>
  );
}

export default Container;

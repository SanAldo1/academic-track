from asyncio import events
from urllib import response

from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, timedelta
import json
import threading
import time
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AcademicEventScraper:
    def __init__(self):
        self.events = []
        self.last_update = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    # get request
    def safe_request(self, url, timeout=10):
        """Make a safe HTTP request with error handling"""
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None

    def parse_date(self, date_str):
        """Parse various date formats into a standard format"""
        if not date_str:
            return "Date TBD"
        
        # Clean up date string
        date_str = date_str.strip()
        
        # date patterns Ill need
        patterns = [
            # Month DD, YYYY
            (r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}', '%B %d, %Y'),
            # MM/DD/YYYY
            (r'\d{1,2}/\d{1,2}/\d{4}', '%m/%d/%Y'),
            # YYYY-MM-DD
            (r'\d{4}-\d{2}-\d{2}', '%Y-%m-%d'),
            # Month YYYY
            (r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', '%B %Y'),
        ]
        
        for pattern, date_format in patterns:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                try:
                    date_obj = datetime.strptime(match.group(), date_format)
                    return date_obj.strftime('%B %d, %Y')
                except ValueError:
                    continue
        
        # for any date-like string
        date_match = re.search(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', date_str)
        if date_match:
            return date_match.group()
        
        return "Date TBD"

    def scrape_iu_math_contest(self):
        """Scrape IU Math Contest website"""
        events = []
        url = "https://science.indianapolis.iu.edu/math/about/math-contest/index.html"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        text = soup.get_text()
        
        date_patterns = [
            r'(?:March|April|May)\s+\d{1,2},?\s+\d{4}',
            r'(?:Spring|Fall)\s+\d{4}',
        ]
        
        date_found = None
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_found = match.group()
                break
        
        # Get title/description
        title_elem = soup.find('h1') or soup.find('h2')
        description = title_elem.text.strip() if title_elem else "IU Indianapolis Mathematics Contest"
        
        events.append({
            'category': 'Math',
            'date': self.parse_date(date_found) if date_found else 'March 2026',
            'description': 'IU Indianapolis Mathematics Contest - Open to all Indiana high school students',
            'location': 'IU Indianapolis School of Science',
            'source_url': url,
            'image': '/IUphoto.PNG'
        })
        
        return events

    def scrape_indiana_library(self):
        """Scrape Indiana State Library - Letters About Literature"""
        events = []
        url = "https://www.in.gov/library/icb/lal/"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        # Look for deadline dates
        date_pattern = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
        dates = re.findall(date_pattern, text)
        
        events.append({
            'category': 'Literature',
            'date': self.parse_date(dates[0]) if dates else 'January 2026',
            'description': 'Letters About Literature - Indiana State Library Writing Contest',
            'location': 'Indiana State Library',
            'source_url': url,
            'image': '/LAL.PNG'
        })
        
        return events

    def scrape_physics_bowl(self):
        """Scrape AAPT Physics Bowl"""
        events = []
        url = "https://www.aapt.org/Programs/PhysicsBowl/"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        events.append({
            'category': 'Physics',
            'date': 'April 2026',
            'description': 'AAPT Physics Bowl - National physics competition for high school students',
            'location': 'Online/Regional Sites',
            'source_url': url,
            'image': '/AAPT.PNG'
        })
        
        return events

    def scrape_intercompetition(self):
        """Scrape InterCompetition - International competitions"""
        events = []
        url = "https://intercompetition.com"
        
        response = self.safe_request(url)
        if not response:
            # Fallback data 
            events.append({
                'category': 'Computer Science',
                'date': 'Year Round',
                'description': 'InterCompetition - International programming and technology competitions',
                'location': 'Online',
                'source_url': url,
                'image': '/INTER.PNG'
            })
            return events
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for listings
        comp_elements = soup.find_all(['div', 'article', 'section'], 
                                      class_=re.compile(r'competition|event|contest'))
        
        for elem in comp_elements[:5]:  # Limit to first 5 competitions
            title = elem.find(['h2', 'h3', 'h4'])
            date_text = elem.find(class_=re.compile(r'date|time'))
            desc = elem.find('p')
            
            if title:
                events.append({
                    'category': 'Computer Science',
                    'date': self.parse_date(date_text.text if date_text else '') or 'TBD',
                    'description': title.text.strip()[:100],
                    'location': 'Online',
                    'source_url': url,
                    'image': '/default-cs.PNG'
                })
        
        return events

    def scrape_iphyc(self):
        """Scrape International Physics Youth Competition"""
        events = []
        url = "https://iphyc.org/en/index"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        events.append({
            'category': 'Physics',
            'date': 'July 2026',
            'description': 'International Physics Youth Competition (IPhYC) - Global physics competition',
            'location': 'International',
            'source_url': url,
            'image': '/iphyc.PNG'
        })
        
        return events

    def scrape_amc(self):
        """Scrape MAA AMC competitions"""
        events = []
        url = "https://maa.org/student-programs/amc/"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        amc_competitions = [
            {
                'description': 'AMC 8 - Middle school mathematics competition',
                'date': 'January 2026',
            },
            {
                'description': 'AMC 10/12 A - High school mathematics competition',
                'date': 'November 2025',
            },
            {
                'description': 'AMC 10/12 B - High school mathematics competition',
                'date': 'November 2025',
            },
            {
                'description': 'AIME - American Invitational Mathematics Examination',
                'date': 'February 2026',
            }
        ]
        
        for comp in amc_competitions:
            events.append({
                'category': 'Math',
                'date': comp['date'],
                'description': comp['description'],
                'location': 'Local Schools',
                'source_url': url,
                'image': '/MAA.PNG'
            })
        
        return events

    def scrape_lasp(self):
        """Scrape LASP student programs"""
        events = []
        url = "https://lasp.org/student-programs/"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for programs/events
        program_elements = soup.find_all(['div', 'article'], 
                                        class_=re.compile(r'program|event'))
        
        for elem in program_elements[:5]:
            title = elem.find(['h2', 'h3'])
            if title:
                events.append({
                    'category': 'Physics',
                    'date': 'TBD',
                    'description': title.text.strip()[:100],
                    'location': 'LASP',
                    'source_url': url,
                    'image': '/iphyc.PNG'
                })
        
        if not events:
            events.append({
                'category': 'Physics',
                'date': 'Summer 2026',
                'description': 'LASP Student Programs - Space and atmospheric physics research opportunities',
                'location': 'Laboratory for Atmospheric and Space Physics',
                'source_url': url,
                'image': '/iphyc.PNG'
            })
        
        return events

    def scrape_aops_competitions(self):
        """Scrape AoPS list of math competitions"""
        events = []
        url = "https://artofproblemsolving.com/wiki/index.php?title=List_of_United_States_high_school_mathematics_competitions"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for table rows or list items with competition info
        competition_elements = soup.find_all(['tr', 'li'])
        
        for elem in competition_elements[:20]:  # Limit to prevent too many events
            text = elem.get_text().strip()
            if text and len(text) > 10:
                # Extract date if present
                date_match = re.search(r'\b(20\d{2})\b', text)
                if date_match:
                    events.append({
                        'category': 'Math',
                        'date': date_match.group(),
                        'description': text[:150],
                        'location': 'Various Locations',
                        'source_url': url,
                        'image': '/AoPS.PNG'
                    })
        
        return events

    def scrape_icpc(self):
        """Scrape ICPC North America"""
        events = []
        url = "https://ec.na.icpc.global"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        events.append({
            'category': 'Computer Science',
            'date': 'February 2026',
            'description': 'ICPC North America East Central Regional - Collegiate programming competition',
            'location': 'Regional Sites',
            'source_url': url,
            'image': '/icpc.PNG'
        })
        
        return events

    def scrape_national_ccdc(self):
        """Scrape National CCDC - Cyber defense competition"""
        events = []
        url = "https://www.nationalccdc.org"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        events.append({
            'category': 'Computer Science',
            'date': 'April 2026',
            'description': 'National Collegiate Cyber Defense Competition - Real-world cybersecurity challenges',
            'location': 'National Level',
            'source_url': url,
            'image': '/ccdc.PNG'
        })
        
        return events

    def scrape_mathleague(self):
        """Scrape Math League competitions"""
        events = []
        url = "https://mathleague.org/ondemand.php"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        events.append({
            'category': 'Math',
            'date': 'Year Round',
            'description': 'Math League On-Demand - Timed mathematics competitions for grades 3-12',
            'location': 'Online',
            'source_url': url,
            'image': '/mathleague.PNG'
        })
        
        return events

    def scrape_acsl(self):
        """Scrape ACSL American Computer Science League"""
        events = []
        url = "https://www.acsl.org"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        events.append({
            'category': 'Computer Science',
            'date': 'November 2025 - May 2026',
            'description': 'American Computer Science League - Multiple contests in programming and computer science',
            'location': 'Online/Local Schools',
            'source_url': url,
            'image': '/acsl.PNG'
        })
        
        return events

    def scrape_usaco(self):
        """Scrape USACO - USA Computing Olympiad"""
        events = []
        url = "https://usaco.org"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        events.append({
            'category': 'Computer Science',
            'date': 'December 2025 - March 2026',
            'description': 'USA Computing Olympiad - Multiple rounds of algorithmic programming contests',
            'location': 'Online',
            'source_url': url,
            'image': '/usaco.PNG'
        })
        
        return events

    def scrape_cyberpatriot(self):
        """Scrape CyberPatriot competition"""
        events = []
        url = "https://www.uscyberpatriot.org"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        events.append({
            'category': 'Computer Science',
            'date': 'October 2025 - March 2026',
            'description': 'CyberPatriot - National Youth Cyber Defense Competition by Air Force Association',
            'location': 'Online/Regional',
            'source_url': url,
            'image': '/uscyberpat.PNG'
        })
        
        return events

    def scrape_ics_competition(self):
        """Scrape ICS Competition"""
        events = []
        url = "https://icscompetition.org/en/"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        events.append({
            'category': 'Computer Science',
            'date': 'Annual',
            'description': 'International Cybersecurity Competition - Global cybersecurity challenges',
            'location': 'International/Online',
            'source_url': url,
            'image': '/icscomp.PNG'
        })
        
        return events

    def scrape_nsb(self):
        """Scrape National Science Bowl"""
        events = []
        url = "https://science.osti.gov/wdts/nsb"
        
        response = self.safe_request(url)
        if not response:
            return events
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        events.append({
            'category': 'Physics',
            'date': 'April 2026',
            'description': 'National Science Bowl - DOE science and math competition for high school students',
            'location': 'Washington, D.C.',
            'source_url': url,
            'image': '/sciencegov.PNG'
        })
        
        return events
    
    def scrape_intercompetition_art(self):
        """Scrape art competitions from InterCompetition"""
        events = []
        url = "https://intercompetition.com/art"
    
        response = self.safe_request(url)
        if not response:
            return events
    
        soup = BeautifulSoup(response.content, 'html.parser')
    
    # Look for competition listings
    # Based on the website structure, competitions appear to be in description blocks
        competition_blocks = soup.find_all(['div', 'article', 'section'])
    
        for block in competition_blocks:
        # Look for description text and deadline patterns
            text = block.get_text()
        
        # Extract deadline
            deadline_match = re.search(r'Deadline:\s*(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})', text)
            if deadline_match:
                deadline = deadline_match.group(1)
            else:
            # Try alternative date format
                deadline_match = re.search(r'Deadline:\s*(\d{1,2}\s+\w+\s+\d{4})', text)
                deadline = deadline_match.group(1) if deadline_match else 'Deadline TBD'
        
        # Extract competition title (usually first line or heading)
            title_elem = block.find(['h2', 'h3', 'h4', 'strong'])
            if title_elem:
                title = title_elem.text.strip()
            else:
            # Use first line as title
                lines = text.strip().split('\n')
                title = lines[0].strip() if lines else 'Art Competition'
        
        # Extract prize information
            prize_match = re.search(r'(?:Grand Prix|1st prize|winner will receive|Grand Prize winner will receive)[^.]*\.', text, re.IGNORECASE)
            prize_info = prize_match.group(0) if prize_match else ''
        
        # Extract brief description (first 150 characters after title)
            description_text = text.replace(title, '').strip()
        # Clean up the description
            description = description_text[:200].replace('\n', ' ').strip()
        
            events.append({
                'category': 'Art',
                'date': self.parse_date(deadline) if deadline else 'Date TBD',
                'description': title,
                'location': 'International / Online',
                'source_url': url,
                'image': None,
                'details': {
                    'deadline': deadline,
                    'prize': prize_info,
                    'full_description': description
               }
            })
    
    # Remove duplicates and limit to reasonable number
        unique_events = []
        seen_titles = set()
        for event in events[:10]:  # Limit to 10 most recent/relevant
            if event['description'] not in seen_titles:
                seen_titles.add(event['description'])
                unique_events.append(event)
    
        return unique_events
    

# fallback events --------------------------------------------------------
    def get_fallback_events(self):
        """Return curated fallback events if scraping fails"""
        return [
            {
                'category': 'Math',
                'date': 'March 3, 2026',
                'description': 'IU Indianapolis Math Contest - Open to all Indiana high school students',
                'location': 'IU Indianapolis School of Science',
                'source_url': 'https://science.indianapolis.iu.edu/math/about/math-contest/index.html',
                'image': '/IUphoto.PNG'
            },
            {
                'category': 'Math',
                'date': 'February 14, 2026',
                'description': 'Indiana MATHCOUNTS Competition',
                'location': 'Purdue University, Fort Wayne',
                'source_url': 'https://www.mathcounts.org',
                'image': '/mathCounts.PNG'
            },
            {
                'category': 'Math',
                'date': 'November 2025',
                'description': 'AMC 10/12 - American Mathematics Competitions',
                'location': 'Local Schools',
                'source_url': 'https://maa.org/student-programs/amc/',
                'image': '/MAA.PNG'
            },
            {
                'category': 'Computer Science',
                'date': 'December 2025 - March 2026',
                'description': 'USA Computing Olympiad (USACO)',
                'location': 'Online',
                'source_url': 'https://usaco.org',
                'image': '/usaco.PNG'
            },
            {
                'category': 'Computer Science',
                'date': 'October 2025 - March 2026',
                'description': 'CyberPatriot - National Youth Cyber Defense Competition',
                'location': 'Online/Regional',
                'source_url': 'https://www.uscyberpatriot.org',
                'image': '/uscyberpat.PNG'
            },
            {
                'category': 'Computer Science',
                'date': 'February 2026',
                'description': 'ICPC North America East Central Regional',
                'location': 'Regional Sites',
                'source_url': 'https://ec.na.icpc.global',
                'image': '/icpc.PNG'
            },
            {
                'category': 'Computer Science',
                'date': 'April 2026',
                'description': 'National Collegiate Cyber Defense Competition',
                'location': 'National Level',
                'source_url': 'https://www.nationalccdc.org',
                'image': '/ccdc.PNG'
            },
            {
                'category': 'Physics',
                'date': 'April 2026',
                'description': 'AAPT Physics Bowl - National physics competition',
                'location': 'Online/Regional Sites',
                'source_url': 'https://www.aapt.org/Programs/PhysicsBowl/',
                'image': '/AAPT.PNG'
            },
            {
                'category': 'Physics',
                'date': 'April 2026',
                'description': 'National Science Bowl - DOE science competition',
                'location': 'Washington, D.C.',
                'source_url': 'https://science.osti.gov/wdts/nsb',
                'image': '/sciencegov.PNG'
            },
            {
                'category': 'Literature',
                'date': 'January 2026',
                'description': 'Letters About Literature - Indiana State Library Writing Contest',
                'location': 'Indiana State Library',
                'source_url': 'https://www.in.gov/library/icb/lal/',
                'image': '/LAL.PNG'
            },
            {
                'category': 'Art',
                'date': 'Spring 2026',
                'description': 'Scholastic Art & Writing Awards - National competition for creative teens',
                'location': 'National Level',
                'source_url': 'https://www.artandwriting.org',
                'image': '/alliance.PNG'
            },
            {
                'category': 'Art',
                'date': 'Year Round',
                'description': 'Congressional Art Competition - Annual visual art competition for high school students',
                'location': 'Washington, D.C.',
                'source_url': 'https://www.house.gov/educators-and-students/congressional-art-competition',
                'image': '/house.PNG'
            }
        ]
# Main scraping function 
    def scrape_all(self):
        """Scrape all sources and combine events"""
        logger.info("Starting full scrape of all sources...")
        all_events = []
        
        # Math competitions
        logger.info("Scraping math competitions...")
        all_events.extend(self.scrape_iu_math_contest())
        all_events.extend(self.scrape_amc())
        all_events.extend(self.scrape_mathleague())
        all_events.extend(self.scrape_aops_competitions())
        
        # Physics competitions
        logger.info("Scraping physics competitions...")
        all_events.extend(self.scrape_physics_bowl())
        all_events.extend(self.scrape_iphyc())
        all_events.extend(self.scrape_lasp())
        all_events.extend(self.scrape_nsb())
        
        # Computer Science competitions
        logger.info("Scraping CS competitions...")
        all_events.extend(self.scrape_intercompetition())
        all_events.extend(self.scrape_icpc())
        all_events.extend(self.scrape_national_ccdc())
        all_events.extend(self.scrape_acsl())
        all_events.extend(self.scrape_usaco())
        all_events.extend(self.scrape_cyberpatriot())
        all_events.extend(self.scrape_ics_competition())
        
        # Literature competitions
        logger.info("Scraping literature competitions...")
        all_events.extend(self.scrape_indiana_library())

        # Art competitions
        logger.info("Scraping art competitions...")
        all_events.extend(self.scrape_intercompetition_art())
        
        # use fallback data in case no returned events
        if not all_events:
            logger.warning("No events scraped, using fallback data")
            return self.get_fallback_events()
        
        # Add Art category events not scraped
        all_events.extend([
            {
                'category': 'Art',
                'date': 'Spring 2026',
                'description': 'Scholastic Art & Writing Awards - National competition for creative teens',
                'location': 'National Level',
                'source_url': 'https://www.artandwriting.org',
                'image': '/alliance.PNG'
            },
            {
                'category': 'Art',
                'date': 'Year Round',
                'description': 'Congressional Art Competition - Annual visual art competition for high school students',
                'location': 'Washington, D.C.',
                'source_url': 'https://www.house.gov/educators-and-students/congressional-art-competition',
                'image': '/house.PNG'
            }
        ])
        

# Initialize scraper
scraper = AcademicEventScraper()

# Store events in memory with periodic updates
cached_events = scraper.get_fallback_events()
last_update_time = None

# Background automatic update ---------------------------------------
def update_events_background():
    """Background task to update events periodically"""
    global cached_events, last_update_time
    
    while True:
        try:
            logger.info("Background update: Scraping events...")
            new_events = scraper.scrape_all()
            if new_events:
                cached_events = new_events
                last_update_time = datetime.now()
                logger.info(f"Background update complete: {len(cached_events)} events")
        except Exception as e:
            logger.error(f"Background update failed: {e}")
        
        # Update every 6 hours
        time.sleep(21600)

# Start background update thread
update_thread = threading.Thread(target=update_events_background, daemon=True)
update_thread.start()

# Routes --------------------------------------------------------
@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events (cached)"""
    return jsonify(cached_events)

@app.route('/api/events/update', methods=['POST'])
def update_events():
    """Trigger a fresh scrape and update events"""
    global cached_events, last_update_time
    
    try:
        logger.info("Manual update triggered")
        new_events = scraper.scrape_all()
        
        if new_events:
            cached_events = new_events
            last_update_time = datetime.now()
            
            return jsonify({
                'success': True,
                'message': f'Successfully updated with {len(new_events)} events',
                'events': new_events
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No events found from scraping'
            }), 404
            
    except Exception as e:
        logger.error(f"Manual update failed: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/events/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'last_update': last_update_time.isoformat() if last_update_time else None,
        'events_count': len(cached_events)
    })

@app.route('/api/events/stats', methods=['GET'])
def get_stats():
    """Get statistics about cached events"""
    if not cached_events:
        return jsonify({'categories': {}, 'total': 0})
    
    categories = {}
    for event in cached_events:
        cat = event.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    return jsonify({
        'total': len(cached_events),
        'categories': categories,
        'last_update': last_update_time.isoformat() if last_update_time else None
    })

if __name__ == '__main__':
    # Initial scrape on startup
    logger.info("Performing initial scrape on startup...")
    try:
        cached_events = scraper.scrape_all() or scraper.get_fallback_events()
        last_update_time = datetime.now()
        logger.info(f"Initial scrape complete: {len(cached_events)} events")
    except Exception as e:
        logger.error(f"Initial scrape failed: {e}")
        cached_events = scraper.get_fallback_events()
    
    app.run(debug=True, port=5000)
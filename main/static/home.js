// Mobile menu toggle
document.getElementById('mobileMenuButton').addEventListener('click', function() {
    const menu = document.getElementById('mobileMenu');
    menu.classList.toggle('hidden');
});

// Language toggle functionality
document.getElementById('englishBtn').addEventListener('click', function() {
    this.classList.add('active');
    document.getElementById('hindiBtn').classList.remove('active');
    console.log('Switched to English');
});

document.getElementById('hindiBtn').addEventListener('click', function() {
    this.classList.add('active');
    document.getElementById('englishBtn').classList.remove('active');
    console.log('Switched to Hindi');
});

// Form submission for crop recommendations
document.getElementById('cropRecommendationForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get form values
    const soilType = document.getElementById('soilType').value;
    const region = document.getElementById('region').value;
    const season = document.getElementById('season').value;
    const waterAvailability = document.getElementById('waterAvailability').value;
    
    // Validate form
    if (!soilType || !region || !season || !waterAvailability) {
        alert('Please fill in all fields to get recommendations.');
        return;
    }
    
    // Show the results section with animation
    const resultsSection = document.getElementById('recommendationResults');
    resultsSection.classList.remove('hidden');
    resultsSection.style.opacity = '0';
    resultsSection.style.transform = 'translateY(20px)';
    
    // Animate the appearance
    setTimeout(() => {
        resultsSection.style.transition = 'all 0.5s ease';
        resultsSection.style.opacity = '1';
        resultsSection.style.transform = 'translateY(0)';
    }, 100);
    
    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }, 300);
    
    console.log('Crop recommendation requested:', { soilType, region, season, waterAvailability });
});

// Mock weather data fetch
document.getElementById('fetchWeatherBtn').addEventListener('click', function() {
    const location = document.getElementById('locationInput').value;
    if (location) {
        console.log('Fetching weather for:', location);
        // Update UI with mock data
        document.getElementById('currentLocation').textContent = location + ', India';
        document.getElementById('currentTemperature').textContent = Math.floor(Math.random() * 10 + 25) + '°C';
        document.getElementById('currentCondition').textContent = 'Updated Weather';
        
        // Show a simple notification
        const btn = document.getElementById('fetchWeatherBtn');
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>';
        
        setTimeout(() => {
            btn.innerHTML = originalHTML;
        }, 1000);
    } else {
        alert('Please enter a location first.');
    }
});

// Current location button
document.getElementById('useCurrentLocation').addEventListener('click', function() {
    const btn = this;
    const originalText = btn.innerHTML;
    
    btn.innerHTML = '<svg class="w-4 h-4 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>Getting Location...';
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            console.log('Latitude:', position.coords.latitude, 'Longitude:', position.coords.longitude);
            // Update UI with mock data based on coordinates
            document.getElementById('locationInput').value = 'Your Village';
            document.getElementById('currentLocation').textContent = 'Your Village, India';
            
            btn.innerHTML = originalText;
        }, function(error) {
            console.error('Geolocation error:', error);
            alert('Unable to get your location. Please enter it manually.');
            btn.innerHTML = originalText;
        });
    } else {
        alert('Geolocation is not supported by your browser');
        btn.innerHTML = originalText;
    }
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add some interactive feedback to cards
document.querySelectorAll('.card-hover').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-5px)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
});

// Simulate real-time data updates
function updateDashboardData() {
    // Update temperature
    const temps = ['26°C', '27°C', '28°C', '29°C', '30°C'];
    document.getElementById('currentTemp').textContent = temps[Math.floor(Math.random() * temps.length)];
    
    // Update humidity
    const humidity = Math.floor(Math.random() * 20 + 60) + '%';
    document.getElementById('currentHumidity').textContent = humidity;
}

// Update data every 30 seconds
setInterval(updateDashboardData, 30000);

console.log('Smart Crop Advisory System loaded successfully!');
// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const searchForm = document.getElementById('search-form');
    if (!searchForm) console.error('search-form not found');
    
    const flightsList = document.getElementById('flights-list');
    if (!flightsList) console.error('flights-list not found');
    
    const hotelsList = document.getElementById('hotels-list');
    if (!hotelsList) console.error('hotels-list not found');
    
    const loading = document.getElementById('loading');
    if (!loading) console.error('loading element not found');
    
    const noFlights = document.getElementById('no-flights');
    if (!noFlights) console.error('no-flights element not found');
    
    const noHotels = document.getElementById('no-hotels');
    if (!noHotels) console.error('no-hotels element not found');
    
    const startPointSelect = document.getElementById('startPoint');
    if (!startPointSelect) console.error('startPoint not found');
    
    const destinationSelect = document.getElementById('destination');
    if (!destinationSelect) console.error('destination not found');
    
    const budgetTooltip = document.getElementById('budget-tooltip');
    if (!budgetTooltip) console.error('budget-tooltip not found');
    
    console.log('DOM elements initialized');
    
    // Create a div to display minimum prices
    const minPricesDiv = document.createElement('div');
    minPricesDiv.className = 'min-price-display';
    minPricesDiv.style.display = 'none';
    
    // Get the budget and date elements to position the min prices div between them
    const budgetGroup = document.querySelector('.form-group:nth-child(3)');
    const dateGroup = document.querySelector('.form-group.date-range:first-of-type');
    
    // Insert the min prices div after the budget field and before the date fields
    if (budgetGroup && dateGroup) {
        searchForm.insertBefore(minPricesDiv, dateGroup);
    }
    
    // Function to load city options into dropdowns
    async function loadCityOptions() {
        try {
            // Get list of all available cities
            const response = await fetch('/search_cities', {
                method: 'POST',
                body: new FormData()
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch cities');
            }
            
            const data = await response.json();
            console.log('Received cities data:', data);
            
            if (!startPointSelect || !destinationSelect) {
                console.error('Could not find select elements');
                return;
            }
            
            // Function to populate a select element
            function populateSelect(select, cities) {
                // Keep the first option (placeholder)
                const firstOption = select.options[0];
                select.innerHTML = '';
                select.appendChild(firstOption);
                
                // Add city options
                cities.forEach(city => {
                    const option = document.createElement('option');
                    const cityText = `${city.name}, ${city.country}`;
                    option.value = cityText;  // Store just city and country as value
                    option.textContent = cityText;  // Display city and country
                    option.setAttribute('data-city-code', city.city_code);  // Store city code for API calls
                    select.appendChild(option);
                });
            }
            
            // Get the list of cities from available cities
            const cities = data.suggestions || data.available_cities || [];
            console.log('Cities to populate:', cities);
            
            if (cities.length === 0) {
                console.error('No cities available');
                return;
            }
            
            // Populate both dropdowns
            populateSelect(startPointSelect, cities);
            populateSelect(destinationSelect, cities);
            
        } catch (error) {
            console.error('Error loading cities:', error);
            // Add error message to dropdowns
            [startPointSelect, destinationSelect].forEach(select => {
                select.innerHTML = '<option value="">Error loading cities</option>';
            });
        }
    }
    
    // Function to fetch and display minimum prices
    async function updateMinPrices() {
        const startPoint = startPointSelect.value;
        const destination = destinationSelect.value;
        
        // Show appropriate message based on selection state
        if (!startPoint && !destination) {
            budgetTooltip.textContent = 'Select origin and destination to see minimum hotel cost';
            return;
        } else if (!startPoint) {
            budgetTooltip.textContent = 'Select origin to see minimum hotel cost';
            return;
        } else if (!destination) {
            budgetTooltip.textContent = 'Select destination to see minimum hotel cost';
            return;
        }
        
        // At this point both origin and destination are selected
        budgetTooltip.textContent = 'Fetching minimum hotel cost...';
        
        // Clear any previous minPricesDiv content
        minPricesDiv.innerHTML = '';
        minPricesDiv.style.display = 'none';
        
        // Create form data
        const formData = new FormData();
        formData.append('startPoint', startPoint);
        formData.append('destination', destination);
        
        try {
            // Fetch minimum prices
            const response = await fetch('/get_min_prices', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error('Failed to fetch minimum prices');
            const data = await response.json();
            
            if (data.error) {
                minPricesDiv.style.display = 'none';
                budgetTooltip.textContent = 'Could not retrieve minimum hotel cost';
                return;
            }
            
            // Update tooltip with minimum hotel cost
            if (data && data.min_hotel_price) {
                budgetTooltip.textContent = `Minimum Hotel Cost per night: ${data.min_hotel_price}`;
            } else {
                budgetTooltip.textContent = 'No hotel price data available for this destination';
            }
            
            // Don't display the minPricesDiv anymore
            minPricesDiv.style.display = 'none';
        } catch (error) {
            console.error('Error fetching minimum prices:', error);
            minPricesDiv.style.display = 'none';
            budgetTooltip.textContent = 'Unable to fetch hotel prices. Please try again';
        }
    }
    
    // Add event listeners to update min prices when selections change
    startPointSelect.addEventListener('change', () => {
        setTimeout(updateMinPrices, 100); // Small delay to ensure value is updated
    });
    
    destinationSelect.addEventListener('change', () => {
        setTimeout(updateMinPrices, 100); // Small delay to ensure value is updated
    });
    
    // Handle form submission
    searchForm.addEventListener('submit', async function(e) {
        e.preventDefault(); // This should prevent the page from reloading
        
        // Show loading state
        loading.style.display = 'block';
        flightsList.innerHTML = '';
        hotelsList.innerHTML = '';
        noFlights.style.display = 'none';
        noHotels.style.display = 'none';
        
        // Get form data
        const formData = new FormData(searchForm);

        // Get the selected city codes from the dropdowns
        const startPointOption = startPointSelect.options[startPointSelect.selectedIndex];
        const destinationOption = destinationSelect.options[destinationSelect.selectedIndex];

        const startPointCode = startPointOption.getAttribute('data-city-code');
        const destinationCode = destinationOption.getAttribute('data-city-code');

        // Append city codes to the form data for the backend
        if (startPointCode) formData.set('startPointCode', startPointCode);
        if (destinationCode) formData.set('destinationCode', destinationCode);
        
        // Validate dates
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        
        if (!startDate || !endDate) {
            alert('Please select both start and end dates');
            loading.style.display = 'none';
            return;
        }
        
        if (new Date(endDate) <= new Date(startDate)) {
            alert('End date must be after start date');
            loading.style.display = 'none';
            return;
        }
        
        try {
            // Fetch flights
            const flightsResponse = await fetch('/search_flights', {
                method: 'POST',
                body: formData
            });
            
            const flightData = await flightsResponse.json();
            console.log('Flight search response:', flightData);
            
            if (!flightsResponse.ok || flightData.error) {
                console.error('Flight search error:', flightData.error);
                throw new Error(flightData.error || 'Flight search failed');
            }
            
            const flights = Array.isArray(flightData) ? flightData : [];
            console.log('Processed flight data:', flights);
            
            if (flights.length === 0) {
                noFlights.style.display = 'block';
            } else {
                noFlights.style.display = 'none';
                flights.forEach(flight => {
                    const flightElement = document.createElement('div');
                    flightElement.className = 'flight-item';

                    // Format times properly
                    const formatTime = (isoString) => {
                        if (!isoString) return 'N/A';
                        return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
                    };

                    const departureTime = formatTime(flight.departureTime);
                    const arrivalTime = formatTime(flight.arrivalTime);
                    const flightNumber = flight.flightNumber || 'N/A';

                    // Format price properly
                    const formatPrice = (price) => {
                        if (price === undefined || price === null) return 'N/A';
                        return `₹${parseFloat(price).toLocaleString('en-IN')}`;
                    };

                    flightElement.innerHTML = `
                        <div class="flight-header">
                            <h3>${flight.airline || 'Unknown Airline'}</h3>
                            <span class="flight-number">${flightNumber}</span>
                        </div>
                        <div class="flight-route">
                            <div class="departure">
                                <span class="time">${departureTime}</span>
                                <span class="airport">${flight.departureAirport || 'N/A'}</span>
                            </div>
                            <div class="flight-arrow">→</div>
                            <div class="arrival">
                                <span class="time">${arrivalTime}</span>
                                <span class="airport">${flight.arrivalAirport || 'N/A'}</span>
                            </div>
                        </div>
                        <div class="flight-details">
                            <div class="price">${formatPrice(flight.price)}</div>
                        </div>
                    `;
                    flightsList.appendChild(flightElement);
                });
            }
            
            // Fetch hotels
            const hotelsResponse = await fetch('/search_hotels', {
                method: 'POST',
                body: formData
            });
            
            const hotelData = await hotelsResponse.json();
            console.log('Hotel search response:', hotelData);
            
            if (!hotelsResponse.ok || hotelData.error) {
                console.error('Hotel search error:', hotelData.error);
                throw new Error(hotelData.error || 'Hotel search failed');
            }
            
            const hotels = Array.isArray(hotelData) ? hotelData : [];
            console.log('Processed hotel data:', hotels);
            
            if (hotels.length === 0) {
                noHotels.style.display = 'block';
            } else {
                noHotels.style.display = 'none';
                hotels.forEach(hotel => {
                    const hotelElement = document.createElement('div');
                    hotelElement.className = 'hotel-item';

                    // Format price properly
                    const formatPrice = (price) => {
                        if (price === undefined || price === null) return 'N/A';
                        return `₹${parseFloat(price).toLocaleString('en-IN')}`;
                    };

                    hotelElement.innerHTML = `
                        <div class="hotel-header">
                            <h3 class="hotel-name">${hotel.name || 'Hotel Name Not Available'}</h3>
                            <div class="hotel-rating">
                                ${'★'.repeat(Math.round(hotel.rating || 0))}${'☆'.repeat(5 - Math.round(hotel.rating || 0))}
                            </div>
                        </div>
                        <div class="hotel-details">
                            <div class="hotel-location">
                                <span class="icon">📍</span>
                                <span>${hotel.location || 'Location Not Available'}</span>
                            </div>
                            <div class="hotel-description">
                                <p>${hotel.description || 'No description available'}</p>
                            </div>
                            <div class="hotel-amenities">
                                ${hotel.amenities ? hotel.amenities.map(amenity => `<span class="amenity-tag">${amenity}</span>`).join('') : ''}
                            </div>
                            <div class="hotel-price">
                                <span class="label">Price per night:</span>
                                <span class="amount">${formatPrice(hotel.price)}</span>
                            </div>
                        </div>
                    `;
                    hotelsList.appendChild(hotelElement);
                });
            }
            
        } catch (error) {
            console.error('Error:', error);
            flightsList.innerHTML = '<p class="error">Error fetching results. Please try again.</p>';
            hotelsList.innerHTML = '<p class="error">Error fetching results. Please try again.</p>';
        } finally {
            loading.style.display = 'none';
            
            // Enable chatbot functionality after search
            const userMessageInput = document.getElementById('userMessage');
            const chatForm = document.getElementById('chat-form');
            const chatButton = chatForm.querySelector('button');
            
            // Enable the chat input and button
            userMessageInput.disabled = false;
            chatButton.disabled = false;
            
            // Set up chat form submission
            chatForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                const message = userMessageInput.value.trim();
                if (!message) return;
                
                // Add user message to chat
                const chatMessages = document.getElementById('chat-messages');
                const userMessageElement = document.createElement('div');
                userMessageElement.className = 'message user';
                userMessageElement.innerHTML = `<p>${message}</p>`;
                chatMessages.appendChild(userMessageElement);
                
                // Clear input
                userMessageInput.value = '';
                
                // Get destination from search form
                const destination = document.getElementById('destination').value;
                const startPoint = document.getElementById('startPoint').value;  // Add this line
                const startDate = document.getElementById('startDate').value;
                const endDate = document.getElementById('endDate').value;
                
                // Create form data for chatbot request
                const chatData = new FormData();
                chatData.append('message', message);
                chatData.append('destination', destination);
                chatData.append('startPoint', startPoint);  // Add this line
                chatData.append('startDate', startDate);
                chatData.append('endDate', endDate);
                
                try {
                    // Show loading in chat
                    const loadingElement = document.createElement('div');
                    loadingElement.className = 'message bot loading';
                    loadingElement.innerHTML = '<p>Thinking...</p>';
                    chatMessages.appendChild(loadingElement);
                    
                    // Fetch response from chatbot
                    const response = await fetch('/chatbot', {
                        method: 'POST',
                        body: chatData
                    });
                    
                    if (!response.ok) throw new Error('Chatbot request failed');
                    const data = await response.json();
                    
                    // Remove loading message
                    chatMessages.removeChild(loadingElement);
                    
                    // Add bot response
                    const botMessageElement = document.createElement('div');
                    botMessageElement.className = 'message bot';
                    botMessageElement.innerHTML = `<p>${data.response}</p>`;
                    chatMessages.appendChild(botMessageElement);
                    
                    // Scroll to bottom of chat
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                } catch (error) {
                    console.error('Chatbot error:', error);
                    const errorElement = document.createElement('div');
                    errorElement.className = 'message bot error';
                    errorElement.innerHTML = '<p>Sorry, I encountered an error. Please try again.</p>';
                    chatMessages.appendChild(errorElement);
                }
            });
        }
    });
    
    // Set minimum date for date inputs to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('startDate').min = today;
    document.getElementById('endDate').min = today;
    
    // Initialize by loading cities and updating min prices
    console.log('Loading city options...');
    loadCityOptions();
    updateMinPrices();
});

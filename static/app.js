document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const flightsList = document.getElementById('flights-list');
    const hotelsList = document.getElementById('hotels-list');
    const loading = document.getElementById('loading');
    const noFlights = document.getElementById('no-flights');
    const noHotels = document.getElementById('no-hotels');
    
    // Add these new elements for min prices
    const startPointSelect = document.getElementById('startPoint');
    const destinationSelect = document.getElementById('destination');
    const budgetTooltip = document.getElementById('budget-tooltip');
    
    // Create a div to display minimum prices
    const minPricesDiv = document.createElement('div');
    minPricesDiv.className = 'min-price-display';
    minPricesDiv.style.display = 'none';
    
    // Get the budget and date elements to position the min prices div between them
    const budgetGroup = document.querySelector('.form-group:nth-child(3)');
    const dateGroup = document.querySelector('.form-group.date-range:first-of-type');
    
    // Insert the min prices div after the budget field and before the date fields
    searchForm.insertBefore(minPricesDiv, dateGroup);
    
    // Function to fetch and display minimum prices
    async function updateMinPrices() {
        const startPoint = startPointSelect.value;
        const destination = destinationSelect.value;
        
        // Only proceed if both values are selected
        if (!startPoint || !destination) {
            minPricesDiv.style.display = 'none';
            budgetTooltip.textContent = 'Select origin and destination to see minimum hotel cost';
            return;
        }
        
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
            budgetTooltip.textContent = `Minimum Hotel Cost: $${data.minHotelPrice}/night`;
            
            // Don't display the minPricesDiv anymore
            minPricesDiv.style.display = 'none';
        } catch (error) {
            console.error('Error fetching minimum prices:', error);
            minPricesDiv.style.display = 'none';
            budgetTooltip.textContent = 'Error retrieving minimum hotel cost';
        }
    }
    
    // Add event listeners to update min prices when selections change
    startPointSelect.addEventListener('change', updateMinPrices);
    destinationSelect.addEventListener('change', updateMinPrices);
    
    // Call updateMinPrices initially to set up the tooltip
    updateMinPrices();
    
    // Make sure this event listener is at the top level of your DOMContentLoaded function
    searchForm.addEventListener('submit', async function(e) {
        e.preventDefault(); // This should prevent the page from reloading
        
        // Show loading state
        loading.style.display = 'block';
        flightsList.innerHTML = '';
        hotelsList.innerHTML = '';
        
        const formData = new FormData(searchForm);
        
        try {
            // Fetch flights
            const flightsResponse = await fetch('/search_flights', {
                method: 'POST',
                body: formData
            });
            
            if (!flightsResponse.ok) throw new Error('Flight search failed');
            const flights = await flightsResponse.json();
            
            if (flights.length === 0) {
                noFlights.style.display = 'block';
            } else {
                noFlights.style.display = 'none';
                flights.forEach(flight => {
                    const flightElement = document.createElement('div');
                    flightElement.className = 'flight-item';
                    flightElement.innerHTML = `
                        <h3>${flight.airline}</h3>
                        <p>From: ${flight.origin}</p>
                        <p>To: ${flight.destination}</p>
                        <p>Price: $${flight.price}</p>
                        <p>Date: ${flight.date}</p>
                    `;
                    flightsList.appendChild(flightElement);
                });
            }
            
            // Fetch hotels
            const hotelsResponse = await fetch('/search_hotels', {
                method: 'POST',
                body: formData
            });
            
            if (!hotelsResponse.ok) throw new Error('Hotel search failed');
            const hotels = await hotelsResponse.json();
            
            if (hotels.length === 0) {
                noHotels.style.display = 'block';
            } else {
                noHotels.style.display = 'none';
                hotels.forEach(hotel => {
                    const hotelElement = document.createElement('div');
                    hotelElement.className = 'hotel-item';
                    hotelElement.innerHTML = `
                        <h3>${hotel.name}</h3>
                        <p>Location: ${hotel.location}</p>
                        <p>Price per night: $${hotel.price_per_night}</p>
                        <p>Rating: ${hotel.rating}/5</p>
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
                const startDate = document.getElementById('startDate').value;
                const endDate = document.getElementById('endDate').value;
                
                // Create form data for chatbot request
                const chatData = new FormData();
                chatData.append('message', message);
                chatData.append('destination', destination);
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
});
// Currency formatter
const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(value);
};

document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    // Get form data
    const formData = {
        location: document.getElementById('location').value,
        area: document.getElementById('area').value,
        bhk: document.getElementById('bhk').value,
        bathrooms: document.getElementById('bathrooms').value,
        amenities: document.getElementById('amenities').value,
        marketTrend: document.getElementById('marketTrend').value,
        investmentPeriod: document.getElementById('investmentPeriod').value,
        expectedGrowth: document.getElementById('expectedGrowth').value
    };

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        // Update KPIs
        document.getElementById('kpi-price').innerText = formatCurrency(data.predicted_price);
        document.getElementById('kpi-future').innerText = formatCurrency(data.future_value);
        document.getElementById('kpi-roi').innerText = `${data.roi_percentage}%`;
        
        const profitElem = document.getElementById('kpi-profit');
        profitElem.innerText = formatCurrency(data.profit);
        profitElem.style.color = data.profit >= 0 ? 'var(--success)' : 'var(--danger)';

        document.getElementById('kpi-segment').innerText = data.market_segment;
        document.getElementById('kpi-risk').innerText = data.risk_category;

        // Update Recommendation Banner
        const recBanner = document.getElementById('recommendationBanner');
        const recIcon = document.getElementById('recIcon');
        const recText = document.getElementById('recText');

        recBanner.className = 'recommendation-banner glass-card'; // reset
        recText.innerText = data.recommendation;

        if (data.recommendation.includes('Invest') || data.recommendation.includes('Strong Buy')) {
            recBanner.classList.add('invest');
            recIcon.innerText = '✅';
        } else if (data.recommendation === 'Moderate Risk') {
            recBanner.classList.add('moderate');
            recIcon.innerText = '⚠️';
        } else {
            recBanner.classList.add('avoid');
            recIcon.innerText = '❌';
        }

        // Update Property Category Badge dynamically
        const aiCategory = document.getElementById('aiPropertyCategory');
        if (data.property_category) {
            aiCategory.innerText = `🏷️ ${data.property_category}`;
            aiCategory.classList.remove('badge-business', 'badge-domestic', 'badge-deal', 'hidden');
            let badgeClass = 'badge-domestic';
            if (data.property_category.includes('Business')) badgeClass = 'badge-business';
            if (data.property_category.includes('Quick Sale')) badgeClass = 'badge-deal';
            
            aiCategory.classList.add(badgeClass);
        } else {
            aiCategory.classList.add('hidden');
        }

        // Show Results
        document.getElementById('resultsWrapper').classList.remove('hidden');

        // Scroll to results
        setTimeout(() => {
            document.getElementById('resultsWrapper').scrollIntoView({ behavior: 'smooth' });
        }, 100);

        // Render Charts via function in charts.js
        if(typeof renderCharts === 'function') {
            renderCharts(data, formData);
        }

    } catch (error) {
        console.error('Error fetching prediction:', error);
        alert('Failed to get prediction from AI models.');
    }
});

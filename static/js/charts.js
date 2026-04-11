// Global variables to hold chart instances so we can destroy them on re-render
let priceChart, roiChart, segmentChart, featureChart;

const renderCharts = (apiData, formData) => {
    // 1. Price Trend Forecast (Line Chart)
    const ctxPrice = document.getElementById('priceTrendChart').getContext('2d');
    if(priceChart) priceChart.destroy();
    
    // Generate projected trend data
    const years = parseInt(formData.investmentPeriod);
    const labels = Array.from({length: years + 1}, (_, i) => `Year ${i}`);
    
    let currentPrice = apiData.predicted_price;
    const growth = parseFloat(formData.expectedGrowth) / 100;
    const priceDataArray = [currentPrice];
    
    for(let i=1; i<=years; i++) {
        currentPrice *= (1 + growth);
        priceDataArray.push(currentPrice);
    }

    priceChart = new Chart(ctxPrice, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Projected Value (INR)',
                data: priceDataArray,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } }
        }
    });

    // 2. ROI Growth Model (Bar Chart)
    const ctxROI = document.getElementById('roiGrowthChart').getContext('2d');
    if(roiChart) roiChart.destroy();

    roiChart = new Chart(ctxROI, {
        type: 'bar',
        data: {
            labels: ['Low Est.', 'AI Prediction', 'High Est.'],
            datasets: [{
                label: 'ROI %',
                data: [
                    apiData.roi_percentage * 0.8,
                    apiData.roi_percentage,
                    apiData.roi_percentage * 1.2
                ],
                backgroundColor: ['#93c5fd', '#3b82f6', '#1e40af'],
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } }
        }
    });

    // 3. Market Segmentation (Pie or Doughnut Chart)
    const ctxSegment = document.getElementById('segmentationChart').getContext('2d');
    if(segmentChart) segmentChart.destroy();

    segmentChart = new Chart(ctxSegment, {
        type: 'doughnut',
        data: {
            labels: ['Budget', 'Mid-Range', 'Premium'],
            datasets: [{
                data: [30, 50, 20], // Static representation of the local market
                backgroundColor: ['#10b981', '#3b82f6', '#8b5cf6'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { position: 'bottom' } 
            }
        }
    });

    // 4. Feature Importance (Bar Chart - Horizontal)
    const ctxFeature = document.getElementById('featureImportanceChart').getContext('2d');
    if(featureChart) featureChart.destroy();

    featureChart = new Chart(ctxFeature, {
        type: 'bar',
        data: {
            labels: ['Location', 'Area', 'BHK', 'Amenities', 'Market Trend'],
            datasets: [{
                label: 'Importance Score',
                data: [0.85, 0.70, 0.65, 0.40, 0.60],
                backgroundColor: '#0ea5e9',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            plugins: { legend: { display: false } }
        }
    });
};

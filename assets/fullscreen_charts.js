// Fullscreen Charts JavaScript Handler
// This script handles copying charts to the fullscreen modal

console.log('✅ Fullscreen charts script loaded');

// Store the current chart ID globally
window.currentFullscreenChartId = null;

// Listen for store changes using Dash's built-in event system
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM loaded, setting up observers');
    
    // Watch for modal to open
    const modalObserver = new MutationObserver(function(mutations) {
        const modal = document.getElementById('fullscreen-chart-modal');
        if (modal && modal.classList.contains('show')) {
            console.log('🔵 Modal opened, chart ID:', window.currentFullscreenChartId);
            if (window.currentFullscreenChartId) {
                setTimeout(function() {
                    copyChartToModal(window.currentFullscreenChartId);
                }, 300);
            }
        }
    });
    
    const modal = document.getElementById('fullscreen-chart-modal');
    if (modal) {
        modalObserver.observe(modal, { attributes: true, attributeFilter: ['class'] });
        console.log('✅ Modal observer set up');
    } else {
        console.warn('⚠️ Modal element not found on page load');
    }
    
    // Watch for store updates
    const storeObserver = new MutationObserver(function(mutations) {
        const store = document.getElementById('fullscreen-chart-store');
        if (store) {
            // Try to get the value from the store
            const storeData = store.textContent || store.innerText;
            if (storeData && storeData.trim()) {
                try {
                    const data = JSON.parse(storeData);
                    if (data) {
                        window.currentFullscreenChartId = data;
                        console.log('📦 Store updated with chart ID:', data);
                    }
                } catch (e) {
                    window.currentFullscreenChartId = storeData.trim();
                    console.log('📦 Store updated with chart ID (text):', storeData.trim());
                }
            }
        }
    });
    
    setTimeout(function() {
        const store = document.getElementById('fullscreen-chart-store');
        if (store) {
            storeObserver.observe(store, { 
                childList: true, 
                characterData: true, 
                subtree: true 
            });
            console.log('✅ Store observer set up');
        } else {
            console.warn('⚠️ Store element not found');
        }
    }, 100);
});

function copyChartToModal(chartId) {
    try {
        console.log('═══════════════════════════════════════');
        console.log('🚀 Starting copyChartToModal');
        console.log('📊 Chart ID:', chartId);
        console.log('═══════════════════════════════════════');
        
        if (!chartId) {
            console.error('❌ No chart ID provided');
            return;
        }
        
        // Find the container
        const container = document.getElementById('fullscreen-chart-container');
        if (!container) {
            console.error('❌ Container #fullscreen-chart-container not found');
            return;
        }
        
        console.log('✅ Found container:', container);
        console.log('   Container dimensions:', container.offsetWidth, 'x', container.offsetHeight);
        
        // Find the original chart - try multiple strategies
        let originalPlotlyDiv = null;
        
        // Strategy 1: Look for the chart by its ID directly
        const chartElement = document.getElementById(chartId);
        if (chartElement) {
            console.log('✅ Found chart element directly:', chartId);
            // Check if it's a Plotly div
            if (chartElement.classList.contains('js-plotly-plot')) {
                originalPlotlyDiv = chartElement;
            } else {
                // Look for Plotly div inside
                originalPlotlyDiv = chartElement.querySelector('.js-plotly-plot');
            }
        }
        
        // Strategy 2: Look for wrapper and find chart inside
        if (!originalPlotlyDiv) {
            const wrapper = document.getElementById(chartId + '-wrapper');
            if (wrapper) {
                console.log('✅ Found chart wrapper:', chartId + '-wrapper');
                originalPlotlyDiv = wrapper.querySelector('.js-plotly-plot');
            }
        }
        
        // Strategy 3: Look for any element with data-chart-id attribute
        if (!originalPlotlyDiv) {
            const wrapperByData = document.querySelector(`[data-chart-id="${chartId}"]`);
            if (wrapperByData) {
                console.log('✅ Found chart by data attribute');
                originalPlotlyDiv = wrapperByData.querySelector('.js-plotly-plot');
            }
        }
        
        if (!originalPlotlyDiv) {
            console.error('❌ Could not find Plotly chart for:', chartId);
            console.log('   Available chart IDs on page:');
            document.querySelectorAll('[id*="chart"]').forEach(el => {
                console.log('   -', el.id);
            });
            console.log('   Available Plotly divs:');
            document.querySelectorAll('.js-plotly-plot').forEach(el => {
                console.log('   -', el.id || 'no-id', 'parent:', el.parentElement?.id);
            });
            container.innerHTML = '<div style="padding: 50px; text-align: center; color: #ef4444; font-size: 18px;">❌ Chart not found: ' + chartId + '</div>';
            return;
        }
        
        console.log('✅ Found original Plotly div');
        
        // Check if Plotly is loaded
        if (typeof Plotly === 'undefined') {
            console.error('❌ Plotly is not loaded');
            container.innerHTML = '<div style="padding: 50px; text-align: center; color: #ef4444; font-size: 18px;">📉 Plotly library not loaded</div>';
            return;
        }
        
        console.log('✅ Plotly is available, version:', Plotly.version);
        
        // Get the figure data from the original chart
        if (!originalPlotlyDiv.data || !originalPlotlyDiv.layout) {
            console.error('❌ Chart data or layout not found');
            console.log('   Has data:', !!originalPlotlyDiv.data);
            console.log('   Has layout:', !!originalPlotlyDiv.layout);
            container.innerHTML = '<div style="padding: 50px; text-align: center; color: #ef4444; font-size: 18px;">❌ Chart data not available</div>';
            return;
        }
        
        console.log('✅ Chart has data and layout');
        console.log('   Data traces:', originalPlotlyDiv.data.length);
        console.log('   Layout keys:', Object.keys(originalPlotlyDiv.layout));
        
        // Clear container and create new div for the chart
        container.innerHTML = '';
        container.style.display = 'block';
        container.style.width = '100%';
        container.style.minHeight = '70vh';
        container.style.background = 'white';
        
        const newPlotlyDiv = document.createElement('div');
        newPlotlyDiv.id = 'fullscreen-plotly-chart';
        newPlotlyDiv.style.width = '100%';
        newPlotlyDiv.style.height = '70vh';
        newPlotlyDiv.style.minHeight = '70vh';
        newPlotlyDiv.style.display = 'block';
        container.appendChild(newPlotlyDiv);
        
        console.log('✅ Created new Plotly div');
        console.log('   New div dimensions:', newPlotlyDiv.offsetWidth, 'x', newPlotlyDiv.offsetHeight);
        
        // Deep clone the data and layout
        const chartData = JSON.parse(JSON.stringify(originalPlotlyDiv.data));
        const chartLayout = JSON.parse(JSON.stringify(originalPlotlyDiv.layout));
        
        // Adjust layout for fullscreen
        chartLayout.height = null;
        chartLayout.autosize = true;
        chartLayout.width = null;
        
        console.log('🎨 Creating plot...');
        
        // Create the plot
        Plotly.newPlot(
            newPlotlyDiv,
            chartData,
            chartLayout,
            {
                responsive: true,
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['sendDataToCloud']
            }
        ).then(function() {
            console.log('✅✅✅ Chart successfully created in modal! ✅✅✅');
            console.log('   Final dimensions:', newPlotlyDiv.offsetWidth, 'x', newPlotlyDiv.offsetHeight);
            
            // Trigger a resize to ensure proper sizing
            setTimeout(function() {
                if (window.Plotly && newPlotlyDiv) {
                    Plotly.Plots.resize(newPlotlyDiv);
                    console.log('✅ Chart resized');
                }
            }, 100);
        }).catch(function(err) {
            console.error('❌ Error creating Plotly chart:', err);
            console.error('   Stack trace:', err.stack);
            container.innerHTML = '<div style="padding: 50px; text-align: center; color: #ef4444; font-size: 18px;">❌ Error loading chart: ' + err.message + '</div>';
        });
        
    } catch (error) {
        console.error('❌ Error in copyChartToModal:', error);
        console.error('   Stack trace:', error.stack);
        const container = document.getElementById('fullscreen-chart-container');
        if (container) {
            container.innerHTML = '<div style="padding: 50px; text-align: center; color: #ef4444; font-size: 18px;">❌ Error: ' + error.message + '</div>';
        }
    }
}

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
        
        // Debug: Check if customdata exists for state-pie-chart
        if (chartId === 'state-pie-chart' && chartData && chartData.length > 0) {
            console.log('🔍 State chart data check:');
            console.log('   customdata exists:', !!chartData[0].customdata);
            if (chartData[0].customdata) {
                console.log('   customdata sample:', chartData[0].customdata.slice(0, 3));
            }
        }
        
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
            
            // Setup drill-down click handlers based on chart type
            if (chartId === 'dealer-pie-chart') {
                console.log('🎯 Setting up dealer drill-down click handler');
                setupDealerDrillDown(newPlotlyDiv);
                // Enhance single-slice visual feedback
                enhanceSingleSliceInteraction(newPlotlyDiv, chartId);
            } else if (chartId === 'state-pie-chart') {
                console.log('🎯 Setting up state drill-down click handler');
                setupStateDrillDown(newPlotlyDiv);
                // Enhance single-slice visual feedback
                enhanceSingleSliceInteraction(newPlotlyDiv, chartId);
            }
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

// Check if we're currently in a drill-down view (to prevent click handler on initial load)
function isInDrillDownView(type) {
    if (type === 'dealer') {
        const metricButtons = document.getElementById('dealer-metric-revenue-btn');
        return metricButtons && metricButtons.style.display !== 'none';
    } else if (type === 'state') {
        const metricButtons = document.getElementById('state-metric-revenue-btn');
        return metricButtons && metricButtons.style.display !== 'none';
    }
    return false;
}

// Setup dealer drill-down click handler
function setupDealerDrillDown(plotlyDiv) {
    if (!plotlyDiv) {
        console.error('❌ No plotly div provided for drill-down');
        return;
    }
    
    console.log('🔧 Configuring dealer pie chart for drill-down...');
    
    // Check if we're in a drill-down view already (back button visible)
    if (isInDrillDownView('dealer')) {
        console.log('ℹ️ Already in drill-down view, skipping click handler setup');
        return;
    }
    
    // Remove any existing click handlers
    if (plotlyDiv.removeAllListeners) {
        plotlyDiv.removeAllListeners('plotly_click');
    }
    
    // Add click event listener
    plotlyDiv.on('plotly_click', function(data) {
        console.log('═══════════════════════════════════════');
        console.log('🖱️ DEALER PIE CHART CLICKED!');
        console.log('📊 Click data:', data);
        console.log('═══════════════════════════════════════');
        
        // Prevent default action and stop propagation
        if (data && data.event) {
            data.event.preventDefault();
            data.event.stopPropagation();
        }
        
        if (!data.points || data.points.length === 0) {
            console.warn('⚠️ No points data in click event');
            return false;
        }
        
        const point = data.points[0];
        console.log('📍 Clicked point:', point);
        
        // Get dealer name from customdata (full name) or label (display name)
        const dealerName = point.customdata && point.customdata[0] 
            ? point.customdata[0] 
            : point.label;
        
        console.log('🏪 Selected dealer:', dealerName);
        
        if (!dealerName) {
            console.error('❌ Could not extract dealer name from click data');
            return false;
        }
        
        // Update the dealer-drilldown-store using Dash's setProps
        try {
            const storeElement = document.querySelector('[id="dealer-drilldown-store"]');
            
            if (window.dash_clientside && window.dash_clientside.set_props) {
                console.log('📦 Updating dealer-drilldown-store with:', { dealer_name: dealerName });
                window.dash_clientside.set_props('dealer-drilldown-store', {
                    data: { dealer_name: dealerName }
                });
                console.log('✅ Store updated successfully!');
            } else if (storeElement) {
                // Fallback method - directly modify the store element
                console.log('📦 Using fallback method to update store');
                storeElement.textContent = JSON.stringify({ dealer_name: dealerName });
                
                // Trigger a change event to notify Dash
                const event = new Event('change', { bubbles: true });
                storeElement.dispatchEvent(event);
                console.log('✅ Store updated via fallback method');
            } else {
                console.error('❌ Could not find dealer-drilldown-store element');
            }
            
            // Visual feedback - add a subtle animation to the clicked slice
            const clickedSliceIndex = point.pointIndex;
            const update = {
                'pull': plotlyDiv.data[0].pull.map((val, idx) => 
                    idx === clickedSliceIndex ? 0.1 : val
                )
            };
            
            Plotly.restyle(plotlyDiv, update, 0).then(function() {
                console.log('✅ Visual feedback applied');
            }).catch(function(err) {
                console.warn('⚠️ Could not apply visual feedback:', err);
            });
            
        } catch (error) {
            console.error('❌ Error updating drill-down store:', error);
            console.error('   Stack trace:', error.stack);
        }
        
        return false; // Prevent any default behavior
    });
    
    // Add hover effect to indicate clickability
    plotlyDiv.on('plotly_hover', function(data) {
        plotlyDiv.style.cursor = 'pointer';
    });
    
    plotlyDiv.on('plotly_unhover', function(data) {
        plotlyDiv.style.cursor = 'default';
    });
    
    console.log('✅ Dealer drill-down handler configured successfully!');
    console.log('💡 Click on any dealer slice to see product breakdown');
}

// Setup state drill-down click handler
function setupStateDrillDown(plotlyDiv) {
    if (!plotlyDiv) {
        console.error('❌ No plotly div provided for state drill-down');
        return;
    }
    
    console.log('🔧 Configuring state pie chart for drill-down...');
    
    // Check if we're in a drill-down view already
    if (isInDrillDownView('state')) {
        console.log('ℹ️ Already in state drill-down view, skipping click handler setup');
        return;
    }
    
    // Remove any existing click handlers
    if (plotlyDiv.removeAllListeners) {
        plotlyDiv.removeAllListeners('plotly_click');
    }
    
    // Add click event listener
    plotlyDiv.on('plotly_click', function(data) {
        console.log('═══════════════════════════════════════');
        console.log('🖱️ STATE PIE CHART CLICKED!');
        console.log('📊 Click data:', data);
        console.log('📊 data.points:', data.points);
        console.log('═══════════════════════════════════════');
        
        // Prevent default action and stop propagation
        if (data && data.event) {
            data.event.preventDefault();
            data.event.stopPropagation();
        }
        
        if (!data.points || data.points.length === 0) {
            console.warn('⚠️ No points data in click event');
            return false;
        }
        
        const point = data.points[0];
        console.log('📍 Clicked point details:');
        console.log('   label:', point.label);
        console.log('   customdata:', point.customdata);
        console.log('   value:', point.value);
        console.log('   pointIndex:', point.pointIndex);
        
        // Get state name from customdata (full name) or label (display name)
        const stateName = point.customdata && point.customdata[0] 
            ? point.customdata[0] 
            : point.label;
        
        console.log('🗺️ Selected state:', stateName);
        
        if (!stateName) {
            console.error('❌ Could not extract state name from click data');
            return false;
        }
        
        // Update the state-drilldown-store using Dash's setProps
        try {
            const storeElement = document.querySelector('[id="state-drilldown-store"]');
            
            if (window.dash_clientside && window.dash_clientside.set_props) {
                console.log('📦 Updating state-drilldown-store with:', { state_name: stateName });
                window.dash_clientside.set_props('state-drilldown-store', {
                    data: { state_name: stateName }
                });
                console.log('✅ Store updated successfully!');
            } else if (storeElement) {
                // Fallback method - directly modify the store element
                console.log('📦 Using fallback method to update store');
                storeElement.textContent = JSON.stringify({ state_name: stateName });
                
                // Trigger a change event to notify Dash
                const event = new Event('change', { bubbles: true });
                storeElement.dispatchEvent(event);
                console.log('✅ Store updated via fallback method');
            } else {
                console.error('❌ Could not find state-drilldown-store element');
            }
            
            // Visual feedback - add a subtle animation to the clicked slice
            const clickedSliceIndex = point.pointIndex;
            const update = {
                'pull': plotlyDiv.data[0].pull.map((val, idx) => 
                    idx === clickedSliceIndex ? 0.1 : val
                )
            };
            
            Plotly.restyle(plotlyDiv, update, 0).then(function() {
                console.log('✅ Visual feedback applied');
            }).catch(function(err) {
                console.warn('⚠️ Could not apply visual feedback:', err);
            });
            
        } catch (error) {
            console.error('❌ Error updating state drill-down store:', error);
            console.error('   Stack trace:', error.stack);
        }
        
        return false; // Prevent any default behavior
    });
    
    // Add hover effect to indicate clickability
    plotlyDiv.on('plotly_hover', function(data) {
        plotlyDiv.style.cursor = 'pointer';
    });
    
    plotlyDiv.on('plotly_unhover', function(data) {
        plotlyDiv.style.cursor = 'default';
    });
    
    console.log('✅ State drill-down handler configured successfully!');
    console.log('💡 Click on any state slice to see dealer breakdown');
}

// Setup state-dealer drill-down click handler (second level: dealer → products within a state)
function setupStateDealerDrillDown(plotlyDiv, stateName) {
    if (!plotlyDiv) {
        console.error('❌ No plotly div provided for state-dealer drill-down');
        return;
    }
    
    console.log('🔧 Configuring dealer pie chart for state drill-down (second level)...');
    console.log('🗺️ State context:', stateName);
    
    // Remove any existing click handlers
    if (plotlyDiv.removeAllListeners) {
        plotlyDiv.removeAllListeners('plotly_click');
    }
    
    // Add click event listener
    plotlyDiv.on('plotly_click', function(data) {
        console.log('═══════════════════════════════════════');
        console.log('🖱️ DEALER PIE CHART CLICKED (IN STATE VIEW)!');
        console.log('📊 Click data:', data);
        console.log('🗺️ State context:', stateName);
        console.log('═══════════════════════════════════════');
        
        // Prevent default action and stop propagation
        if (data && data.event) {
            data.event.preventDefault();
            data.event.stopPropagation();
        }
        
        if (!data.points || data.points.length === 0) {
            console.warn('⚠️ No points data in click event');
            return false;
        }
        
        const point = data.points[0];
        console.log('📍 Clicked point:', point);
        
        // Get dealer name from customdata (full name) or label (display name)
        const dealerName = point.customdata && point.customdata[0] 
            ? point.customdata[0] 
            : point.label;
        
        console.log('🏪 Selected dealer:', dealerName);
        
        if (!dealerName) {
            console.error('❌ Could not extract dealer name from click data');
            return false;
        }
        
        // Update the state-dealer-drilldown-store using Dash's setProps
        try {
            const storeElement = document.querySelector('[id="state-dealer-drilldown-store"]');
            
            if (window.dash_clientside && window.dash_clientside.set_props) {
                console.log('📦 Updating state-dealer-drilldown-store with:', { dealer_name: dealerName });
                window.dash_clientside.set_props('state-dealer-drilldown-store', {
                    data: { dealer_name: dealerName }
                });
                console.log('✅ Store updated successfully!');
            } else if (storeElement) {
                // Fallback method - directly modify the store element
                console.log('📦 Using fallback method to update store');
                storeElement.textContent = JSON.stringify({ dealer_name: dealerName });
                
                // Trigger a change event to notify Dash
                const event = new Event('change', { bubbles: true });
                storeElement.dispatchEvent(event);
                console.log('✅ Store updated via fallback method');
            } else {
                console.error('❌ Could not find state-dealer-drilldown-store element');
            }
            
            // Visual feedback - add a subtle animation to the clicked slice
            const clickedSliceIndex = point.pointIndex;
            const update = {
                'pull': plotlyDiv.data[0].pull.map((val, idx) => 
                    idx === clickedSliceIndex ? 0.1 : val
                )
            };
            
            Plotly.restyle(plotlyDiv, update, 0).then(function() {
                console.log('✅ Visual feedback applied');
            }).catch(function(err) {
                console.warn('⚠️ Could not apply visual feedback:', err);
            });
            
        } catch (error) {
            console.error('❌ Error updating state-dealer drill-down store:', error);
            console.error('   Stack trace:', error.stack);
        }
        
        return false; // Prevent any default behavior
    });
    
    // Add hover effect to indicate clickability
    plotlyDiv.on('plotly_hover', function(data) {
        plotlyDiv.style.cursor = 'pointer';
    });
    
    plotlyDiv.on('plotly_unhover', function(data) {
        plotlyDiv.style.cursor = 'default';
    });
    
    console.log('✅ State-dealer drill-down handler configured successfully!');
    console.log('💡 Click on any dealer slice to see products sold in ' + stateName);
}

// Watch for state-dealer chart being created in the fullscreen container
document.addEventListener('DOMContentLoaded', function() {
    const fullscreenContainer = document.getElementById('fullscreen-chart-container');
    if (fullscreenContainer) {
        const chartObserver = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) {  // Element node
                        // Check if the state-dealer-chart was added
                        let stateDealerChart = null;
                        let chartWrapper = null;
                        
                        if (node.id === 'state-dealer-chart') {
                            stateDealerChart = node;
                            chartWrapper = node.parentElement;  // Get wrapper div
                        } else {
                            stateDealerChart = node.querySelector('#state-dealer-chart');
                            if (stateDealerChart) {
                                chartWrapper = stateDealerChart.parentElement;  // Get wrapper div
                            }
                        }
                        
                        if (stateDealerChart && chartWrapper) {
                            console.log('🔍 Detected state-dealer-chart being created!');
                            
                            // Get the state name from the wrapper's data attribute
                            const stateName = chartWrapper.getAttribute('data-state-name');
                            
                            // Wait for Plotly to initialize the chart
                            setTimeout(function() {
                                const plotlyDiv = stateDealerChart.querySelector('.js-plotly-plot') || stateDealerChart;
                                if (plotlyDiv && plotlyDiv.data) {
                                    console.log('✅ Found Plotly chart in state-dealer view');
                                    setupStateDealerDrillDown(plotlyDiv, stateName);
                                } else {
                                    console.warn('⚠️ Plotly chart not ready yet, retrying...');
                                    setTimeout(function() {
                                        const retryDiv = stateDealerChart.querySelector('.js-plotly-plot') || stateDealerChart;
                                        if (retryDiv && retryDiv.data) {
                                            setupStateDealerDrillDown(retryDiv, stateName);
                                        }
                                    }, 500);
                                }
                            }, 300);
                        }
                    }
                });
            });
        });
        
        chartObserver.observe(fullscreenContainer, {
            childList: true,
            subtree: true
        });
        
    }
});

// Enhanced interaction for single-slice pie charts
function enhanceSingleSliceInteraction(plotlyDiv, chartId) {
    if (!plotlyDiv || !plotlyDiv.data || !plotlyDiv.data[0]) {
        return;
    }
    
    // Check if this is a single-slice chart
    const data = plotlyDiv.data[0];
    const sliceCount = data.values ? data.values.length : 0;
    
    if (sliceCount === 1) {
        console.log('🔵 Single-slice chart detected - enhancing interactivity');
        
        // Make the single slice slightly pulled out by default to indicate clickability
        const update = {
            'pull': [0.08]  // Slightly pull out the single slice
        };
        
        Plotly.restyle(plotlyDiv, update, 0).then(function() {
            console.log('✅ Single-slice enhancement applied');
        }).catch(function(err) {
            console.warn('⚠️ Could not apply single-slice enhancement:', err);
        });
        
        // Add a note to the layout indicating it's clickable
        if (plotlyDiv.layout) {
            const currentTitle = plotlyDiv.layout.title;
            const titleText = currentTitle && currentTitle.text ? currentTitle.text : '';
            
            // Add annotation to indicate clickability
            const annotation = {
                text: '👆 Click to see detailed breakdown',
                x: 0.5,
                y: -0.15,
                xref: 'paper',
                yref: 'paper',
                showarrow: false,
                font: {
                    size: 12,
                    color: '#6366f1'
                },
                xanchor: 'center'
            };
            
            const layoutUpdate = {
                annotations: [annotation]
            };
            
            Plotly.relayout(plotlyDiv, layoutUpdate).then(function() {
                console.log('✅ Clickability annotation added');
            }).catch(function(err) {
                console.warn('⚠️ Could not add annotation:', err);
            });
        }
    } else {
        console.log('ℹ️ Multi-slice chart detected (' + sliceCount + ' slices)');
    }
}

// Make sure window is loaded before setting up
window.addEventListener('load', function() {
    // Safe to access DOM and Dash components here
    console.log('✅ Window loaded - you can safely interact with the page');
});

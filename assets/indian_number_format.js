/**
 * Format number with Indian numbering system (lakhs and crores)
 * Examples: 1,234 | 12,345 | 1,23,456 | 12,34,567 | 1,23,45,678
 */
function formatIndianNumber(num) {
    if (num === null || num === undefined || isNaN(num)) return '0';
    
    // Handle decimals
    let numStr = Math.round(num).toString();
    let negative = numStr.startsWith('-');
    if (negative) numStr = numStr.substring(1);
    
    // For numbers less than 1000, no comma needed
    if (numStr.length <= 3) {
        return (negative ? '-' : '') + numStr;
    }
    
    // Indian numbering: last 3 digits, then groups of 2
    let result = numStr.slice(-3);
    numStr = numStr.slice(0, -3);
    
    while (numStr.length > 0) {
        if (numStr.length <= 2) {
            result = numStr + ',' + result;
            break;
        } else {
            result = numStr.slice(-2) + ',' + result;
            numStr = numStr.slice(0, -2);
        }
    }
    
    return (negative ? '-' : '') + result;
}

/**
 * Format currency in Indian style
 */
function formatIndianCurrency(num) {
    if (num === null || num === undefined || isNaN(num)) return '₹0';
    return '₹' + formatIndianNumber(num);
}

// Make functions globally available
window.formatIndianNumber = formatIndianNumber;
window.formatIndianCurrency = formatIndianCurrency;

console.log('Indian number formatting loaded');

# Business Analytics Dashboard

A comprehensive, interactive business analytics dashboard built with Streamlit for analyzing sales, purchases, customer insights, and payment data. Data is fetched from the Avante Medicals ERP API.

## Features

### 🔐 Secure Authentication
- Login with your ERP credentials
- Token-based authentication with automatic refresh
- Secure session management

### 📊 Sales Analytics
- Revenue & Quantity Insights with pie charts by Dealer, State, and Executive
- Month-wise trends for revenue and quantity sold
- Product family comparisons
- Dealer ranking
- Predictive sales forecasting using linear regression

### 🛒 Purchase Analytics
- Purchase amount and quantity analysis by vendor
- Material-wise purchase trends
- Slow-moving purchases identification

### 👥 Customer Insights
- Interactive drill-down analysis (State → City → Executive)
- Non-moving and slow-moving items tracker
- Cross-selling opportunities analysis
- Product drop-off tracker (month-over-month decline)

### 💳 Payment & Credit Analysis
- Overdue payments tracking
- Aging bucket analysis (0-30, 31-60, 61-90, 91-120, 120+ days)
- Interest calculation on overdue payments

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Bhurva6/sales-dashboard.git
cd sales-dashboard
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
source venv/bin/activate  # Activate virtual environment
streamlit run dashboard.py
```

2. Login with your ERP credentials:
   - Enter your username and password
   - Click "Login" to authenticate

3. The dashboard will automatically fetch data from the API and display analytics across four tabs:
   - Sales Analytics
   - Purchase Analytics
   - Customer Insights
   - Payment Analysis

4. Use the sidebar controls:
   - **Refresh Data**: Fetch latest data from the API
   - **Logout**: End your session securely

## API Integration

The dashboard connects to the Avante Medicals ERP API:
- **Base URL**: `http://avantemedicals.com/API/api.php`
- **Authentication**: JWT token-based
- **Auto-refresh**: Tokens are automatically refreshed when expired

### API Endpoints Used:
- `POST ?action=login` - User authentication
- `POST ?action=protected` - Fetch protected sales data
- `POST ?action=refresh_token` - Refresh access token
- `POST ?action=logout` - End session

## Data Format

Your Excel file should have a `Type` column to categorize rows:
- `Sales` - for sales transactions
- `Purchase` - for purchase transactions  
- `Payment` - for payment/credit data

See `combined_dummy.xlsx` for a sample data format (if included).

## Technologies Used

- **Streamlit** - Web application framework
- **Pandas** - Data manipulation and analysis
- **Plotly** - Interactive visualizations
- **Scikit-learn** - Predictive analytics
- **NumPy** - Numerical computing
- **Requests** - API communication
- **JWT** - Token-based authentication

## Features Overview

- 📱 Mobile-responsive design
- 🔄 Real-time data processing
- 📈 Interactive charts and graphs
- 🎯 Drill-down analysis capabilities
- ⚡ Fast data preview
- 🎨 Clean, modern UI

## Project Structure

```
dashboard/
├── dashboard.py       # Main Streamlit application
├── api_client.py      # API client for ERP integration
├── requirements.txt   # Python dependencies
├── README.md          # Documentation
├── venv/              # Virtual environment (not in repo)
└── .gitignore         # Git ignore file
```

## Security Notes

- Credentials are never stored locally
- Tokens are stored in session state only
- Automatic logout on session end
- Secure HTTPS communication with API

## Contributing

Feel free to open issues or submit pull requests for improvements.

## License

MIT License

## Contact

For questions or support, please open an issue on GitHub.

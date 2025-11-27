# Business Analytics Dashboard

A comprehensive, interactive business analytics dashboard built with Streamlit for analyzing sales, purchases, customer insights, and payment data.

## Features

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
streamlit run dashboard.py
```

2. Upload your Excel file with the following structure:
   - **Required column**: `Type` with values: 'Sales', 'Purchase', or 'Payment'
   - **Sales columns**: Date, Month, Dealer, State, City, Executive, Product, Product Family, Quantity, Unit Price, Revenue, Payment Status, Days Overdue, Interest Amount
   - **Purchase columns**: Date, Month, Vendor, Material, Quantity, Unit Price, Purchase Amount
   - **Payment columns**: Customer, Amount, Due Date, Days Overdue, Interest Amount, Region, Executive

3. Explore the analytics across four tabs:
   - Sales Analytics
   - Purchase Analytics
   - Customer Insights
   - Payment Analysis

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
- **OpenPyXL** - Excel file handling

## Features Overview

- 📱 Mobile-responsive design
- 🔄 Real-time data processing
- 📈 Interactive charts and graphs
- 🎯 Drill-down analysis capabilities
- ⚡ Fast data preview
- 🎨 Clean, modern UI

## Contributing

Feel free to open issues or submit pull requests for improvements.

## License

MIT License

## Contact

For questions or support, please open an issue on GitHub.

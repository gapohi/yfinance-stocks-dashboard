## Project Overview

This project retrieves stock data from Yahoo Finance, stores it in MongoDB, and visualizes it using a Dash dashboard.  

## Disclaimer on Financial Decisions

The use of this software and the provided data should not be considered as financial advice. No responsibility is assumed for any financial decisions made based on the data or results obtained from the software. Users are responsible for conducting their own research and making informed decisions.

## Directory Structure

Here’s an overview of the project directory structure:

```plaintext
yfinance-stocks-dashboard/
├── src/
│   ├── stocks.py        # Retrieves stock data from Yahoo Finance and stores it in MongoDB
│   ├── dashboard.py     # Builds the Dash dashboard to visualize stock data
│   └── main.py          # Main entry point for running the project, starts the dashboard and data retrieval
├── .gitignore           # For ignoring unnecessary files in a Python/Dash project
├── LICENSE              # MIT License
├── README.md            # Project overview and setup instructions
```

## Requirements

The following libraries are required to run this project:

*   `dash`
*   `dash_table`
*   `pandas`
*   `plotly`
*   `pymongo`
*   `requests`
*   `yfinance`

This project was developed using Python version 3.11.5.

## Installation

1. Clone the repository to your local machine:
```bash
git clone https://github.com/gapohi/yfinance-stocks-dashboard.git
```

2. Navigate to the repository directory:
```bash
cd yfinance-stocks-dashboard
```

3. Install the required libraries:
```bash
pip install dash dash_table pandas plotly pymongo requests yfinance
```

4. Run the main.py file
```bash
cd src
python main.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would 
like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
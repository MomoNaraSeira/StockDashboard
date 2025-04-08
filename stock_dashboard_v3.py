import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
from fredapi import Fred
from dash.exceptions import PreventUpdate
import datetime


# Enhanced news function with sample data fallbacks
def get_stock_news(ticker_symbol):
    # Sample pre-defined news data for major stocks as a fallback
    sample_news = {
        
    }
    
    # Default news for stocks not in our sample data
    default_news = {
        'title': f"Market Updates for {ticker_symbol}",
        'summary': f"Stay informed with the most recent News, Market Developments and Analyst Opinions on {ticker_symbol}.",
        'link': f"https://finance.yahoo.com/quote/{ticker_symbol}/news/",
        'source': "Financial News Network"
    }
    
    try:
        # First attempt: Try to get news from yfinance
        ticker = yf.Ticker(ticker_symbol)
        news = ticker.news
        
        if news and len(news) > 0:
            latest_news = news[0]
            
            # Try to extract timestamp
            timestamp = None
            for time_key in ['providerPublishTime', 'published', 'publishedAt', 'time']:
                if time_key in latest_news and latest_news[time_key]:
                    try:
                        timestamp = datetime.datetime.fromtimestamp(latest_news[time_key])
                        break
                    except:
                        pass
            
            if not timestamp:
                timestamp = datetime.datetime.now()
                
            formatted_date = timestamp.strftime("%b %d, %Y %H:%M")
            
            # Try to extract publisher
            publisher_name = "Unknown Source"
            if 'publisher' in latest_news:
                publisher = latest_news['publisher']
                if isinstance(publisher, dict) and 'name' in publisher:
                    publisher_name = publisher['name']
                elif isinstance(publisher, str):
                    publisher_name = publisher
            
            # Check if we have valid title and summary
            title = latest_news.get('title')
            summary = latest_news.get('summary', latest_news.get('body', ''))
            link = latest_news.get('link', f'https://finance.yahoo.com/quote/{ticker_symbol}/news/')
            
            if title and summary:  # Only use yfinance data if we have both title and summary
                return {
                    'title': title,
                    'summary': summary,
                    'link': link,
                    'date': formatted_date,
                    'source': publisher_name
                }
        
        # Second attempt: Use our sample data if available
        if ticker_symbol in sample_news:
            news_item = sample_news[ticker_symbol]
            news_item['date'] = datetime.datetime.now().strftime("%b %d, %Y %H:%M")
            return news_item
        
        # Third attempt: Use default generic news
        default_news['date'] = datetime.datetime.now().strftime("%b %d, %Y %H:%M")
        return default_news
        
    except Exception as e:
        # If all else fails, use either sample data or default news
        if ticker_symbol in sample_news:
            news_item = sample_news[ticker_symbol]
            news_item['date'] = datetime.datetime.now().strftime("%b %d, %Y %H:%M")
            return news_item
        
        default_news['date'] = datetime.datetime.now().strftime("%b %d, %Y %H:%M")
        return default_news

# Company Descriptions
COMPANY_DESCRIPTIONS = {
    "AAPL": (
        "Apple Inc. is a multinational technology company that designs and manufactures consumer electronics like the iPhone, iPad, and Mac computers. It also offers services such as the App Store, Apple Music, and iCloud. Apple is known for its innovative products and strong brand loyalty.",
        "https://logo.clearbit.com/apple.com"
    ),
    "MSFT": (
        "Microsoft Corporation develops, licenses, and supports a range of software products, including the Windows operating system and Office suite. It also offers cloud computing services through Azure and owns LinkedIn and GitHub. Microsoft is one of the world's largest technology companies.",
        "https://logo.clearbit.com/microsoft.com"
    ),
    "GOOGL": (
        "Alphabet Inc. is the parent company of Google LLC, specializing in internet-related services and products. Its offerings include the Google search engine, YouTube, and the Android operating system. Alphabet also invests in various technology ventures through its 'Other Bets' segment.",
        "https://logo.clearbit.com/abc.xyz"
    ),
    "AMZN": (
        "Amazon.com, Inc. is a multinational technology company focusing on e-commerce, cloud computing, and artificial intelligence. It operates the world's largest online marketplace and offers cloud services through Amazon Web Services (AWS). Amazon also produces consumer electronics like the Kindle and Echo devices.",
        "https://logo.clearbit.com/amazon.com"
    ),
    "NVDA": (
        "NVIDIA Corporation designs and manufactures graphics processing units (GPUs) for gaming, professional visualization, data centers, and automotive markets. Its GPUs are widely used in artificial intelligence and high-performance computing applications. NVIDIA has become a leader in the semiconductor industry.",
        "https://logo.clearbit.com/nvidia.com"
    ),
    "BRK-B": (
        "Berkshire Hathaway Inc. is a multinational conglomerate holding company led by CEO Warren Buffett. Its subsidiaries operate in various industries, including insurance, utilities, manufacturing, and retail. Berkshire Hathaway also holds significant equity investments in companies like Apple and Coca-Cola.",
        "https://logo.clearbit.com/berkshirehathaway.com"
    ),
    "TSLA": (
        "Tesla, Inc. specializes in electric vehicles (EVs), energy storage, and solar energy solutions. Its product lineup includes electric cars like the Model S, Model 3, and Model X, as well as solar panels and energy storage systems. Tesla aims to accelerate the world's transition to sustainable energy.",
        "https://logo.clearbit.com/tesla.com"
    ),
    "META": (
        "Meta Platforms, Inc., formerly known as Facebook, focuses on building technologies that help people connect and share. Its products include social media platforms like Facebook, Instagram, and WhatsApp. Meta is also investing in virtual and augmented reality through its Reality Labs division.",
        "https://logo.clearbit.com/meta.com"
    ),
    "UNH": (
        "UnitedHealth Group Incorporated is a diversified health care company offering health care coverage and benefits through UnitedHealthcare. It also provides health care services and technology through Optum. UnitedHealth Group serves millions of individuals globally.",
        "https://logo.clearbit.com/unitedhealthgroup.com"
    ),
    "JNJ": (
        "Johnson & Johnson is a multinational corporation that develops medical devices, pharmaceuticals, and consumer health products. Its well-known brands include Band-Aid, Tylenol, and Neutrogena. J&J operates in over 60 countries and has a strong reputation for quality and innovation.",
        "https://logo.clearbit.com/jnj.com"
    ),
    "XOM": (
        "Exxon Mobil Corporation is a multinational oil and gas corporation engaged in the exploration, production, and distribution of petroleum and petrochemical products. It operates globally and has a significant presence in both upstream and downstream segments. ExxonMobil is one of the world's largest publicly traded energy providers.",
        "https://logo.clearbit.com/exxonmobil.com"
    ),
    "JPM": (
        "JPMorgan Chase & Co. is a leading global financial services firm offering investment banking, financial services, and asset management. It serves millions of customers and many of the world's prominent corporate, institutional, and government clients. JPMorgan Chase is known for its strong balance sheet and extensive global operations.",
        "https://logo.clearbit.com/jpmorganchase.com"
    ),
    "V": (
        "Visa Inc. is a global payments technology company facilitating electronic funds transfers worldwide. It offers products like credit, debit, and prepaid cards, as well as payment systems for merchants and consumers. Visa's network connects millions of merchants and financial institutions.",
        "https://logo.clearbit.com/visa.com"
    ),
    "PG": (
        "The Procter & Gamble Company is a multinational consumer goods corporation specializing in a wide range of personal health, hygiene, and home care products. Its brands include Tide, Pampers, and Gillette. P&G operates in over 180 countries and is known for its focus on innovation and quality.",
        "https://logo.clearbit.com/pg.com"
    ),
    "MA": (
        "Mastercard Incorporated is a global financial services company offering payment processing and related services. It facilitates transactions between consumers, financial institutions, merchants, and governments. Mastercard's products include credit, debit, and prepaid cards, as well as payment solutions for businesses.",
        "https://logo.clearbit.com/mastercard.com"
    ),
    "LLY": (
        "Eli Lilly and Company is a global pharmaceutical company specializing in the discovery, development, and marketing of human pharmaceuticals. Its products address various therapeutic areas, including diabetes, oncology, and neuroscience. Lilly is committed to advancing medical science and improving patient outcomes.",
        "https://logo.clearbit.com/lilly.com"
    ),
    "HD": (
        "The Home Depot, Inc. is the largest home improvement retailer in the United States, offering tools, construction products, appliances, and services. It caters to both do-it-yourself customers and professional contractors. Home Depot operates numerous stores across North America and has a significant online presence.",
        "https://logo.clearbit.com/homedepot.com"
    ),
    "AVGO": (
        "Broadcom Inc. is a global technology company that designs, develops, and supplies a broad range of semiconductor and infrastructure software solutions. Its products serve various markets, including data centers, networking, software, and broadband. Broadcom's innovations are integral to modern digital infrastructures.",
        "https://logo.clearbit.com/broadcom.com"
    ),
    "MRK": (
        "Merck & Co., Inc., known as MSD outside the United States and Canada, is a global pharmaceutical company. It develops prescription medicines, vaccines, biologic therapies, and animal health products. Merck is committed to improving health and well-being around the world.",
        "https://logo.clearbit.com/merck.com"
    ),
    "CVX": (
        "Chevron Corporation is a multinational energy corporation involved in every aspect of the oil, natural gas, and geothermal energy industries. It explores, produces, refines, and markets these energy resources globally. Chevron is also investing in renewable energy technologies.",
        "https://logo.clearbit.com/chevron.com"
    )
}

# List of top 30 US stocks
TOP_30_STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "UNH", "JNJ",
                  "XOM", "JPM", "V", "PG", "MA", "CVX", "HD", "LLY", "MRK", "PEP",
                  "ABBV", "KO", "AVGO", "COST", "MCD", "TMO", "DIS", "CSCO", "VZ", "ADBE"]

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# FRED API key
FRED_API_KEY = "eeeb34acccfb7941a4d425282ee7342d"
fred = Fred(api_key=FRED_API_KEY)

# Macroeconomic Data Series IDs and explanations
MACRO_INDICATORS = {
    "US Inflation": ("CPIAUCSL", "Higher inflation erodes purchasing power, often leading to increased costs for companies and decreased consumer spending, which can negatively impact stock prices."),
    "US Interest Rate": ("FEDFUNDS", "Increased interest rates can make borrowing more expensive for companies, potentially slowing down growth and negatively affecting stock valuations. Conversely, lower rates can stimulate growth."),
    "US GDP Growth": ("GDP", "Strong GDP growth usually indicates a healthy economy, boosting company profits and investor confidence, which typically leads to higher stock prices."),
    "US Unemployment Rate": ("UNRATE", "A low unemployment rate suggests a strong labor market, which can lead to increased consumer spending and higher corporate earnings, generally positive for stocks.")
}

# Investor Profile Questions
INVESTOR_QUESTIONS = [
    "I am comfortable with the possibility of losing money in exchange for potentially higher returns.",
    "I have a long time horizon (10+ years) before I need to use my investments.",
    "I am knowledgeable about different investment options and strategies.",
    "I tend to make investment decisions based on logic and analysis rather than emotion.",
    "I would get stressed if my investment portfolio suddenly decreased in value by 20%." # New Question
]

# Layout
app.layout = dbc.Container([
    dbc.Row([
        # Header with Title and Tabs aligned to the left
        dbc.Col([
            dbc.Row([  # Header row
                dbc.Col(html.H1("Stock Dashboard 101", className="text-center", style={"color": "white", "padding": "15px"}), width=9),
                dbc.Col(dcc.Tabs(id="main-tabs", value="intro", children=[  # Set initial value to 'intro'
                    dcc.Tab(label="Introduction", value="intro", style={"fontSize": "20px", "padding": "5px 10px", "backgroundColor": "#8B5DFF"}),
                    dcc.Tab(label="Stock Data", value="stock-data", style={"fontSize": "20px", "padding": "5px 10px", "backgroundColor": "#8B5DFF"}),
                    dcc.Tab(label="Macroeconomic Indicators", value="macro-indicators", style={"fontSize": "20px", "padding": "5px 10px", "backgroundColor": "#8B5DFF"})
                ], className="mb-3", style={"display": "flex", "justifyContent": "flex-start", "marginTop": "10px", "fontSize": "20px"}), width=3)
            ])
        ], width=12)
    ], style={"backgroundColor": "#4B0082"}),  # Dark purple background for header
    dbc.Row([
        dbc.Col([  # Main content area for selected tab
            html.Div(id="tabs-content")
        ], width=12)
    ])
], fluid=True)

# Callback for updating the content in the tabs
@app.callback(
    Output("tabs-content", "children"),
    [Input("main-tabs", "value")]
)
def render_tabs_content(selected_tab):
    if selected_tab == "stock-data":
        return html.Div([  # The content for the "Stock Data" tab
            dbc.Row([
                dbc.Col([
                    html.Label("Select a Company Stock", style={"color": "white", "fontSize": "25px"}),
                    dcc.Dropdown(
                        id="stock-dropdown",
                        options=[{"label": stock, "value": stock} for stock in TOP_30_STOCKS],
                        value="NVDA",
                        clearable=False,
                        className="mb-3",
                        style={"color": "black", "fontSize": "20px", "fontWeight": "bold"}
                    ),
                    html.Div(id="company-header", className="text-center text-white mb-3"),
                    html.Img(id="company-logo", style={"display": "block", "margin": "0 auto", "maxHeight": "50px"}),
                    html.Label("Select a Timeline for Stock Prices", style={"color": "white", "fontSize": "25px"}),
                    dcc.Tabs(id="price-range-tabs", value="10y", children=[
                        dcc.Tab(label="All", value="max", style={"fontSize": "20px", "padding": "5px 10px","backgroundColor": "#8B5DFF"}),
                        dcc.Tab(label="10Y", value="10y", style={"fontSize": "20px", "padding": "5px 10px", "backgroundColor": "#8B5DFF"}),
                        dcc.Tab(label="5Y", value="5y", style={"fontSize": "20px", "padding": "5px 10px", "backgroundColor": "#8B5DFF"}),
                        dcc.Tab(label="1Y", value="1y", style={"fontSize": "20px", "padding": "5px 10px", "backgroundColor": "#8B5DFF"})
                    ], className="mb-3"),
                    dcc.Graph(id="stock-price-chart", style={"height": "825px", "border": "1px solid lightgrey"})
                ], width=6),
                dbc.Col([
                    dcc.Tabs(id="tabs", value="performance", children=[
                        dcc.Tab(label="Performance", value="performance", style={"fontSize": "20px", "padding": "5px 10px", "backgroundColor": "#8B5DFF"}),
                        dcc.Tab(label="Background Info", value="background", style={"fontSize": "20px", "padding": "5px 10px", "backgroundColor": "#8B5DFF"})
                    ], className="mb-3"),
                    html.Div(id="tab-content")
                ], width=6)
            ])
        ])
    elif selected_tab == "intro":
        return dbc.Row([
            dbc.Col([
                # Carousel for Introduction Slides
                dbc.Carousel(
                    items=[
                        {"key": f"slide-{i}", "src": f"StockDashboard/assets/slide ({i}).png", "img_style": {"width": "100%", "height": "auto"}} # Make sure the path is correct.
                        for i in range(7)
                    ],
                    controls=True,
                    indicators=False,
                    interval=6000,  # 6 seconds
                    ride="carousel",
                    className="carousel-fade",
                ),
                # Info Cards
                html.Div([
                    dbc.Row([
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.H5("What is a Stock?", className="card-title"),
                                    html.P("A stock represents ownership in a company. Buying shares makes you a part-owner."),
                                    dbc.Button(
                                        "Learn More", 
                                        color="primary", 
                                        href="https://www.investopedia.com/terms/s/stock.asp",
                                        target="_blank")
                                ]),
                                className="mb-3", style={"width": "15rem", "height":"15rem"}
                            ), width=3
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.H5("How Do Dividends Work?", className="card-title"),
                                    html.P("Dividends are company profits shared with shareholders as regular payouts."),
                                    dbc.Button(
                                        "Learn More", 
                                        color="primary", 
                                        href="https://www.investopedia.com/terms/d/dividend.asp",
                                        target="_blank")
                                ]),
                                className="mb-3", style={"width": "15rem", "height":"15rem"}
                            ), width=3
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.H5("What Affects Stock Prices?", className="card-title"),
                                    html.P("Stock prices change due to supply and demand, company performance, and economic factors."),
                                    dbc.Button(
                                        "Learn More", 
                                        color="primary", 
                                        href="https://www.investopedia.com/articles/basics/04/100804.asp",
                                        target="_blank")
                                ]),
                                className="mb-3", style={"width": "15rem" , "height":"15rem"}
                            ), width=3
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([
                                    html.H5("How To Get Started?", className="card-title"),
                                    html.P("Investing in stocks can be a powerful way to grow your wealth over time."),
                                    dbc.Button(
                                        "Learn More", 
                                        color="primary", 
                                        href="https://www.investopedia.com/articles/basics/06/invest1000.asp",
                                        target="_blank")
                                ]),
                                className="mb-3", style={"width": "15rem", "height":"15rem"}
                            ), width=3
                        )
                    ], justify="center")  # Centers the row of cards
                ], style={"marginTop": "30px"})
            ], width=6),  # Left side - Introduction content

            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Investor Persona Quiz", className="card-title", style={"color": "black", "fontSize": "24px"}),
                        html.P("Answer the following questions to determine your investor profile:", className="card-text", style={"color": "black", "fontSize": "20px"}),
                        html.P("For each statement, choose a number from 1 to 5, where 1 means 'Strongly Disagree' and 5 means 'Strongly Agree'.", style={"color": "black", "fontSize": "20px"}),

                        # Questions and Likert Scales
                        html.Div([
                            dbc.Row([
                                dbc.Col(html.P(f"{i+1}. {question}", style={"fontWeight": "bold", "color": "black", "fontSize": "22px", "marginBottom": "15px"}), width=8),  # Increased font size and margin
                                dbc.Col(
                                    dcc.RadioItems(
                                        id=f"q{i+1}-likert",
                                        options=[{"label": i, "value": i} for i in range(1, 6)],
                                        inline=True,
                                        labelStyle={'marginRight': '15px', "fontSize": "18px", 'color': 'black'} # font size of radio items and color of radio items
                                    ), width=4
                                )
                            ], style={"marginBottom": "20px"}) # Add line spacing between each question
                            for i, question in enumerate(INVESTOR_QUESTIONS)
                        ]),

                        html.Div(id="quiz-result", style={"marginTop": "20px", "fontSize": "20px"}),
                        dbc.Button("Submit", id="submit-button", color="primary"),
                        dbc.Button("Restart", id="restart-button", color="secondary", style={"marginLeft": "10px"}),

                    ]),
                    style={"backgroundColor": "lightgrey", "height": "100%"}
                )
            ], width=6)  # Right side - Investor Persona Quiz
        ])
    elif selected_tab == "macro-indicators":
        return html.Div([  # Content for "Macroeconomic Indicators" tab
            dcc.Tabs(id="macro-tabs", value="US Inflation", children=[
                dcc.Tab(label="US Inflation", value="US Inflation", style={"fontSize": "16px", "padding": "5px 10px", "backgroundColor": "#8B5DFF"}),
                dcc.Tab(label="US Interest Rate", value="US Interest Rate", style={"fontSize": "16px", "padding": "5px 10px", "backgroundColor": "#8B5DFF"}),
                dcc.Tab(label="US GDP Growth", value="US GDP Growth", style={"fontSize": "16px", "padding": "5px 10px", "backgroundColor": "#8B5DFF"}),
                dcc.Tab(label="US Unemployment Rate", value="US Unemployment Rate", style={"fontSize": "16px", "padding": "5px 10px", "backgroundColor": "#8B5DFF"})
            ], className="mb-3"),
             html.Div(
                id="macro-indicator-title-container",
                className="text-center mt-3",
                style={"position": "relative"}
            ),
            dcc.Graph(id="macro-indicator-chart", style={"height": "890px", "width": "100%"})
        ])

# Existing callback for stock data (unchanged)
@app.callback(
    [Output("company-header", "children"), Output("company-logo", "src"), Output("stock-price-chart", "figure")],
    [Input("stock-dropdown", "value"), Input("price-range-tabs", "value")]
)
def update_dashboard(selected_stock, selected_range):
    stock = yf.Ticker(selected_stock)
    info = stock.info
    hist = stock.history(period=selected_range)

    header = html.H2(f"{info.get('longName', selected_stock)} ({selected_stock})", className="text-white")
    logo_url = info.get("logo_url", "")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], fill='tozeroy', mode='lines', name='Stock Price', line=dict(color='indigo')))
    fig.update_layout(title="Stock Price", template="plotly_dark", xaxis=dict(gridcolor='purple'), yaxis=dict(gridcolor='purple'))

    return header, logo_url, fig

# Existing callback for performance and background info (unchanged)
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"), Input("stock-dropdown", "value")]
)
def update_tab_content(selected_tab, selected_stock):
    if not selected_stock:
        return html.Div("No stock selected", className="text-white")

    stock = yf.Ticker(selected_stock)
    info = stock.info
    years = list(range(2019, 2024))
    description, logo_url = COMPANY_DESCRIPTIONS.get(selected_stock, ("No description available.", ""))

    if selected_tab == "performance":
        fcf = [info.get("freeCashflow", 1e6) * (1.1 ** i) for i in range(5)]
        npm = [info.get("profitMargins", 0.1) * (1.1 ** i) for i in range(5)]
        roe = [info.get("returnOnEquity", 0.1) * (1.1 ** i) for i in range(5)]
        pe_ratio = info.get("trailingPE", 20)

        fig_fcf = go.Figure([go.Bar(x=years, y=fcf, marker_color="indigo")])
        fig_fcf.update_layout(title="", paper_bgcolor="lightgray", plot_bgcolor="lightgray", xaxis=dict(gridcolor='purple'), yaxis=dict(gridcolor='purple'))

        fig_npm = go.Figure([go.Bar(x=years, y=npm, marker_color="indigo")])
        fig_npm.update_layout(title="", paper_bgcolor="lightgray", plot_bgcolor="lightgray", xaxis=dict(gridcolor='purple'), yaxis=dict(gridcolor='purple'))

        fig_roe = go.Figure([go.Bar(x=years, y=roe, marker_color="indigo")])
        fig_roe.update_layout(title="", paper_bgcolor="lightgray", plot_bgcolor="lightgray", xaxis=dict(gridcolor='purple'), yaxis=dict(gridcolor='purple'))

        fig_pe = go.Figure([go.Indicator(
            mode="gauge+number",
            value=pe_ratio,
            title={"text": ""},
            gauge={
                'axis': {'range': [0, 60]},
                'bar': {'color': "indigo"},  # Change the gauge bar color
                'bgcolor': "white",  # Change background color of the gauge
                'bordercolor': "gray",  # Change the border color
                'borderwidth': 2
            }
        )])
        fig_pe.update_layout(paper_bgcolor="lightgray", plot_bgcolor="lightgray")

        return html.Div([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_fcf, style={"height": "350px"}), width=6),
                dbc.Col(dcc.Graph(figure=fig_npm, style={"height": "350px"}), width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H1("Free Cash Flow (FCF)", className="card-title fw-bold"),
                            html.P("Cash left after expenses and investments.", className="card-text"),
                            html.P("More FCF means growth, dividends, or debt reduction—good for investors.", className="card-text")
                        ])
                    ], className="h-100"),
                ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H1("Net Profit Margin", className="card-title fw-bold"),
                            html.P("Profit as a percentage of revenue.", className="card-text"),
                            html.P("Higher margin = better efficiency and profitability.", className="card-text")
                        ])
                    ], className="h-100"),
                ]),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_roe, style={"height": "350px"}), width=6),
                dbc.Col(dcc.Graph(figure=fig_pe, style={"height": "350px"}), width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H1("Return on Equity (ROE)", className="card-title fw-bold"),
                            html.P("Profit made from shareholders' equity.", className="card-text"),
                            html.P("High ROE means the company uses investor money well.", className="card-text")
                        ])
                    ], className="h-100"),
                ]),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H1("P/E Ratio", className="card-title fw-bold"),
                            html.P("Stock price divided by earnings per share.", className="card-text"),
                            html.P("Low P/E = undervalued, high P/E = growth potential (compare to industry).", className="card-text")
                        ])
                    ], className="h-100"),
                ]),
            ])
        ])
    else:
        # Get latest news for the selected stock
        news_data = get_stock_news(selected_stock)
        
        return html.Div([
            # Company title and logo
            html.Div([
                html.Img(src=logo_url, style={"display": "block", "margin": "10px auto", "maxHeight": "150px"})
            ], className="text-center mb-4"),

            # Description Card
            dbc.Card([
                dbc.CardBody([
                    html.H1("Description", className="card-title fw-bold"),
                    html.P(description, className="card-text", style={"fontSize":"24px"})
                ])
            ], className="mb-4"),

            # Industry, Sector, Website cards in a row
            dbc.Row([
                # Industry Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H1("Industry", className="card-title fw-bold"),
                            html.P(info.get('industry', 'N/A'), className="card-text", style={"fontSize":"24px"})
                        ])
                    ], className="h-100")
                ], width=4),

                # Sector Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H1("Sector", className="card-title fw-bold"),
                            html.P(info.get('sector', 'N/A'), className="card-text", style={"fontSize":"24px"})
                        ])
                    ], className="h-100")
                ], width=4),

                # Website Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H1("Website", className="card-title fw-bold"),
                            html.A(info.get('website', 'N/A'), href=info.get('website', '#'),
                                target="_blank", className="card-text", style={"fontSize":"24px"})
                        ])
                    ], className="h-100")
                ], width=4)
            ], className="mb-4"),
            
            # News Card (added below the row of Industry, Sector, Website)
            dbc.Card([
                dbc.CardBody([
                    html.H1(news_data['title'], className="card-title"),
                    html.P([
                        news_data['summary'][:300] + "..." if len(news_data['summary']) > 300 else news_data['summary']
                    ], className="card-text", style={"fontSize":"20px"}),
                    dbc.Button(
                        "Read More", 
                        color="primary", 
                        href=news_data['link'],
                        target="_blank"
                    )
                ])
            ], className="mb-4")
        ])

# Callback for updating macroeconomic indicator chart
@app.callback(
    [Output("macro-indicator-title-container", "children"), Output("macro-indicator-chart", "figure")],
    [Input("macro-tabs", "value")]
)
def update_macro_chart(selected_indicator):
    series_id, explanation = MACRO_INDICATORS[selected_indicator]
    data = fred.get_series(series_id)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data.values,
        mode='lines',
        name=selected_indicator,
        fill='tozeroy',  # Fill area under the line
        line=dict(color='indigo')
    ))
    fig.update_layout(
        title=selected_indicator,
        template="plotly_dark",
        xaxis=dict(gridcolor='purple'),
        yaxis=dict(gridcolor='purple'),
        xaxis_title="Date",
        yaxis_title=selected_indicator
    )

    indicator_title = html.H3(
        selected_indicator,
        className="text-center text-white mt-3",
        id="macro-indicator-title",
        style={"cursor": "pointer"}  # Change cursor to indicate it's clickable/hoverable
    )

    tooltip = dbc.Tooltip(
        explanation,
        target="macro-indicator-title",
        placement="bottom"
    )

    return [indicator_title, tooltip], fig

# Callback for Investor Persona Quiz
@app.callback(
    [Output("quiz-result", "children"),
     Output("q1-likert", "value"),
     Output("q2-likert", "value"),
     Output("q3-likert", "value"),
     Output("q4-likert", "value"),
     Output("q5-likert", "value")],
    [Input("submit-button", "n_clicks"), Input("restart-button", "n_clicks")],
    [State("q1-likert", "value"),
     State("q2-likert", "value"),
     State("q3-likert", "value"),
     State("q4-likert", "value"),
     State("q5-likert", "value")]
)
def determine_investor_profile(submit_clicks, restart_clicks, q1, q2, q3, q4, q5):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == "restart-button":
        return None, None, None, None, None, None

    if trigger_id == "submit-button":
        answers = [q1, q2, q3, q4, q5]
        if any(a is None for a in answers):
            return "Please answer all questions.", q1, q2, q3, q4, q5

        total_score = sum(answers)

        if total_score <= 12:
            profile = "Risk-Averse: You prefer low-risk investments that prioritize capital preservation. If you are risk-averse, you prefer safe and predictable outcomes over uncertain ones, even if the potential reward is higher. For example, you would rather keep your money in a savings account than invest in stocks that could go up or down. You prioritize security and avoiding losses over making big profits. Insurance companies and conservative investors often take a risk-averse approach."
        elif total_score <= 18:
            profile = "Risk-Neutral: You are comfortable with moderate risk to achieve moderate returns. If you are risk-neutral, you make decisions based only on expected returns, without worrying about the level of risk. You would be indifferent between a guaranteed $50 and a 50 percent chance of winning $100 because both have the same expected value. In business, you might focus purely on potential profits without factoring in uncertainty."
        else:
            profile = "Risk-Seeking: You are willing to take on higher risk for the potential of higher returns. If you are risk-seeking, you prefer uncertainty and are willing to take bigger risks for the chance of higher rewards. For example, you might gamble or invest in high-risk stocks, hoping for big returns despite the possibility of losing money. You enjoy excitement and are comfortable with uncertainty. Entrepreneurs and extreme sports athletes often have risk-seeking tendencies."

        return html.Div([
            html.H5("Your Investor Profile:", style={"fontWeight": "bold", "color": "black", "fontSize": "22px"}),
            html.P(profile, style={"color": "black", "fontSize": "20px"})
        ]), q1, q2, q3, q4, q5

    raise PreventUpdate

if __name__ == "__main__":
    app.run_server(debug=True)

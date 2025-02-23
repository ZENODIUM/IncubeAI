# Inqube AI

![inqube_thumbnail](https://github.com/user-attachments/assets/e3ffb021-53ea-4984-83b9-728f509c4fca)

**Tagline**: Delivering infinite product insights from every dimension...

Inqube AI is an advanced competitor analysis tool designed to help businesses, startups, and entrepreneurs gain deep insights into their competitors' products and services. Leveraging AI and machine learning, the tool automates the process of gathering, analyzing, and visualizing data from multiple sources, including e-commerce platforms, websites, and YouTube. It provides actionable insights to help users make informed decisions, identify market opportunities, and refine their strategies.

---

## **How Inqube AI Works**

Inqube AI, powered by the IBM Granite Model, is a competitor analysis tool that provides deep insights into products and services. Here’s a step-by-step breakdown of how it works:

### **Step 1: User Input**
Users provide the following details:
1. **Product Name**: The name of the product or service to analyze.
2. **Country Code**: A two-letter code (e.g., US, IN) for region-specific results.
3. **Search Parameters**:
   - Number of search results to analyze.
   - Number of YouTube videos to analyze.
   - Number of YouTube comments to analyze per video.
4. **Type**: Select ‘Product’ or ‘Service’ for accurate analysis.

### **Step 2: Web Search**
The **Serper tool** searches the web for product/service details such as:
- Product name.
- Price.
- Link to the product page.
- Snippet description.
- Seller information.

This provides a list of competitor products or services for further analysis.

### **Step 3: Web Scraping**
The product links obtained from Serper are processed by **Crew AI’s ScrapeWebsiteTool**. This tool:
- Scrapes detailed information from the product’s webpage.
- Extracts key details like product descriptions, features, pricing, and customer reviews.

### **Step 4: YouTube Analysis**
The product name is passed to the **YouTube API** to:
1. Find related videos for the product/service.
2. Extract video transcripts using the `youtube_transcript_api` Python library.
3. Collect comments from the videos for sentiment analysis.

This step helps understand customer sentiment and trends through video content and user feedback.

### **Step 5: AI Analysis**
All collected data—video transcripts, scraped content, and product details—are passed to the **IBM Granite Model** (`granite-3-8b-instruct`). The model generates a detailed analysis, including:

Get your granite access token by passing your api in iam.py

1. **SWOT Analysis**:
   - Strengths, Weaknesses, Opportunities, and Threats.
2. **Pros and Cons**:
   - Key advantages and disadvantages of the product/service.
3. **Sentiment Analysis**:
   - Insights from YouTube comments (positive vs. negative).
4. **Price and Rating Analysis**:
   - Competitive pricing and customer satisfaction metrics.

This process repeats for each search result specified by the user.

### **Step 6: Final Output**
The insights from all analyzed items are consolidated using the IBM Granite Model. The final output includes:
1. **Visualizations**:
   - **Bar Graphs**: Compare price, ratings, and offers across competitors.
   - **Pie Charts**: Display sentiment distribution (positive vs. negative comments).
2. **Startup Recommendations**:
   - Suggestions for launching a new product/service, including:
     - Unique features to add.
     - Pricing strategies.
     - Marketing tips.
     - Potential risks and solutions.

---

## **Key Features**
1. **Competitor Analysis**:
   - Analyze competitor products/services in detail.
2. **YouTube Insights**:
   - Extract video transcripts and comments for sentiment analysis.
3. **AI-Powered Insights**:
   - Generate SWOT analysis, pros/cons, and actionable recommendations.
4. **Interactive Visualizations**:
   - Bar graphs and pie charts for easy comparison and understanding.
5. **Customizable Inputs**:
   - Adjust search parameters for tailored analysis.

---

## **Why Inqube AI?**
Inqube AI combines **web scraping**, **YouTube analysis**, and **AI-powered insights** to deliver a comprehensive competitor analysis. Whether you’re launching a new product, refining your strategy, or exploring the market, Inqube AI provides actionable insights to help you stay ahead.

---

## **Setup**

### **Prerequisites**
- Python 3.8 or higher.
- Streamlit.
- Plotly.
- Requests.
- YouTube Transcript API.

import streamlit as st
import requests
import json
from youtube_transcript_api import YouTubeTranscriptApi
import re
import plotly.express as px
import pandas as pd

# Assuming the helper functions are imported from a separate module
from helpers import send_to_granite, search_service_items, search_shopping_items, scrape_website_content, search_youtube_videos, fetch_youtube_transcript, fetch_youtube_comments, extract_details



def analyze_with_granite_llm(content,source,delivery, imageUrl,offers, snippet, product_name, price, rating, rating_count, youtube_transcript=None, youtube_comments=None):
    # Craft a structured prompt for the Granite LLM
    prompt = f"""
    Analyze the following product information and provide a structured summary:

    Product Name: {product_name}
    Price: {price}
    Rating: {rating}
    Number of Reviews: {rating_count}
    About: {snippet}

    Scraped Content:
    {content}

    YouTube Video Transcript:
    {youtube_transcript if youtube_transcript else "No transcript available."}

    YouTube Video Comments:
    {youtube_comments if youtube_comments else "No comments available."}

    Provide the analysis in the following structured format (if some invormation is unavailable, fill them with "Not Available"):
    1. **Product Overview**: A brief description of the product.
    2. **Key Features**: List the most important features of the product.
    3. **Pros**: Highlight the advantages of the product based on reviews and content.
    4. **Cons**: Mention any drawbacks or complaints about the product.
    5. **Price Analysis**: Comment on whether the price is competitive.
    6. **Rating Analysis**: Analyze the rating and number of reviews.
    7. **YouTube Insights**: Summarize insights from the YouTube video transcript and comments.
    8. **Additional Details**: Any other relevant information about the product.
    9. **Strengths (Best features)**: Strengths (Best features) for swot analysis.
    10. **Weaknesses (Negative feedback)**: Weaknesses (Negative feedback) for swot analysis.
    11. **Opportunities (Unexplored features)** Opportunities (Unexplored features) for swot analysis.
    12. **Threats (Strong competitors): Threats (Strong competitors) for swot analysis.
    13. **Seller Name**: Name of the seller.
    14. **Negative Comments**: number of negative comments from both YouTube Video Comments Above or reviews from scrapped content.
    15. **Positive Comments**: number of positive comments from both YouTube Video Comments Above or reviews from scrapped content.
    """
    
    #print("prompt: ")
    #print(prompt)
    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    body = {
        "input": prompt,  # Use the structured prompt as input
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 1500,
            "min_new_tokens": 0,
            "repetition_penalty": 1
        },
        "model_id": "ibm/granite-3-8b-instruct",
        "project_id": "58e29d0a-b08d-4b3a-9e10-d41d5adb23fd",
        "moderations": {
            "hap": {
                "input": {
                    "enabled": False,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": False
                    }
                },
                "output": {
                    "enabled": False,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": False
                    }
                }
            },
            "pii": {
                "input": {
                    "enabled": False,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": False
                    }
                },
                "output": {
                    "enabled": False,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": False
                    }
                }
            }
        }
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {granite_key}" # Replace with your IBM Cloud API key
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()
    #print("response data")
    #print(data)
    if data.get("results"):
        generated_text = data["results"][0].get("generated_text", "No analysis available.")
        print("generated_text: " + generated_text)
    else:
        generated_text = "No analysis available."
    
    return generated_text


# Streamlit UI setup
st.title("Incube Intelligence")
st.divider()
st.write("Inqube AI empowers you to explore existing services and products, delivering a complete analysis to fuel your startup, competitor analysis, or any other business or personal applications. By leveraging advanced AI, this tool provides deep insights into competitor offerings, customer sentiment, and market trends, helping you make data-driven decisions and stay ahead in your industry. Whether you're launching a new product, refining your strategy, or simply exploring the market, Inqube AI is your ultimate companion for actionable insights.")

# Sidebar for user inputs
with st.sidebar:

    st.title("Inqube AI")
    st.image("logo.png", width=200)  # Ensure "logo.png" is in the same directory
    st.divider()
    st.write("Delivering infinite product insights from every dimension...")
    st.divider()


    granite_key = st.text_input("Enter your IBM Granite Key", type="password")
    product_name = st.text_input("Enter the product name to analyze")
    country_code = st.text_input("Enter your two-letter country code")
    type = st.checkbox("Is it a service? (Leave unchecked for product)")
    number_of_search = st.slider("Number of search results to analyze", 1, 10, 3)
    number_of_video_search = st.slider("Number of YouTube videos to analyze per product", 1, 5, 2)
    comment_count = st.slider("Number of YouTube comments to analyze per video", 1, 20, 2)



    st.write("### Inqube Bot")
    messages = st.container(height=300)

    # Chatbot logic
    if prompt := st.chat_input("Say something"):
        # User input
        messages.chat_message("user").write(prompt)

        # Bot responses
        if prompt.lower() == "how to use":
            messages.chat_message("assistant").write(
                "To use this project:\n"
                "1. Enter your Granite Key, product name, and country code.\n"
                "2. Choose whether the product is a service or not.\n"
                "3. Adjust the sliders for search results, YouTube videos, and comments.\n"
                "4. Click 'Analyze' to get insights."
            )
        elif prompt.lower() == "what to enter":
            messages.chat_message("assistant").write(
                "You need to enter:\n"
                "- **Granite Key**: Your API key for analysis.\n"
                "- **Product Name**: The name of the product or service to analyze.\n"
                "- **Country Code**: A two-letter code (e.g., US, IN).\n"
                "- **Type**: Check if it's a service; leave unchecked for products.\n"
                "- **Sliders**: Adjust the number of search results, YouTube videos, and comments."
            )
        elif prompt.lower() == "about":
            messages.chat_message("assistant").write(
                "**About Inqube AI**:\n"
                "Inqube AI is a competitor analysis tool that provides deep insights into products and services. "
                "It uses AI to analyze data from multiple sources, including e-commerce platforms and YouTube, "
                "to help businesses make data-driven decisions."
            )
        elif prompt.lower() == "features":
            messages.chat_message("assistant").write(
                "**Features of Inqube AI**:\n"
                "- Competitor product analysis.\n"
                "- YouTube video and comment insights.\n"
                "- AI-powered SWOT analysis.\n"
                "- Interactive visualizations (bar charts, pie charts).\n"
                "- Startup recommendations based on competitor analysis."
            )
        elif prompt.lower() == "hi":
            messages.chat_message("assistant").write(
                "Hello! I am Inqube AI.\n"
                "**Tagline**: Delivering infinite product insights from every dimension..."
            )
        else:
            messages.chat_message("assistant").write(
                "Available commands:\n"
                "- **how to use**: Instructions on how to use the project.\n"
                "- **what to enter**: Details of input parameters.\n"
                "- **about**: Information about the project.\n"
                "- **features**: Features of the project.\n"
                "- **hi**: Greet the bot and see the tagline."
            )

# Function to clean and extract numeric values
def clean_numeric(value):
    if isinstance(value, str):
        # Remove non-numeric characters like $, +, etc.
        cleaned_value = re.sub(r"[^0-9.]", "", value)
        return float(cleaned_value) if cleaned_value else 0
    return value

# Function to extract numeric values from comments
def extract_comment_count(comments):
    if isinstance(comments, int):
        return comments  # Already extracted as an integer in extract_details
    elif isinstance(comments, str):
        numbers = re.findall(r"\d+", comments)
        return int(numbers[0]) if numbers else 0
    return 0


# Main page logic
if st.button('Analyze'):
    if not granite_key or not product_name or not country_code:
        st.error("Please fill in the Granite Key, Product Name, and Country Code.")
    else:
        with st.spinner('Analyzing...'):
            product_analysis_results = {}
            type = "service" if type else "product"
            
            if type == "product":
                shopping_results = search_shopping_items(product_name, country_code)
            else:
                shopping_results = search_service_items(product_name, country_code)

            # Prepare data for plotting
            plot_data = {
                "Title": [],
                "Price": [],
                "Rating": [],
                "Rating Count": [],
                "Offers": []
            }

            # Global counts for positive and negative comments
            global_positive_count = 0
            global_negative_count = 0
            st.subheader("Analyzed Products:")
            st.divider()

            for result in shopping_results[:number_of_search]:
                try:
                    scraped_content = scrape_website_content(result['link'])
                    youtube_videos = search_youtube_videos(result['title'], number_of_video_search)
                    all_transcripts = []
                    all_comments = []
                    links = []
                    for video in youtube_videos[:number_of_video_search]:
                        video_id = video['id']['videoId']
                        links.append(f"https://www.youtube.com/watch?v={video_id}")
                        transcript = fetch_youtube_transcript(video_id)
                        comments = fetch_youtube_comments(video_id, comment_count)
                        if transcript:
                            all_transcripts.append(transcript)
                        if comments:
                            all_comments.extend(comments)
                    
                    analysis = analyze_with_granite_llm(
                        content=scraped_content,
                        source=result.get('source', 'N/A'),
                        snippet=result.get('snippet', 'N/A'),
                        product_name=result['title'],
                        price=result.get('price', 'N/A'),
                        rating=result.get('rating', 'N/A'),
                        delivery=result.get('delivery', 'N/A'),
                        imageUrl=result.get('imageUrl', 'N/A'),
                        offers=result.get('offers', 'N/A'),
                        rating_count=result.get('ratingCount', 'N/A'),
                        youtube_transcript=" ".join(all_transcripts),
                        youtube_comments=all_comments
                    )
                    product_analysis_results[result['title']] = extract_details(analysis)
                    print(product_analysis_results)
                    # Add data for plotting
                    plot_data["Title"].append(result['title'])
                    plot_data["Price"].append(clean_numeric(result.get('price', '0')))
                    plot_data["Rating"].append(clean_numeric(result.get('rating', '0')))
                    plot_data["Rating Count"].append(clean_numeric(result.get('ratingCount', '0')))
                    plot_data["Offers"].append(clean_numeric(result.get('offers', '0')))

                    # Display details for each product in a grid format
                    with st.expander(f"Details for {result['title']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(result.get('imageUrl', 'N/A'), caption="Product Image", width=200)
                            st.write(f"**Source:** {result.get('source', 'N/A')}")
                            st.write(f"**Price:** {result.get('price', 'N/A')}")
                            st.write(f"**Rating:** {result.get('rating', 'N/A')}")
                            st.write(f"**Rating Count:** {result.get('ratingCount', 'N/A')}")
                            st.write(f"**Link:** {result.get('link', 'N/A')}")
                        with col2:
                            st.write(f"**Delivery:** {result.get('delivery', 'N/A')}")
                            st.write(f"**Offers:** {result.get('offers', 'N/A')}")
                            st.write(f"**Snippet:** {result.get('snippet', 'N/A')}")
                            st.write(f"**YouTube Links:** {', '.join(links)}")
                            #st.write(f"**Scraped Content:** {scraped_content[:500]}...")  # Display first 500 chars


                        # Display extracted details
                        details = product_analysis_results[result['title']]
                        st.write("### Extracted Analysis Details")
                        st.write(f"**Product Overview:** {details.get('Product Overview', 'N/A')}")
                        st.write(f"**Key Features:** {', '.join(details.get('Key Features', [])) if details.get('Key Features') else 'N/A'}")
                        st.write(f"**Price Analysis:** {details.get('Price Analysis', 'N/A')}")
                        st.write(f"**Rating Analysis:** {details.get('Rating Analysis', 'N/A')}")
                        st.write(f"**YouTube Insights:** {', '.join(details.get('YouTube Insights', [])) if details.get('YouTube Insights') else 'N/A'}")
                        st.write(f"**Additional Details:** {', '.join(details.get('Additional Details', [])) if details.get('Additional Details') else 'N/A'}")
                        st.write(f"**Seller Name:** {details.get('Seller Name', 'N/A')}")

                        # Add a divider
                        st.divider()

                        # Display SWOT Analysis in a 2x2 grid
                        st.write("### SWOT Analysis")
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**Strengths**")
                            if details.get("Strengths"):
                                st.write(", ".join(details["Strengths"]))
                            else:
                                st.write("N/A")

                            st.write("**Weaknesses**")
                            if details.get("Weaknesses"):
                                st.write(", ".join(details["Weaknesses"]))
                            else:
                                st.write("N/A")

                        with col2:
                            st.write("**Opportunities**")
                            if details.get("Opportunities"):
                                st.write(", ".join(details["Opportunities"]))
                            else:
                                st.write("N/A")

                            st.write("**Threats**")
                            if details.get("Threats"):
                                st.write(details["Threats"])
                            else:
                                st.write("N/A")

                        # Add a divider
                        st.divider()

                        # Display Pros and Cons side by side in a table
                        st.write("### Pros and Cons")
                        pros_cons_col1, pros_cons_col2 = st.columns(2)

                        with pros_cons_col1:
                            st.write("**Pros**")
                            if details.get("Pros"):
                                st.write(", ".join(details["Pros"]))
                            else:
                                st.write("N/A")

                        with pros_cons_col2:
                            st.write("**Cons**")
                            if details.get("Cons"):
                                st.write(", ".join(details["Cons"]))
                            else:
                                st.write("N/A")

                        # Add a divider
                        st.divider()


                        # Pie chart for positive and negative comments
                        positive_comments = details.get("Positive Comments", "Not available")
                        negative_comments = details.get("Negative Comments", "Not available")

                        if positive_comments != "Not available" and negative_comments != "Not available":
                            positive_count = extract_comment_count(positive_comments)
                            negative_count = extract_comment_count(negative_comments)

                            # Update global counts
                            global_positive_count += positive_count
                            global_negative_count += negative_count

                            # Pie chart for this item
                            pie_data = {
                                "Type": ["Positive Comments", "Negative Comments"],
                                "Count": [positive_count, negative_count]
                            }
                            df_pie = pd.DataFrame(pie_data)
                            fig_pie = px.pie(df_pie, values="Count", names="Type", title=f"Sentiment Analysis for {result['title']}",
                                             color="Type",
                 color_discrete_map={"Positive Comments": "#153969", "Negative Comments": "#c0cfe1"},
                 category_orders={"Type": ["Positive Comments", "Negative Comments"]})
                            st.plotly_chart(fig_pie)

                except Exception as e:
                    st.error(f"Error processing {result['link']}: {e}")

            # Global pie chart for all items
            if global_positive_count > 0 or global_negative_count > 0:
                global_pie_data = {
                    "Type": ["Positive Comments", "Negative Comments"],
                    "Count": [global_positive_count, global_negative_count]
                }
                df_global_pie = pd.DataFrame(global_pie_data)
                fig_global_pie = px.pie(df_global_pie, values="Count", names="Type", title="Global Sentiment Analysis",
                                        color="Type",
                 color_discrete_map={"Positive Comments": "#153969", "Negative Comments": "#c0cfe1"},
                 category_orders={"Type": ["Positive Comments", "Negative Comments"]})
                st.plotly_chart(fig_global_pie)

            # Bar graphs for Price, Rating, Rating Count, and Offers
            df_bar = pd.DataFrame(plot_data)
            st.subheader("Price Comparison")
            fig_price = px.bar(df_bar, x="Title", y="Price", text="Price", title="Price Comparison",color_discrete_sequence=["#153969"])
            fig_price.update_traces(textposition='outside', hoverinfo="x+y")
            fig_price.update_xaxes(showticklabels=False)  # Hide x-axis labels
            st.plotly_chart(fig_price)

            st.subheader("Rating Comparison")
            fig_rating = px.bar(df_bar, x="Title", y="Rating", text="Rating", title="Rating Comparison",color_discrete_sequence=["#153969"])
            fig_rating.update_traces(textposition='outside', hoverinfo="x+y")
            fig_rating.update_xaxes(showticklabels=False)  # Hide x-axis labels
            st.plotly_chart(fig_rating)

            st.subheader("Rating Count Comparison")
            fig_rating_count = px.bar(df_bar, x="Title", y="Rating Count", text="Rating Count", title="Rating Count Comparison",color_discrete_sequence=["#153969"])
            fig_rating_count.update_traces(textposition='outside', hoverinfo="x+y")
            fig_rating_count.update_xaxes(showticklabels=False)  # Hide x-axis labels
            st.plotly_chart(fig_rating_count)

            st.subheader("Offers Comparison")
            fig_offers = px.bar(df_bar, x="Title", y="Offers", text="Offers", title="Offers Comparison",color_discrete_sequence=["#153969"])
            fig_offers.update_traces(textposition='outside', hoverinfo="x+y")
            fig_offers.update_xaxes(showticklabels=False)  # Hide x-axis labels
            st.plotly_chart(fig_offers)

            # Final analysis
            analysis_json = json.dumps(product_analysis_results, indent=4)
            prompt = f"""
            These are the existing products (competitors) and their analysis:
            {analysis_json}

            I am going to build a startup based on this product. Provide details in the following format:

            My Startup Name and Tagline Suggestion:
            Target Audience:
            Pricing Strategy (suggest average price too according to the products from the analysis):
            Detailed Unique Features to Add (which are not in existing products from the analysis):
            All the Features/Improvements that can be made in existing products from the analysis:
            Customer Pain Points & Solutions (According the the review analysis of products):
            Advertisement and Marketing Tips:
            Highlight potential risks associated with launching this startup:
            """
            final_analysis = send_to_granite(prompt, granite_key)
            st.info("Analysis Complete!")
            st.balloons()
            st.subheader("Startup Analysis Report:")
            st.divider()
            st.write(final_analysis)
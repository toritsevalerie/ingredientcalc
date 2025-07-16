# import openai
# import PyPDF2
# import io
# import requests
# from bs4 import BeautifulSoup
# import streamlit as st

# # --- Set default page if no page has been selected yet ---
# # This helps Streamlit remember which "tab" the user clicked
# if "page" not in st.session_state:
#     st.session_state.page = None

# # --- App layout setup ---
# # Sets the page title (shown in browser tab) and makes the layout wide
# st.set_page_config(page_title="Regulatory Tools", layout="wide")

# # --- Header text at the top of the app ---
# st.title("Simple tools for regulatory teams.")
# st.write("")

# # --- Create 3 columns for main navigation buttons ---
# col1, col2, col3 = st.columns([1, 1, 1])

# # Column 1: User clicks this to go to the Ingredient Calculator tool
# with col1:
#     if st.button("Ingredient Calculator"):
#         st.session_state.page = "calculator"

# # Column 2: User clicks this to go to the PDF rule finder + AI chat tool
# with col2:
#     if st.button("Regulatory Rule Explainer"):
#         st.session_state.page = "rule_finder"

# # Column 3: User clicks this to go to the scraper/search tool (we’ll build this next)
# with col3:
#     if st.button("🔍 Search Online for Regulatory Rules"):
#         st.session_state.page = "scraper"

# # --- INGREDIENT CALCULATOR TOOL ---
# if st.session_state.page == "calculator":
#     st.title("🧪 Ingredient Calculator")
#     st.write("Upload a CSV with lab results (nutrients per 100g), and we’ll help convert them to serving sizes.")

#     uploaded_file = st.file_uploader("Upload your lab results CSV or PDF", type=["csv", "pdf"])

#     if uploaded_file is not None:
#         import pandas as pd

#     if uploaded_file.name.endswith(".csv"):
#         df = pd.read_csv(uploaded_file)
#         st.write("Here’s your uploaded data:")
#         st.dataframe(df)

#     elif uploaded_file.name.endswith(".pdf"):
#         # Extract text from PDF
#         reader = PyPDF2.PdfReader(uploaded_file)
#         text = ""
#         for page in reader.pages:
#             text += page.extract_text()

#         # Simple table parsing (assumes format: Nutrient | Amount per 100g | Unit)
#         lines = text.split("\n")
#         rows = []
#         for line in lines:
#             parts = line.split()
#             if len(parts) >= 3:
#                 unit = parts[-1]
#                 try:
#                     amount = float(parts[-2])
#                     nutrient = " ".join(parts[:-2])
#                     rows.append([nutrient, amount, unit])
#                 except ValueError:
#                     continue

#         df = pd.DataFrame(rows, columns=["Nutrient", "Amount per 100g", "Unit"])
#         st.write("Here’s your extracted PDF data:")
#         st.dataframe(df)

#         # Let user enter a serving size (e.g. 150g)
#     serving_size = st.number_input("Enter serving size in grams (e.g. 150g)", min_value=1.0, step=1.0)

#     if serving_size:
#             st.write(f"Nutrient values per {serving_size}g serving:")

#             # Scale the values from 100g to the serving size
#             df_converted = df.copy()
#             df_converted["Amount per Serving"] = (df["Amount per 100g"] * serving_size) / 100
#             df_converted = df_converted[["Nutrient", "Amount per Serving", "Unit"]]

#             # Convert units like IU → µg for specific vitamins
#             def convert_iu_to_mcg(row):
#                 if row["Unit"] == "IU":
#                     if "Vitamin A" in row["Nutrient"]:
#                         return row["Amount per Serving"] * 0.3, "µg"
#                     elif "Vitamin D" in row["Nutrient"]:
#                         return row["Amount per Serving"] * 0.025, "µg"
#                     elif "Vitamin E" in row["Nutrient"]:
#                         return row["Amount per Serving"] * 0.67, "µg"
#                 return row["Amount per Serving"], row["Unit"]

#             df_converted[["Amount per Serving", "Unit"]] = df_converted.apply(convert_iu_to_mcg, axis=1, result_type="expand")

#             # Show the converted table
#             st.dataframe(df_converted)

#             # Let user download the new table as a CSV
#             csv = df_converted.to_csv(index=False)
#             b64 = csv.encode()
#             st.download_button(
#                 label="📥 Download Converted Table as CSV",
#                 data=b64,
#                 file_name="converted_nutrition_data.csv",
#                 mime="text/csv"
#             )


# import PyPDF2
import io
import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd

# --- Set default page if no page has been selected yet ---
if "page" not in st.session_state:
    st.session_state.page = None

# --- App layout setup ---
st.set_page_config(page_title="Regulatory Tools", layout="wide")

# --- Header text at the top of the app ---
st.title("Simple tools for regulatory teams.")
st.write("")

# --- Create 3 columns for main navigation buttons ---
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("Ingredient Calculator"):
        st.session_state.page = "calculator"

with col2:
    if st.button("Regulatory Rule Explainer"):
        st.session_state.page = "rule_finder"

with col3:
    if st.button("🔍 Search Online for Regulatory Rules"):
        st.session_state.page = "scraper"

# --- INGREDIENT CALCULATOR TOOL ---
if st.session_state.page == "calculator":
    st.title("🧪 Ingredient Calculator")
    st.write("Upload a CSV with lab results (nutrients per 100g), and we’ll help convert them to serving sizes.")

    uploaded_file = st.file_uploader("Upload your lab results CSV or PDF", type=["csv", "pdf"])
    df = None

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            st.write("Here’s your uploaded data:")
            st.dataframe(df)

        elif uploaded_file.name.endswith(".pdf"):
            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            # Simple table parsing (Nutrient | Amount per 100g | Unit)
            lines = text.split("\n")
            rows = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    unit = parts[-1]
                    try:
                        amount = float(parts[-2])
                        nutrient = " ".join(parts[:-2])
                        rows.append([nutrient, amount, unit])
                    except ValueError:
                        continue

            df = pd.DataFrame(rows, columns=["Nutrient", "Amount per 100g", "Unit"])
            st.write("Here’s your extracted PDF data:")
            st.dataframe(df)

    # --- Nutrition Calculation ---
    if df is not None:
        serving_size = st.number_input("Enter serving size in grams (e.g. 150g)", min_value=1.0, step=1.0)

        if serving_size:
            st.write(f"Nutrient values per {serving_size}g serving:")

            df_converted = df.copy()
            df_converted["Amount per Serving"] = (df["Amount per 100g"].astype(float) * serving_size) / 100
            df_converted = df_converted[["Nutrient", "Amount per Serving", "Unit"]]

            def convert_iu_to_mcg(row):
                if row["Unit"] == "IU":
                    if "Vitamin A" in row["Nutrient"]:
                        return row["Amount per Serving"] * 0.3, "µg"
                    elif "Vitamin D" in row["Nutrient"]:
                        return row["Amount per Serving"] * 0.025, "µg"
                    elif "Vitamin E" in row["Nutrient"]:
                        return row["Amount per Serving"] * 0.67, "µg"
                return row["Amount per Serving"], row["Unit"]

            df_converted[["Amount per Serving", "Unit"]] = df_converted.apply(convert_iu_to_mcg, axis=1, result_type="expand")

            st.dataframe(df_converted)

            csv = df_converted.to_csv(index=False).encode()
            st.download_button(
                label="📥 Download Converted Table as CSV",
                data=csv,
                file_name="converted_nutrition_data.csv",
                mime="text/csv"
            )


# # --- PDF RULE FINDER + AI EXPLAINER TOOL ---
# if st.session_state.page == "rule_finder":
#     st.title("📄 Regulations & Rule Explainer")

#     # Set up storage space in memory to hold uploaded PDFs
#     if "reg_docs" not in st.session_state:
#         st.session_state.reg_docs = {}

#     # Let user upload a PDF (or txt) regulation document
#     uploaded_file = st.file_uploader("Upload a regulatory document", type=["txt", "pdf"])

#     if uploaded_file:
#         # Optional: Let user rename the file
#         default_name = uploaded_file.name
#         custom_name = st.text_input("Optional: Give this file a name", value=default_name)

#         # Save the file contents into session storage (can be retrieved by name later)
#         st.session_state.reg_docs[custom_name] = uploaded_file.getvalue()
#         st.success(f"✅ '{custom_name}' saved successfully!")

#     # Display uploaded files and allow AI chat on each one
#     if st.session_state.reg_docs:
#         st.subheader("📁 Uploaded Files")

#         for name, file in st.session_state.reg_docs.items():
#             st.markdown(f"📄 **{name}**")

#             # Let user chat with AI about this specific file
#             st.subheader(f"🤖 Ask AI About '{name}'")

#             # Keep previous Q&A stored for this file
#             if "chat_history" not in st.session_state:
#                 st.session_state.chat_history = {}
#             if name not in st.session_state.chat_history:
#                 st.session_state.chat_history[name] = []

#             # Show previous questions and answers for this file
#             for q, a in reversed(st.session_state.chat_history[name]):
#                 st.markdown(f"**You:** {q}")
#                 st.markdown(f"**AI:** {a}")
#                 st.markdown("---")

#             # Input for a new question
#             new_question = st.text_input("Ask a question", key=f"q_{name}")
#             if st.button("Send", key=f"ask_btn_{name}") and new_question:
#                 with st.spinner("Thinking..."):
#                     # Extract all text from the PDF
#                     pdf_reader = PyPDF2.PdfReader(io.BytesIO(file))
#                     full_text = ""
#                     for page in pdf_reader.pages:
#                         full_text += page.extract_text() or ""
#                     trimmed_text = full_text[:3000]  # Limit text length to keep token use low

#                     # Send to OpenAI for answer
#                     client = openai.OpenAI()
#                     response = client.chat.completions.create(
#                         model="gpt-4o",
#                         messages=[
#                             {"role": "system", "content": "You're a helpful regulatory assistant. Answer in detail based on the document."},
#                             {"role": "user", "content": f"Document:\n{trimmed_text}"},
#                             {"role": "user", "content": f"Question: {new_question}"}
#                         ],
#                         temperature=0.3,
#                         max_tokens=800  # You changed this to 800 to get longer answers
#                     )

#                     answer = response.choices[0].message.content.strip()
#                     st.session_state.chat_history[name].append((new_question, answer))
#                     st.experimental_rerun()

#             # Let user download the original file
#             st.download_button(
#                 label="📥 Download/View",
#                 data=file,
#                 file_name=name,
#                 mime="application/pdf"
#             )
# # --- CUSTOM REGULATION SCRAPER TOOL ---
# if st.session_state.page == "scraper":
#     st.title("🌐 Search for Regulatory Rules Online")

#     st.markdown("Use this tool to search official websites (e.g., FDA, Health Canada) for regulatory rules and save them to your doc library.")

#     # Step 1: Let user type a search query
#     query = st.text_input("Search regulatory rule (e.g., 'labeling for infant formula')")

#     # Step 2: Only run search logic if user clicks AND query is not empty
#     if st.button("🔎 Search Now") and query.strip():
#         with st.spinner("Searching..."):
#             # Build a search query using DuckDuckGo
#             search_url = f"https://html.duckduckgo.com/html/?q=site:fda.gov+{query}"

#             # Send a GET request to the search engine
#             headers = {"User-Agent": "Mozilla/5.0"}
#             response = requests.get(search_url, headers=headers)

#             # Parse the HTML response using BeautifulSoup
#             soup = BeautifulSoup(response.text, "html.parser")

#             # Find search result links (DuckDuckGo wraps them in a .result__a class)
#             results = soup.find_all("a", class_="result__a")

#             if not results:
#                 st.error("No results found or scraping failed.")
#             else:
#                 st.success("✅ Found some results. These are real links from FDA.gov:")

#                 # Show the top 5 results
#                 for result in results[:5]:
#                     title = result.text
#                     link = result["href"]
#                     st.markdown(f"🔗 [{title}]({link})")
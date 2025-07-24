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


import PyPDF2
import io
import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import PyPDF2
# import pytesseract
from PIL import Image
import io

# --- Set default page if no page has been selected yet ---
if "page" not in st.session_state:
    st.session_state.page = None

# --- App layout setup ---
st.set_page_config(page_title="Regulatory Tools", layout="wide")

# --- Header text at the top of the app ---
st.title("Simple tools for regulatory teams.")
st.write("")

# --- Create 3 columns for main navigation buttons ---
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if st.button("Ingredient Calculator"):
        st.session_state.page = "calculator"

with col2:
    if st.button("Compliance Review Assistant"):
        st.session_state.page = "compliance_review_tool"

with col3:
    if st.button("Claims Repository/Dashboard"):
        st.session_state.page = "claim_repository"

with col4: 
    if st.button("Regulatory Search Assistant"):
        st.session_state.page = "search_assistant"

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


# Complaince Assistant Tool 
# Help regulatory folks quickly review ingredients, artwork, and claims to catch anything non-compliant

if st.session_state.page == "compliance_review_tool":
    st.title('👩🏽‍💻 Compliance Review Assistant')
    st.write('Upload your files or paste content to instantly review ingredients, labels, artwork and claims for potential compliance issues')
    st.caption("⚠️ Image/Artwork Uploads not yet supported in this version.")

    # store uploaded file as a variable and let pdf, images etc be able to be uploaded 
    uploaded_file = st.file_uploader("Upload or drag and drop a file (like a spec sheet, label, or claims document), or paste your ingredient list or marketing claims below", type=["pdf", "jpeg", "jpg", "png"])
    # store text submissison input field 
    uploaded_text = st.text_area('Paste your ingredient list or marketing claims here', placeholder=" e.g water, glycerin etc")

    # detect if anything was submitted 
    if uploaded_file or uploaded_text.strip():
        with st.spinner('give me a second...'):
            import time
            time.sleep(1)

        st.subheader('Which country are you reviewing this for?')
        country = st.selectbox(
            "Choose a Country",
            ["-- Select a Country --", "Canada", "United States", "United Kingdom", "Australia", "New Zealand"]
        )
        
        if country != "-- Select a Country --":
            st.subheader("What would you like to focus on?")
            review_option = st.radio(
                "Do you want to review everything, or focus on something specific?",
                ["Review everything", "Focus on a specific section"]
        )
            specific_focus = ""
            if review_option == "Focus on a specific section":
                st.text_input("What specific section would you like to focus on?", placeholder=("e.g is the vegan claim okay?"))

        if st.button("Run Compliance Check"):
            with st.spinner("Checking against Health Canada and CFIA..."):
                time.sleep(2)

            # Pretend output (mock results)
            st.success("✅ Review complete")

            st.markdown("### 📝 Findings")
            st.markdown(f"""
            **Claim Reviewed:** `{specific_focus or 'All available text'}`
            
            **Result:** ⚠️ *The claim 'vegan' is not explicitly defined under Canadian food labeling regulations.*
            
            However, per [CFIA Guidance on Plant-Based Foods](https://inspection.canada.ca), such claims may be used if **not misleading** and compliant with ingredient definitions.

            **Next Steps:** Ensure no animal-derived ingredients are present. Consider including a clarifying statement like "suitable for vegans".
            """)

            # Internal note section
            internal_note = st.text_area("📌 Add internal note for team (optional)", placeholder="e.g. Reviewed by Sam. Need to confirm if enzyme source is animal-free.")

            # Status dropdown
            status = st.selectbox("Set review status", ["In Progress", "Reviewed", "Needs Follow-up"])
            st.write(f"🗂️ Status saved as: **{status}**")

if st.session_state.page == "claim_repository":
    st.title("🗃️ Claim Repository")
    st.write("This is a **mockup interface** to demonstrate how regulatory teams might browse and manage previously reviewed claims.")

    st.caption("⚠️ This is a static prototype for demo purposes only. Features like file uploads, editing, and downloads are not functional yet. More capabilities will be added.")

    # ---------------------------
    # Instructions
    st.subheader("🔍 What You Can Do Here")
    st.markdown("""
    - View a searchable list of previously reviewed claims  
    - Filter by category, product, or approval status  
    - Click on a claim to see its full details  
    """)

    st.info("This tool is designed to help regulatory teams avoid duplicate reviews, find substantiation, and reuse already-approved language.")

    # ---------------------------
    # Sample claim data (mock)
    sample_data = pd.DataFrame({
        "Claim Text": ["Supports immune function", "Boosts energy levels", "Aids digestion"],
        "Product": ["Nestlé Protein Shake", "Vital Energy Bar", "Gut Health Gummies"],
        "Category": ["Immunity", "Energy", "Digestion"],
        "Status": ["Approved", "In Review", "Rejected"],
        "Review Date": ["2024-10-15", "2025-02-01", "2025-03-12"],
    })

    # ---------------------------
    # Search & Filter Controls
    st.subheader("🔎 Search & Filter")

    search_term = st.text_input("Search claims by keyword", "")
    category_filter = st.selectbox("Filter by Category", ["All"] + sorted(sample_data["Category"].unique()))
    product_filter = st.selectbox("Filter by Product", ["All"] + sorted(sample_data["Product"].unique()))
    status_filter = st.selectbox("Filter by Approval Status", ["All"] + sorted(sample_data["Status"].unique()))

    # Apply filters
    filtered_data = sample_data.copy()

    if search_term:
        filtered_data = filtered_data[filtered_data["Claim Text"].str.contains(search_term, case=False)]

    if category_filter != "All":
        filtered_data = filtered_data[filtered_data["Category"] == category_filter]

    if product_filter != "All":
        filtered_data = filtered_data[filtered_data["Product"] == product_filter]

    if status_filter != "All":
        filtered_data = filtered_data[filtered_data["Status"] == status_filter]

    # ---------------------------
    # Table View
    st.subheader("📊 Table View")
    st.dataframe(filtered_data)

    # ---------------------------
    # Expander View
    st.subheader("🎴 Reviewed Claims")

    if filtered_data.empty:
        st.warning("No claims found with the selected filters or search term.")
    else:
        for index, row in filtered_data.iterrows():
            with st.expander(f"{row['Claim Text']} – {row['Product']}"):
                st.markdown(f"""
                **🧠 Category:** {row['Category']}  
                **✅ Status:** {row['Status']}  
                **📅 Reviewed On:** {row['Review Date']}  
                **🔗 Substantiation File:** [View PDF](#)  
                **👩‍⚖️ Reviewed By:** M.T.  
                **🏷️ Tags:** adult, protein, Canada  
                **📚 Source Link:** [CFIA Regulation](#)
                """)

# #Claim Repository Tool 

# # If this page is selected, display the Claim Repository prototype
# if st.session_state.page == "claim_repository":
#     st.title("🗃️ Claim Repository")
#     st.write("This is a **mockup interface** to demonstrate how regulatory teams might browse and manage previously reviewed claims.")

#     st.caption("⚠️ This is a static prototype for demo purposes only. Features like file uploads, editing, and downloads are not functional yet. More capabilities will be added.")

#     # Instructions
#     st.subheader("🔍 What You Can Do Here")
#     st.markdown("""
#     - View a searchable list of previously reviewed claims
#     - Filter by category, product, or approval status
#     - Click on a claim to see its full details
#     """)
#     sample_data = pd.DataFrame({
#         "Claim Text": ["Supports immune function", "Boosts energy levels", "Aids digestion"],
#         "Product": ["Nestlé Protein Shake", "Vital Energy Bar", "Gut Health Gummies"],
#         "Category": ["Immunity", "Energy", "Digestion"],
#         "Status": ["Approved", "In Review", "Rejected"],
#         "Review Date": ["2024-10-15", "2025-02-01", "2025-03-12"],
#     })
#     # --- Search and Filter Controls ---
#     st.subheader("🔎 Search & Filter")

#     search_term = st.text_input("Search claims by keyword", "")
#     category_filter = st.selectbox("Filter by Category", ["All"] + sorted(sample_data["Category"].unique()))
#     product_filter = st.selectbox("Filter by Product", ["All"] + sorted(sample_data["Product"].unique()))
#     status_filter = st.selectbox("Filter by Approval Status", ["All"] + sorted(sample_data["Status"].unique()))

#     # --- Filter the data ---
#     filtered_data = sample_data.copy()

#     if search_term:
#         filtered_data = filtered_data[filtered_data["Claim Text"].str.contains(search_term, case=False)]

#     if category_filter != "All":
#         filtered_data = filtered_data[filtered_data["Category"] == category_filter]

#     if product_filter != "All":
#         filtered_data = filtered_data[filtered_data["Product"] == product_filter]

#     if status_filter != "All":
#         filtered_data = filtered_data[filtered_data["Status"] == status_filter]

#     # Optional note for context
#     st.info("This tool is designed to help regulatory teams avoid duplicate reviews, find substantiation, and reuse already-approved language.")

#     # Sample placeholder data for the prototype
    

#     st.subheader("📋 Claims Table")
#     st.dataframe(filtered_data) 

#     st.subheader("📋 Reviewed Claims)")

#     for index, row in filtered_data.iterrows():
#         with st.expander(f"{row['Claim Text']} – {row['Product']}"):
#             st.markdown(f"""
#             **🧠 Category:** {row['Category']}  
#             **✅ Status:** {row['Status']}  
#             **📅 Reviewed On:** {row['Review Date']}  
#             **🔗 Substantiation File:** [View PDF](#)  
#             **👩‍⚖️ Reviewed By:** M.T.  
#             **🏷️ Tags:** adult, protein, Canada  
#             **📚 Source Link:** [CFIA Regulation](#)
#             """)         
    




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
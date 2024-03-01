import streamlit as st
import requests
import pandas as pd

# Function to search for studies based on a query
@st.cache_data  # Cache data to improve performance
def search_studies(query):
    url = f"https://clinicaltrials.gov/api/query/full_studies?expr={query}&max_rnk=50&fmt=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        studies = []
        for study_info in data['FullStudiesResponse']['FullStudies']:
            study = {
                'NCT Number': study_info['Study']['ProtocolSection']['IdentificationModule']['NCTId'],
                'Title': study_info['Study']['ProtocolSection']['IdentificationModule'].get('OfficialTitle', 'Not Available'),
                'Status': study_info['Study']['ProtocolSection']['StatusModule']['OverallStatus'],
                'Sponsor': study_info['Study']['ProtocolSection']['SponsorCollaboratorsModule'].get('LeadSponsor', {}).get('LeadSponsorName', 'Not Available'),
            }
            studies.append(study)
        return pd.DataFrame(studies)
    else:
        st.error("Failed to fetch data: Server responded with an error")
        return pd.DataFrame()

# Detailed view of a selected study
def view_study_details(nct_number):
    url = f"https://clinicaltrials.gov/api/query/full_studies?expr={nct_number}&fmt=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        study_info = data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']

        # Display the study details
        st.markdown(f"## Study Details for {nct_number}")

        # Displaying sections with markdown for readability
        # Identification Module
        st.markdown("""
        **Identification**
        - **Title:** {}
        - **Brief Title:** {}
        - **Acronym:** {}
        - **Study Type:** {}
        """.format(
            study_info['IdentificationModule'].get('OfficialTitle', 'Not Available'),
            study_info['IdentificationModule'].get('BriefTitle', 'Not Available'),
            study_info['IdentificationModule'].get('Acronym', 'Not Available'),
            study_info['DesignModule'].get('StudyType', 'Not Available')
        ))

        # Status Module
        st.markdown("""
        **Status**
        - **Overall Status:** {}
        - **Start Date:** {}
        - **Completion Date:** {}
        - **Last Update Posted:** {}
        """.format(
            study_info['StatusModule'].get('OverallStatus', 'Not Available'),
            study_info['StatusModule'].get('StartDate', 'Not Available'),
            study_info['StatusModule'].get('CompletionDate', {}).get('CompletionDate', 'Not Available'),
            study_info['StatusModule'].get('LastUpdateSubmitDate', 'Not Available')
        ))

        # Design Module
        st.markdown("""
        **Design**
        - **Study Phase:** {}
        - **Allocation:** {}
        - **Intervention Model:** {}
        - **Primary Purpose:** {}
        - **Masking:** {}
        """.format(
            ", ".join(study_info['DesignModule'].get('PhaseList', {}).get('Phase', ['Not Available'])),
            study_info['DesignModule'].get('DesignInfo', {}).get('Allocation', 'Not Available'),
            study_info['DesignModule'].get('DesignInfo', {}).get('InterventionModel', 'Not Available'),
            study_info['DesignModule'].get('DesignInfo', {}).get('PrimaryPurpose', 'Not Available'),
            study_info['DesignModule'].get('DesignInfo', {}).get('Masking', 'Not Available')
        ))

        # Eligibility Module
        st.markdown("""
        **Eligibility**
        - **Age Limits:** {} to {}
        - **Gender Eligibility:** {}
        - **Healthy Volunteers:** {}
        """.format(
            study_info['EligibilityModule'].get('MinimumAge', 'Not Available'),
            study_info['EligibilityModule'].get('MaximumAge', 'Not Available'),
            study_info['EligibilityModule'].get('Gender', 'Not Available'),
            study_info['EligibilityModule'].get('HealthyVolunteers', 'Not Available')
        ))

        # Contacts and Locations Module
        st.markdown("**Locations**")
        locations = study_info['ContactsLocationsModule'].get('LocationList', [])
        if locations and isinstance(locations, list):  # Ensure it's a list
            for location in locations:
                if isinstance(location, dict):  # Ensure each item is a dictionary
                    facility_name = location.get('Facility', {}).get('Name', 'Not Available') if isinstance(
                        location.get('Facility', {}), dict) else 'Not Available'
                    status = location.get('Status', 'Not Available')
                    contact_name = location.get('Contact', {}).get('LastName', 'Not Available') if isinstance(
                        location.get('Contact', {}), dict) else 'Not Available'
                    phone = location.get('Contact', {}).get('Phone', 'Not Available') if isinstance(
                        location.get('Contact', {}), dict) else 'Not Available'
                    st.markdown(
                        f"- **Facility:** {facility_name}, **Status:** {status}, **Contact:** {contact_name}, **Phone:** {phone}")
        else:
            st.markdown("- No locations available")

         # Expand with more sections as needed
        # Outcomes Module
        st.markdown("**Outcomes**")
        # Primary Outcomes
        primary_outcomes = study_info['OutcomesModule'].get('PrimaryOutcomeList', {}).get('PrimaryOutcome', [])
        if isinstance(primary_outcomes, list):  # Ensure it's a list
            for outcome in primary_outcomes:
                if isinstance(outcome, dict):  # Ensure each outcome is a dictionary
                    measure = outcome.get('PrimaryOutcomeMeasure', 'Not Available')
                    time_frame = outcome.get('PrimaryOutcomeTimeFrame', 'Not Available')
                    description = outcome.get('PrimaryOutcomeDescription', 'Not Available')
                    st.markdown(
                        f"- **Primary Outcome Measure:** {measure}, **Time Frame:** {time_frame}, **Description:** {description}")

        # Secondary Outcomes
        secondary_outcomes = study_info['OutcomesModule'].get('SecondaryOutcomeList', {}).get('SecondaryOutcome', [])
        if isinstance(secondary_outcomes, list):  # Ensure it's a list
            for outcome in secondary_outcomes:
                if isinstance(outcome, dict):  # Ensure each outcome is a dictionary
                    measure = outcome.get('SecondaryOutcomeMeasure', 'Not Available')
                    time_frame = outcome.get('SecondaryOutcomeTimeFrame', 'Not Available')
                    description = outcome.get('SecondaryOutcomeDescription', 'Not Available')
                    st.markdown(
                        f"- **Secondary Outcome Measure:** {measure}, **Time Frame:** {time_frame}, **Description:** {description}")

    else:
        st.error("Failed to fetch study details: Server responded with an error")


def main():
    st.title('Clinical Trials Search')
    
    # Add custom CSS for theme
    st.markdown("""
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                }

                h1, h2, h3, h4, h5, h6 {
                    color: #333333;
                }

                .stTextInput>div>div>input {
                    border-radius: 10px;
                    border: 2px solid #cccccc;
                }

                .stButton>button {
                    background-color: #007bff;
                    color: white;
                    border-radius: 10px;
                    border: none;
                    padding: 8px 16px;
                    cursor: pointer;
                }

                .stButton>button:hover {
                    background-color: #0056b3;
                }
            </style>
        """, unsafe_allow_html=True)

    # User input for search
    query = st.text_input("Enter Sponsor Name, Study Name, Study ID, or Disease")

    if query:
        search_results = search_studies(query)
        if not search_results.empty:
            st.subheader('Search Results')
            # Create a list of strings combining the NCT Number and Title for each study
            options = [f"{row['NCT Number']}: {row['Title']}" for index, row in search_results.iterrows()]
            # Use the full list as options for the selectbox
            selected_option = st.selectbox('Select a study to view details', options)
            # Extract the NCT Number back from the selected option
            selected_nct_number = selected_option.split(":")[0]
            if st.button('Show Details'):
                view_study_details(selected_nct_number)
        else:
            st.write("No studies found matching the query.")


if __name__ == "__main__":
    main()

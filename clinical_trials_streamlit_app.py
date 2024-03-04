import streamlit as st
import requests
import pandas as pd

# Cache data to improve performance
@st.cache
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

def view_study_details(nct_number):
    url = f"https://clinicaltrials.gov/api/query/full_studies?expr={nct_number}&fmt=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        study_info = data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']
        return study_info
    else:
        st.error("Failed to fetch study details: Server responded with an error")
        return None

def display_study_details(study_info):
    if study_info:
        st.markdown("## Study Details")

        # Status Module
        status_module = study_info.get('StatusModule', {})
        overall_status = status_module.get('OverallStatus', 'Not Available')
        start_date = status_module.get('StartDateStruct', {}).get('StartDate', 'Not Available')
        completion_date = status_module.get('CompletionDateStruct', {}).get('CompletionDate', 'Not Available')
        last_update_date = status_module.get('LastUpdateSubmitDate', 'Not Available')
        st.markdown("""
            **Status**
            - **Overall Status:** {}
            - **Start Date:** {}
            - **Completion Date:** {}
            - **Last Update Date:** {}
        """.format(overall_status, start_date, completion_date, last_update_date))

        # Baseline Characteristics
        baseline_section = study_info.get('ResultsSection', {}).get('BaselineCharacteristicsModule', {})
        total_enrolled = baseline_section.get('BaselinePopulationDescription', 'Not Available')
        st.markdown("""
            **Baseline Characteristics**
            - **Total Enrolled:** {}
        """.format(total_enrolled))
        
        # Add additional baseline details here...

        # Efficacy Results
        efficacy_results = study_info.get('ResultsSection', {}).get('OutcomesMeasuresModule', {})
        primary_outcomes = efficacy_results.get('PrimaryOutcomeList', {}).get('PrimaryOutcome', [])
        st.markdown("**Efficacy Results - Primary Outcomes**")
        for outcome in primary_outcomes:
            measure = outcome.get('OutcomeMeasure', 'Not Available')
            time_frame = outcome.get('OutcomeTimeFrame', 'Not Available')
            description = outcome.get('OutcomeDescription', 'Not Available')
            st.markdown(f"- **Measure:** {measure}, **Time Frame:** {time_frame}, **Description:** {description}")
        
        # Add additional efficacy details here...

        # Adverse Events
        adverse_events_section = study_info.get('ResultsSection', {}).get('AdverseEventsModule', {})
        total_subjects_affected = adverse_events_section.get('TotalSubjectsAffected', 'Not Available')
        total_adverse_events = adverse_events_section.get('TotalAdverseEvents', 'Not Available')
        st.markdown("""
            **Adverse Events**
            - **Total Subjects Affected:** {}
            - **Total Adverse Events:** {}
        """.format(total_subjects_affected, total_adverse_events))
        
        # Add additional adverse event details here...

        # Participant Flow
        participant_flow_section = study_info.get('ResultsSection', {}).get('ParticipantFlowModule', {})
        recruitment_details = participant_flow_section.get('RecruitmentDetails', 'Not Available')
        st.markdown("""
            **Participant Flow**
            - **Recruitment Details:** {}
        """.format(recruitment_details))
        
        # Add additional participant flow details here...

    else:
        st.error("Failed to fetch study details: Study information not found")

def main():
    st.title('Clinical Trials Search Dashboard')

    query = st.text_input("Enter Sponsor Name, Study Name, Study ID, or Disease")

    if query:
        search_results = search_studies(query)
        if not search_results.empty:
            st.subheader('Search Results')
            study_selection = st.selectbox('Select a study to view details', search_results['NCT Number'])
            if st.button('Show Details'):
                study_info = view_study_details(study_selection)
                display_study_details(study_info)
        else:
            st.write("No studies found matching the query.")

if __name__ == "__main__":
    main()

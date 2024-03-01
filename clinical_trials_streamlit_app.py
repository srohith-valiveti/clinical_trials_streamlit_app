import streamlit as st
import requests
import pandas as pd


# Cache data to improve performance
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
                'Title': study_info['Study']['ProtocolSection']['IdentificationModule'].get('OfficialTitle',
                                                                                            'Not Available'),
                'Status': study_info['Study']['ProtocolSection']['StatusModule']['OverallStatus'],
                'Sponsor': study_info['Study']['ProtocolSection']['SponsorCollaboratorsModule'].get('LeadSponsor',
                                                                                                    {}).get(
                    'LeadSponsorName', 'Not Available'),
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
        return study_info  # Return the detailed study information for later display
    else:
        st.error("Failed to fetch study details: Server responded with an error")
        return None  # Return None if the details couldn't be fetched


def display_study_details(study_info):
    if study_info:  # Check if study_info is not None
        # Display sections with markdown for readability
        st.markdown(f"## Study Details")

        # Use columns to organize the display
        col1, col2 = st.columns(2)

        with col1:
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

        with col2:
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


        # Outcomes Module
        st.markdown("**Outcomes**")
        # Primary Outcomes
        primary_outcomes = study_info.get('OutcomesModule', {}).get('PrimaryOutcomeList', {}).get('PrimaryOutcome', [])
        if primary_outcomes:
            st.markdown("**Primary Outcomes:**")
            for outcome in primary_outcomes:
                measure = outcome.get('PrimaryOutcomeMeasure', 'Not Available')
                time_frame = outcome.get('PrimaryOutcomeTimeFrame', 'Not Available')
                description = outcome.get('PrimaryOutcomeDescription', 'Not Available')
                st.markdown(f"- **Measure:** {measure}, **Time Frame:** {time_frame}, **Description:** {description}")

        # Secondary Outcomes
        secondary_outcomes = study_info.get('OutcomesModule', {}).get('SecondaryOutcomeList', {}).get(
            'SecondaryOutcome', [])
        if secondary_outcomes:
            st.markdown("**Secondary Outcomes:**")
            for outcome in secondary_outcomes:
                measure = outcome.get('SecondaryOutcomeMeasure', 'Not Available')
                time_frame = outcome.get('SecondaryOutcomeTimeFrame', 'Not Available')
                description = outcome.get('SecondaryOutcomeDescription', 'Not Available')
                st.markdown(f"- **Measure:** {measure}, **Time Frame:** {time_frame}, **Description:** {description}")

        # Additional sections such as Study Arms, Interventions, and Participant Flow can be added here following the same pattern

            # Study Arms Module
            st.markdown("**Study Arms**")
            arms = study_info.get('ArmsInterventionsModule', {}).get('ArmGroupList', {}).get('ArmGroup', [])
            if arms:
                for arm in arms:
                    arm_group_label = arm.get('ArmGroupLabel', 'Not Available')
                    arm_group_type = arm.get('ArmGroupType', 'Not Available')
                    description = arm.get('ArmGroupDescription', 'Not Available')
                    st.markdown(
                        f"- **Label:** {arm_group_label}, **Type:** {arm_group_type}, **Description:** {description}")
            else:
                st.markdown("- No study arms available")

            # Interventions Module
            st.markdown("**Interventions**")
            interventions = study_info.get('ArmsInterventionsModule', {}).get('InterventionList', {}).get(
                'Intervention', [])
            if interventions:
                for intervention in interventions:
                    intervention_name = intervention.get('InterventionName', 'Not Available')
                    intervention_type = intervention.get('InterventionType', 'Not Available')
                    description = intervention.get('InterventionDescription', 'Not Available')
                    st.markdown(
                        f"- **Name:** {intervention_name}, **Type:** {intervention_type}, **Description:** {description}")
            else:
                st.markdown("- No interventions available")

            # Inclusion & Exclusion Criteria
        st.markdown("**Eligibility Criteria**")
        # Directly access the eligibility criteria text block if it exists
        eligibility_criteria = study_info.get('EligibilityModule', {}).get('EligibilityCriteria', 'Not Available')
        if eligibility_criteria != 'Not Available':
            # Assuming the criteria are separated into Inclusion and Exclusion in the text block
            criteria_sections = eligibility_criteria.split('Exclusion Criteria:')
            if len(criteria_sections) > 1:
                # If there is clear separation between Inclusion and Exclusion
                st.markdown("**Inclusion Criteria:**")
                st.markdown(criteria_sections[0].replace('Inclusion Criteria:', '').strip())  # Clean up Inclusion text
                st.markdown("**Exclusion Criteria:**")
                st.markdown(criteria_sections[1].strip())  # Clean up Exclusion text
            else:
                # If no clear separation, display the entire criteria as one block
                st.markdown(eligibility_criteria.strip())  # Just clean up and display the string
        else:
            st.markdown("- No eligibility criteria available")

            # Participant Flow Module
            st.markdown("**Participant Flow**")
            participant_flow = study_info.get('ResultsSection', {}).get('ParticipantFlowModule', {})
            if participant_flow:
                rec_details = participant_flow.get('RecruitmentDetails', 'Not Available')
                pre_assign_details = participant_flow.get('PreAssignmentDetails', 'Not Available')
                st.markdown(
                    f"- **Recruitment Details:** {rec_details}, **Pre-Assignment Details:** {pre_assign_details}")

                # Flow Groups
                flow_groups = participant_flow.get('FlowGroupList', {}).get('FlowGroup', [])
                if flow_groups:
                    st.markdown("**Flow Groups:**")
                    for group in flow_groups:
                        group_title = group.get('FlowGroupTitle', 'Not Available')
                        group_desc = group.get('FlowGroupDescription', 'Not Available')
                        st.markdown(f"- **Title:** {group_title}, **Description:** {group_desc}")
                else:
                    st.markdown("- No flow groups information available")
            else:
                st.markdown("- No participant flow information available")

def main():
    st.title('Clinical Trials Search Dashboard')

    # User input for search
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

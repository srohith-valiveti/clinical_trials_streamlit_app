import streamlit as st
import requests
import pandas as pd


# Cache data to improve performance
@st.cache  # Note: Corrected from @st.cache_data
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
        return study_info
    else:
        st.error("Failed to fetch study details: Server responded with an error")
        return None


def display_study_details(study_info):
    if study_info:  # Check if study_info is not None
        # Display sections with markdown for readability
        st.markdown("## Study Details")

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
            st.markdown("**Status**")
            overall_status = study_info['StatusModule'].get('OverallStatus', 'Not Available')
            start_date = study_info['StatusModule'].get('StartDate', {}).get('StartDate', 'Not Available')
            completion_date = study_info['StatusModule'].get('CompletionDate', {}).get('CompletionDate',
                                                                                       'Not Available')
            last_update_date = study_info['StatusModule'].get('LastUpdateSubmitDate', 'Not Available')
            st.markdown(f"- **Overall Status:** {overall_status}")
            st.markdown(f"- **Start Date:** {start_date}")
            st.markdown(f"- **Completion Date:** {completion_date}")
            st.markdown(f"- **Last Update Date:** {last_update_date}")

            # Eligibility Module
            st.markdown("**Eligibility**")
            eligibility = study_info.get('EligibilityModule', {})
            age_minimum = eligibility.get('MinimumAge', 'Not Available')
            age_maximum = eligibility.get('MaximumAge', 'Not Available')
            gender = eligibility.get('Gender', 'Not Available')
            healthy_volunteers = eligibility.get('HealthyVolunteers', 'Not Available')
            st.markdown(f"""
                - **Minimum Age:** {age_minimum}
                - **Maximum Age:** {age_maximum}
                - **Gender:** {gender}
                - **Accepts Healthy Volunteers:** {healthy_volunteers}
            """)

            # Locations Module - Count Only
            locations = study_info.get('ContactsLocationsModule', {}).get('LocationList', {}).get('Location', [])
            number_of_locations = len(locations)  # Just count the number of items in the list
            st.markdown("**Number of Locations:** {}".format(number_of_locations))

            # Keywords Module
            keywords_section = study_info.get('ConditionsModule', {}).get('KeywordList', {}).get('Keyword', [])
            if keywords_section:
                st.markdown("**Keywords**")
                keywords = ', '.join(keywords_section)
                st.markdown(f"- **Keywords:** {keywords}")
            else:
                st.markdown("- No keywords available")

        # Continuing within the 'display_study_details' function:

        with col2:
            # Study Design Module
            st.markdown("**Study Design**")
            study_design = study_info.get('DesignModule', {})
            study_type = study_design.get('StudyType', 'Not Available')
            study_design_allocation = study_design.get('DesignInfo', {}).get('Allocation', 'Not Available')
            study_design_intervention = study_design.get('DesignInfo', {}).get('InterventionModel', 'Not Available')
            study_design_purpose = study_design.get('DesignInfo', {}).get('PrimaryPurpose', 'Not Available')
            st.markdown(f"""
                - **Study Type:** {study_type}
                - **Allocation:** {study_design_allocation}
                - **Intervention Model:** {study_design_intervention}
                - **Primary Purpose:** {study_design_purpose}
            """)

            # Outcomes Module
            st.markdown("**Outcomes**")
            outcomes = study_info.get('OutcomesModule', {})
            primary_outcomes = outcomes.get('PrimaryOutcomeList', {}).get('PrimaryOutcome', [])
            if primary_outcomes:
                st.markdown("**Primary Outcomes:**")
                for outcome in primary_outcomes:
                    measure = outcome.get('PrimaryOutcomeMeasure', 'Not Available')
                    time_frame = outcome.get('PrimaryOutcomeTimeFrame', 'Not Available')
                    description = outcome.get('PrimaryOutcomeDescription', 'Not Available')
                    st.markdown(
                        f"- **Measure:** {measure}, **Time Frame:** {time_frame}, **Description:** {description}")

            st.markdown("**Secondary Outcomes**")
            secondary_outcomes = study_info.get('OutcomesModule', {}).get('SecondaryOutcomeList', {}).get(
                'SecondaryOutcome', [])
            if secondary_outcomes:
                for outcome in secondary_outcomes:
                    measure = outcome.get('SecondaryOutcomeMeasure', 'Not Available')
                    time_frame = outcome.get('SecondaryOutcomeTimeFrame', 'Not Available')
                    description = outcome.get('SecondaryOutcomeDescription', 'Not Available')
                    st.markdown(
                        f"- **Measure:** {measure}, **Time Frame:** {time_frame}, **Description:** {description}")
            else:
                st.markdown("- No secondary outcomes available")

                # Adverse Events Module
                st.markdown("**Adverse Events**")
                adverse_events = study_info.get('ResultsSection', {}).get('AdverseEventsModule', {})
                if adverse_events:
                    total_subjects_affected = adverse_events.get('TotalSubjectsAffected', 'Not Available')
                    total_adverse_events = adverse_events.get('TotalAdverseEvents', 'Not Available')
                    st.markdown(f"""
                            - **Total Subjects Affected:** {total_subjects_affected}
                            - **Total Adverse Events:** {total_adverse_events}
                        """)

                # Here you could add more detailed adverse events information if needed

                # Participant Flow Module
            st.markdown("**Participant Flow**")
            participant_flow = study_info.get('ResultsSection', {}).get('ParticipantFlowModule', {})
            if participant_flow:
                recruitment_details = participant_flow.get('RecruitmentDetails', 'Not Available')
                pre_assignment_details = participant_flow.get('PreAssignmentDetails', 'Not Available')
                st.markdown(f"""
                       - **Recruitment Details:** {recruitment_details}
                       - **Pre-Assignment Details:** {pre_assignment_details}
                   """)
                # Additional participant flow details could be included here if necessary

        # Baseline Characteristics Module
        baseline_characteristics = study_info.get('ResultsSection', {}).get('BaselineCharacteristicsModule', {})
        if baseline_characteristics:
            st.markdown("### Baseline Characteristics")
            total_enrolled = baseline_characteristics.get('BaselinePopulationDescription', 'Not Available')
            st.markdown(f"- **Total Enrolled:** {total_enrolled}")

            baseline_groups = baseline_characteristics.get('BaselineGroupList', {}).get('BaselineGroup', [])
            if baseline_groups:
                for group in baseline_groups:
                    group_title = group.get('BaselineGroupTitle', 'Not Available')
                    st.markdown(f"#### Group: {group_title}")

                    # Baseline Measurements
                    measurements = group.get('BaselineMeasureList', {}).get('BaselineMeasure', [])
                    for measure in measurements:
                        measure_title = measure.get('BaselineMeasureTitle', 'Not Available')
                        measure_unit = measure.get('BaselineMeasureUnitOfMeasure', 'Not Available')
                        st.markdown(f"- **Measure:** {measure_title} ({measure_unit})")

                        # Categories within each measurement
                        categories = measure.get('BaselineCategoryList', {}).get('BaselineCategory', [])
                        for category in categories:
                            category_title = category.get('BaselineCategoryTitle', 'Not Available')
                            measurements = category.get('BaselineMeasurementList', {}).get('BaselineMeasurement', [])
                            for measurement in measurements:
                                measure_value = measurement.get('BaselineMeasurementValue', 'Not Available')
                                participants = measurement.get('NumberOfParticipants', 'Not Available')
                                st.markdown(
                                    f"  - **Category:** {category_title}, **Value:** {measure_value}, **Participants:** {participants}")
            else:
                st.markdown("- No baseline group information available")
        else:
            st.markdown("- No baseline characteristics information available")



    else:
        st.error("Failed to fetch study details: Server responded with an error")


def main():
    st.title('Clinical Trials Search Dashboard')

    # Dictionary Search Section
    st.markdown("## Dictionary Search for Medical Terms")
    st.markdown("Use the following resources to search for medical terms:")

    # MedDRA Dictionary Search
    meddra_url = "https://www.meddra.org/"
    st.markdown(f"[Search terms on MedDRA]({meddra_url}) (Medical Dictionary for Regulatory Activities)")

    # CDISC Dictionary Search
    cdisc_url = "https://www.cdisc.org/"
    st.markdown(f"[Search terms on CDISC]({cdisc_url}) (Clinical Data Interchange Standards Consortium)")

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

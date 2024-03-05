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
    if study_info:  # Check if study_info is not None
        st.markdown("<style> body { font-family: 'Arial', sans-serif; font-size: 14px; } </style>", unsafe_allow_html=True)

        st.markdown("## Study Details")

        st.markdown("### Identification")
        identification = study_info['IdentificationModule']
        st.text(f"NCT Number: {identification.get('NCTId', 'Not Available')}")
        st.text(f"Org Study ID: {identification.get('OrgStudyIdInfo', {}).get('OrgStudyId', 'Not Available')}")
        st.text(f"Organization Name: {identification.get('Organization', {}).get('OrgFullName', 'Not Available')}")
        st.text(f"Organization Class: {identification.get('Organization', {}).get('OrgClass', 'Not Available')}")
        st.text(f"Brief Title: {identification.get('BriefTitle', 'Not Available')}")
        st.text(f"Official Title: {identification.get('OfficialTitle', 'Not Available')}")
        st.text(f"Acronym: {identification.get('Acronym', 'Not Available')}")

        st.markdown("### Enrollment")
        enrollment_info = study_info.get('EnrollmentInfo', {})
        st.text(f"Enrollment Count: {enrollment_info.get('EnrollmentCount', 'Not Available')}")
        st.text(f"Enrollment Type: {enrollment_info.get('EnrollmentType', 'Not Available')}")

        st.markdown("### Status")
        status = study_info['StatusModule']
        st.text(f"Status Verified Date: {status.get('StatusVerifiedDate', 'Not Available')}")
        st.text(f"Overall Status: {status.get('OverallStatus', 'Not Available')}")
        st.text(f"Has Expanded Access: {status.get('ExpandedAccessInfo', {}).get('HasExpandedAccess', 'Not Available')}")
        st.text(f"Start Date: {status.get('StartDateStruct', {}).get('StartDate', 'Not Available')} ({status.get('StartDateStruct', {}).get('StartDateType', 'Not Available')})")
        st.text(f"Primary Completion Date: {status.get('PrimaryCompletionDateStruct', {}).get('CompletionDate', 'Not Available')} ({status.get('PrimaryCompletionDateStruct', {}).get('CompletionDateType', 'Not Available')})")
        st.text(f"Completion Date: {status.get('CompletionDateStruct', {}).get('CompletionDate', 'Not Available')} ({status.get('CompletionDateStruct', {}).get('CompletionDateType', 'Not Available')})")
        st.text(f"Study First Submit Date: {status.get('StudyFirstSubmitDate', 'Not Available')}")
        st.text(f"Study First Submit QC Date: {status.get('StudyFirstSubmitQCDate', 'Not Available')}")
        st.text(f"Study First Post Date: {status.get('StudyFirstPostDateStruct', {}).get('StudyFirstPostDate', 'Not Available')} ({status.get('StudyFirstPostDateStruct', {}).get('StudyFirstPostDateType', 'Not Available')})")
        st.text(f"Last Update Submit Date: {status.get('LastUpdateSubmitDate', 'Not Available')}")
        st.text(f"Last Update Post Date: {status.get('LastUpdatePostDateStruct', {}).get('LastUpdatePostDate', 'Not Available')} ({status.get('LastUpdatePostDateStruct', {}).get('LastUpdatePostDateType', 'Not Available')})")

        st.markdown("### Conditions")
        conditions = study_info['ConditionsModule']['ConditionList']['Condition']
        st.markdown(f"**Conditions:** {', '.join(conditions)}")

        st.markdown("### Keywords")
        keywords = study_info['ConditionsModule']['KeywordList']['Keyword']
        st.markdown(f"**Keywords:** {', '.join(keywords)}")

        st.markdown("### Description")
        description = study_info['DescriptionModule']
        st.markdown(f"**Brief Summary:** {description.get('BriefSummary', 'Not Available')}")
        st.markdown(f"**Detailed Description:** {description.get('DetailedDescription', 'Not Available')}")

        st.markdown("### Design")
        design = study_info['DesignModule']
        st.text(f"Study Type: {design.get('StudyType', 'Not Available')}")
        phases = design.get('PhaseList', {}).get('Phase', [])
        st.text(f"Phases: {', '.join(phases)}")

        st.markdown("### Design Info")
        design_info = design.get('DesignInfo', {})
        st.text(f"Allocation: {design_info.get('DesignAllocation', 'Not Available')}")
        st.text(f"Intervention Model: {design_info.get('DesignInterventionModel', 'Not Available')}")
        st.text(f"Intervention Model Description: {design_info.get('DesignInterventionModelDescription', 'Not Available')}")
        st.text(f"Primary Purpose: {design_info.get('DesignPrimaryPurpose', 'Not Available')}")

        st.markdown("### Masking")
        masking_info = design_info.get('DesignMaskingInfo', {})
        st.text(f"Masking: {masking_info.get('DesignMasking', 'Not Available')}")
        who_masked = masking_info.get('DesignWhoMaskedList', {}).get('DesignWhoMasked', [])
        st.text(f"Who is Masked: {', '.join(who_masked)}")

        st.markdown("### Arms & Interventions")
        arm_groups = study_info.get('ArmsInterventionsModule', {}).get('ArmGroupList', {}).get('ArmGroup', [])
        if isinstance(arm_groups, dict):
            arm_groups = [arm_groups]

        for arm in arm_groups:
            arm_label = arm.get('ArmGroupLabel', 'Not Available')
            arm_type = arm.get('ArmGroupType', 'Not Available')
            arm_description = arm.get('ArmGroupDescription', 'Not Available')
            interventions = arm.get('ArmGroupInterventionList', {}).get('ArmGroupInterventionName', [])
            if isinstance(interventions, str):
                interventions = [interventions]
            interventions_str = ', '.join(interventions) if interventions else 'Not Available'

            st.markdown(f"**{arm_label} ({arm_type})**")
            st.text(f"Description: {arm_description}")
            st.text(f"Interventions: {interventions_str}")
            st.markdown("---")

        st.markdown("### Outcomes")
        primary_outcomes = study_info['OutcomesModule'].get('PrimaryOutcomeList', {}).get('PrimaryOutcome', [])
        if primary_outcomes:
            st.markdown("**Primary Outcomes:**")
            for outcome in primary_outcomes:
                measure = outcome.get('PrimaryOutcomeMeasure', 'Not Available')
                description = outcome.get('PrimaryOutcomeDescription', 'Not Available')
                time_frame = outcome.get('PrimaryOutcomeTimeFrame', 'Not Available')
                st.text(f"- Measure: {measure}")
                st.text(f"  Description: {description}")
                st.text(f"  Time Frame: {time_frame}")
            st.markdown("---")

        secondary_outcomes = study_info['OutcomesModule'].get('SecondaryOutcomeList', {}).get('SecondaryOutcome', [])
        if secondary_outcomes:
            st.markdown("**Secondary Outcomes:**")
            for outcome in secondary_outcomes:
                measure = outcome.get('SecondaryOutcomeMeasure', 'Not Available')
                description = outcome.get('SecondaryOutcomeDescription', 'Not Available')
                time_frame = outcome.get('SecondaryOutcomeTimeFrame', 'Not Available')
                st.text(f"- Measure: {measure}")
                st.text(f"  Description: {description}")
                st.text(f"  Time Frame: {time_frame}")
            st.markdown("---")

        st.markdown("### Eligibility Criteria")
        eligibility = study_info.get('EligibilityModule', {})
        st.text(f"Healthy Volunteers: {eligibility.get('HealthyVolunteers', 'Not Available')}")
        st.text(f"Gender: {eligibility.get('Gender', 'Not Available')}")
        st.text(f"Minimum Age: {eligibility.get('MinimumAge', 'Not Available')}")
        st.text(f"Maximum Age: {eligibility.get('MaximumAge', 'Not Available')}")

        st.markdown("**Key Inclusion Criteria:**", unsafe_allow_html=True)
        inclusion_criteria = eligibility.get('EligibilityCriteria', '').split('\n\n')
        for criterion in inclusion_criteria:
            st.text(f"- {criterion}")

        st.markdown("**Key Exclusion Criteria:**", unsafe_allow_html=True)
        exclusion_criteria = eligibility.get('EligibilityCriteria', '').split('\n\n')
        for criterion in exclusion_criteria:
            st.text(f"- {criterion}")

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

from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import date, time

import warnings


warnings.filterwarnings("ignore", category=UserWarning)


class RFPKeyDates(BaseModel):
    """Contains the key dates information about the RFPs"""
    Document_num: str = Field(description="""The official identifier of the job, typically labeled as 'RFP No.', 'EOI No.', or similar. 
                      This is usually found on the first page of the document. 
                      Common formats include examples like 'EOI: NEA-FD-2081/82-CS-01', 'RFP No.: DOED/BOOT/2081/82/RFP-01', etc."""
                  ) 
    issued_date : str = Field(description="The RFP issued date. Please note that if the month is written like 'january', extract as it is. dont convert to the number")
    final_submission_date: str =Field(description="last date to submit the proposal. Please note that if the month is written like 'january', extract as it is. Dont convert to the number")
    Final_submission_time: time =Field(description="Time after this the submission is not allowed")
    last_queries_submission_date: date= Field(description="""This is the final date before all the proponent has to submit the
                                               queries / concerns they have regarding RFPs, EOI. It is also called last date to request for clarifications.
                                              Please note that ifthe month is written like 'january', extract as it is. Dont convert to the number """)
    query_response_date: str= Field(description="""This is the date the client will provide the clarifications of all the queries submitted. 
                                    Please note that if the month is written like 'january', extract as it is""")
    opening_date : str=Field(description="""The is the date in which the client will open the financial proposal
                              if it is RFP stage, and the winner is declared, hence it is also
                              called 'financial opening'. But if it is EOI state, it is just th EOI opening date
                            . The EOI is then evenluated. """)
    

    prebid_meeting_date: str =Field(description="""
                                     Client's prescheduled date for pre-bid or pre-submission meeting. 
                                     This date is generally announced to facilitate all 
                                     the bidders who have queries regarding submission. So on this
                                     date client will preapred clarifications of all the queries submitted.""")
    prebid_meeting_time: time=Field(description="Predbid meeting time")



class RFPClientContactDetails(BaseModel):
    """Extracts the client contact details from the RFP or EOI document.
    This details is available in PROPONENTS' MEETING Section or Contact Person regarding Query about EOI Document Section"""

    doc_num: str = Field(
        description="""The official reference number of the RFP or EOI.
        This is usually mentioned on the first page and may appear as 'RFP No.', 'EOI No.', etc.
        Common formats include: 'EOI: NEA-FD-2081/82-CS-01', 'RFP NO.: DOED/BOOT/2081/82/RFP-01'
        Dont use this, extract only form the given context."""
    )

    client: str = Field(
        description="""The full legal name of the client organization issuing the RFP or EOI. This is available in PROPONENTS' MEETING SECTION or 
        Contact Person regarding Query about EOI Document Section"""
    )

    address: str = Field(
        description="The complete mailing or physical address of the client organization."
    )

    client_representative_name: str = Field(
        description="The full name of the client's designated contact person for this RFP or EOI."
    )

    phone_number: str = Field(
        description="The phone or mobile number of the client or their representative. Include country code if available."
    )

    client_email: str = Field(
        description="The email address of the client or their representative. Include all listed emails if there are multiple."
    )



class RFPSubmissionDetails(BaseModel):
    """Extracted information about the EOI/RFP submission process."""

    doc_num: str = Field(
        description=(
            "The official reference number of the RFP or EOI. "
            "Usually found on the first page and may appear as 'RFP No.', 'EOI No.', etc. "
            "Examples: 'EOI: NEA-FD-2081/82-CS-01', 'RFP NO.: DOED/BOOT/2081/82/RFP-01'. "
            "Extract only from the given context; do not infer."
        )
    )

    submission_address: str = Field(
        description=(
            "Full mailing or physical address where the proposal should be submitted."
        )
    )

    submission_language: str = Field(
        description="Language(s) allowed or required for the submission."
    )

    submission_mode: Literal["electronic", "physical", "both"] = Field(
        description=(
            "Method(s) by which submissions should be made. "
            "If both hard copies and electronic submissions are allowed, use 'both'."
        )
    )
    submission_platform: str=Field(description="""In which platform the sumission has to be made. For example if physical, where to submit. 
                                   and if submission is to be made electronic through which electronic portal the document must be submitted.""")

    number_of_copies: int = Field(
        description="Number of copies of the submission required, if specified."
    )

    submission_fees_required: Literal['Yes', 'No', 'Not Sure']
    amount_of_submission_fees: Optional[float|int|str] = Field(default=None, description="Amount of fees to process the submitted document such as EOI, RFP etc.")






class RFPProcurementInformation(BaseModel):
    """Structured information extracted from a Request for Proposal (RFP) or Expression of Interest (EOI) document."""

    doc_num: str = Field(
        description=(
            "The official reference number of the RFP or EOI. "
            "This is usually mentioned on the first page and may appear as 'RFP No.', 'EOI No.', etc. "
            "Common formats include: 'EOI: NEA-FD-2081/82-CS-01', 'RFP NO.: DOED/BOOT/2081/82/RFP-01'. "
            "Extract only from the given context; do not invent or assume."
        )
    )

    procurement_method: Literal["QCBS", "CQ/CQS", "FBS", "LCS", "SSS", "ICS"] = Field(
        description="Procurement selection method used to award the contract (e.g., QCBS, CQS, FBS)."
    )

    funding_agency: str = Field(
        description="Name of the entity or organization financing the project (e.g., World Bank, ADB, GoN)."
    )

    contract_type: Literal[
        "Lump Sum",
        "Time-based",
        "Retainer and Call-Off Contract",
        "Percentage Contract",
        "Performance-Based / Output-Based Contract",
        "Cost Plus",
        "Fixed Budget Contract",
    ] = Field(
        description="Type of contract as stated or implied in the document.\n"
        "- Choose 'Performance-Based / Output-Based Contract' if payment is released upon completion or approval of specific deliverables (e.g., reports).\n"
        "- Choose 'Lump Sum' if payment is a single fixed amount not explicitly tied to deliverables or time.\n"
        "- Choose 'Time-based' if payment is based on person-days/months or hourly rates.\n"
        "Use the payment structure (e.g., milestones, reports) to decide."
    )

    joint_venture_allowed: Literal['Yes', 'No', 'Not Sure'] = Field(
        description="""Client may allow to associate with other companies to enhance the qualifications.
        Indicates whether joint ventures (JVs) are permitted to participate in the bidding process.
        """
    )

    max_no_of_firms_in_JV: str = Field(
        description="""How many firms can form a joint venture to bid project.
        Client may allow to associate with other companies to enhance the qualifications. If joint ventures are allowed,
        specify the maximum number of firms allowed to form a JV. Generally, the maximum number of
        joint venture allowed is three, but it may vary. 
        You may Look at `INSTRUCTIONS FOR SUBMISSION OF EXPRESSION OF INTEREST` SECTION explicitly to extract this information.
        Do Not assume us the provided context to extract the information.
        """
    )

    bidding_type: Literal["national", "international"] = Field(
        description=(
            "Specifies whether the procurement process is national or international.\n"
            "- 'International' allows participation from foreign firms.\n"
            "- 'National' restricts participation to local/domestic firms only."
        )
    )

    subcontracting_allowed: Literal['Yes', 'No', 'Not Sure'] = Field(
        description="Indicates whether subcontracting is allowed as per the bidding document."
    )

class RFPProjectInformation(BaseModel):
    """Structured information extracted from a Request for Proposal or Expression of Interest Document"""

    Document_num: str = Field(description="""The official identifier of the job, typically labeled as 'RFP No.', 'EOI No.', or similar. 
                      This is usually found on the first page of the document. 
                      Common formats include examples like 'EOI: NEA-FD-2081/82-CS-01', 'RFP No.: DOED/BOOT/2081/82/RFP-01', etc."""
                  ) 

    project_title: str = Field(description=(
                    "Extract the title of the project for which this procurement (EOI or RFP) is being issued. "
                    "This usually appears in phrases like 'Development of XYZ Project', 'Consulting services for the ABC Project', "
                    "or within parentheses near project details like capacity (e.g., 65 MW). "
                    "Return only the project name itself, such as 'Kaligandaki Upper Hydropower Project'."
                )

),
    service_type: str = Field(description="Type of the service being procured from the Project")
    project_stage: Literal["Pre-Feasibility Study", 
                           "Feasibility-Study", 
                           "Detailed-Design", 
                           'Tender-Documents', 
                           "Construction-Supervision", 
                           "Proof of concept", 
                           "Development", 
                           "Operation and Maintanence", 
                           "other"] = Field(description=(
                                  "Identify the **current project stage** of the project as described in the RFP/EOI. "
                                  "Do not select 'pre-feasibility study' or 'feasibility study' unless it is the actual phase the RFP/EOI is requesting work for. "
                                  "If the RFP talks about preparing designs, drawings, or tender documents, it is likely in the 'detailed design or development' stage. "
                                  "If the RFP is about overseeing actual work, it is in 'construction/supervision'."
                                  
                              ))



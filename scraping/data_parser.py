class DataParser:
    """
    A class to parse LinkedIn API responses and extract structured profile data.
    
    This class provides methods to extract various components of LinkedIn profiles
    including personal information, education, experience, skills, and contact details
    from API response JSON.
    
    Attributes:
        json_data (dict): The parsed JSON data from the API response
        page_response (Response): The original response object
    """
    
    def __init__(self, response):
        """
        Initialize the DataParser with an API response.
        
        Args:
            response (Response): The response object from a LinkedIn API request,
                                expected to have a .json() method
        """
        self.json_data = response.json()
        self.page_response = response

    def get_profile_data(self) -> dict:
        """
        Extract and structure the main profile data from LinkedIn response.
        
        This method extracts personal information, professional details, skills,
        experience, and education from the LinkedIn profile data. It combines
        these elements into a structured dictionary format.
        
        Returns:
            dict: A dictionary containing structured profile information with the following keys:
                - public_id (str): LinkedIn public identifier
                - full_name (str): User's full name
                - headline (str): Professional headline
                - summary (str): Profile summary, cleaned and normalized
                - industry_name (str): Industry classification
                - location (str): Geographic location
                - skills (list): List of skills from the profile
                - experience (list): List of work experiences
                - education (list): List of educational backgrounds
        """
        first_name = self.json_data.get("profile", {}).get("firstName")
        last_name = self.json_data.get("profile", {}).get("lastName")
        public_id = self.json_data.get("profile", {}).get("miniProfile", {}).get("publicIdentifier")
        summary = self.json_data.get("profile", {}).get("summary")
        headline = self.json_data.get("profile", {}).get("headline")
        industry_name = self.json_data.get("profile", {}).get("industryName")
        location = self.json_data.get("profile", {}).get("geoLocationName")
        skills = self._get_skills_data()
        experience = self._get_experience_data()
        education = self._get_education_data()
        full_name = f"{first_name} {last_name}"
        summary = " ".join(summary.split()).strip() if summary else None
        return {
            "public_id": public_id,
            "full_name": full_name,
            "headline": headline,
            "summary": summary,
            "industry_name": industry_name,
            "location": location,
            "skills": skills,
            "experience": experience,
            "education": education,
        }

    def _get_education_data(self) -> list:
        """
        Extract education information from LinkedIn profile data.
        
        This method processes the education section of a LinkedIn profile and
        extracts relevant details into a structured format.
        
        Returns:
            list: A list of dictionaries, each containing:
                - school_name (str): Name of the educational institution
                - degree (str): Degree or qualification obtained
                - period (dict): Time period information for the education
        """
        raw_education_data = self.json_data.get("educationView", {}).get("elements")
        if not raw_education_data:
            return []

        return [
            {
                "school_name": item.get("schoolName"),
                "degree": item.get("degreeName"),
                "period": item.get("timePeriod"),
            }
            for item in raw_education_data
        ]

    def _get_experience_data(self) -> list:
        """
        Extract work experience information from LinkedIn profile data.
        
        This method processes the work experience section of a LinkedIn profile
        and extracts relevant details into a structured format.
        
        Returns:
            list: A list of dictionaries, each containing:
                - job_title (str): Title or position held
                - company_name (str): Name of the employer
                - location (str): Work location
                - period (dict): Time period information for the position
                - description (str): Job description
        """
        raw_experience = self.json_data.get("positionView", {}).get("elements")
        if not raw_experience:
            return []
        return [
            {
                "job_title": item.get("title"),
                "company_name": item.get("companyName"),
                "location": item.get("locationName"),
                "period": item.get("timePeriod"),
                "description": item.get("description"),
            }
            for item in raw_experience
        ]

    def _get_skills_data(self) -> list:
        """
        Extract skills information from LinkedIn profile data.
        
        This method processes the skills section of a LinkedIn profile and
        returns a list of skill names.
        
        Returns:
            list: A list of skill names (str) listed on the profile
        """
        raw_skills = self.json_data.get("skillView", {}).get("elements")
        if not raw_skills:
            return []
        return [skill.get("name") for skill in raw_skills if skill.get("name")]

    def get_contact_details(self) -> dict:
        """
        Extract contact information from LinkedIn profile data.
        
        This method retrieves email address and phone number from the profile data
        if available.
        
        Returns:
            dict: A dictionary containing:
                - email (str): Email address from the profile
                - phone (str): Phone number from the profile
        """
        email = self.json_data.get("emailAddress")
        phone = self.json_data.get("phoneNumbers", [{}])[0].get("number")
        return {"email": email, "phone": phone}

    def get_connections_profile_ids(self) -> list:
        """
        Extract the public identifiers of a user's LinkedIn connections.
        
        This method processes the connections section of a LinkedIn response and
        extracts the public identifiers for each connection.
        
        Returns:
            list: A list of public identifiers (str) for the user's connections
        """
        connections_elements = self.json_data.get("elements", [])
        if not connections_elements:
            return []
        profile_ids = [
            item.get("connectedMemberResolutionResult", {}).get("publicIdentifier")
            for item in connections_elements
            if item.get("connectedMemberResolutionResult", {}).get("publicIdentifier")
        ]
        return profile_ids
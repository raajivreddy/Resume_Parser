from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class ContactInfo(BaseModel):
    name: Optional[str] = Field(None, description="Full name of the candidate")
    email: Optional[EmailStr] = Field(None, description="Email address of the candidate")
    phone: Optional[str] = Field(None, description="Phone number of the candidate")
    location: Optional[str] = Field(None, description="Location or address")

class Education(BaseModel):
    institution: Optional[str] = Field(None, description="Name of the educational institution")
    degree: Optional[str] = Field(None, description="Degree obtained")
    graduation_year: Optional[str] = Field(None, description="Year of graduation")

class Experience(BaseModel):
    company: Optional[str] = Field(None, description="Company name")
    position: Optional[str] = Field(None, description="Job title or position")
    duration: Optional[str] = Field(None, description="Duration of employment")
    description: Optional[str] = Field(None, description="Job description or responsibilities")

class Project(BaseModel):
    title: Optional[str] = Field(None, description="Project title")
    description: Optional[str] = Field(None, description="Project description")

class ResumeData(BaseModel):
    contact: ContactInfo = Field(default_factory=ContactInfo, description="Candidate contact details")
    education: List[Education] = Field(default_factory=list, description="List of educational backgrounds")
    experience: List[Experience] = Field(default_factory=list, description="List of work experiences")
    projects: List[Project] = Field(default_factory=list, description="List of projects")
    certifications: List[str] = Field(default_factory=list, description="List of certifications")
    skills: List[str] = Field(default_factory=list, description="List of skills")

class ParseResponse(BaseModel):
    status: str = Field(..., description="Status of the parsing request (e.g., 'success', 'error')")
    data: Optional[ResumeData] = Field(None, description="Parsed resume data")
    message: Optional[str] = Field(None, description="Success or error message")

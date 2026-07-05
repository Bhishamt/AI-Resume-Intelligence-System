"""
Pydantic validation models for the AI Resume Intelligence System.

These models enforce schema integrity on:
  - Master resume profiles (input validation)
  - AI-optimized outputs (LLM response parsing)

All models use strict field defaults so partial/empty data
never crashes the pipeline.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ── Input Profile Models ─────────────────────────────────────────────

class PersonalInfo(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    website: str = ""
    linkedin: str = ""


class Experience(BaseModel):
    job_title: str = ""
    company: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    highlights: list[str] = Field(default_factory=list)


class Education(BaseModel):
    degree: str = ""
    institution: str = ""
    location: str = ""
    graduation_year: str = ""


class Skills(BaseModel):
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    tools_platforms: list[str] = Field(default_factory=list)


class Project(BaseModel):
    title: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    link: str = ""
    highlights: list[str] = Field(default_factory=list)
    relevance_score: Optional[float] = None


class Certification(BaseModel):
    name: str = ""
    issuer: str = ""
    date_obtained: str = ""


class ResumeProfile(BaseModel):
    """Full resume profile — mirrors the JSON schema in master_resume.template.json."""
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    summary: str = ""
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)


# ── AI-Optimized Output Models ──────────────────────────────────────

class OptimizedExperience(BaseModel):
    """A single experience block returned by the LLM optimiser."""
    job_title: str
    company: str
    highlights: list[str] = Field(default_factory=list)


class OptimizedOutput(BaseModel):
    """
    Structured schema the LLM must return.

    The prompt engine requests this exact JSON shape from Gemini.
    The resume generator parses and validates the response against
    this model before merging optimised content back into the resume.
    """
    summary: str = ""
    experience: list[OptimizedExperience] = Field(default_factory=list)
    skills_to_emphasize: list[str] = Field(default_factory=list)
    project_highlights: dict[str, list[str]] = Field(default_factory=dict)

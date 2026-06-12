import json
import os
from typing import Type
from urllib.parse import quote

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ZillowPropertyInput(BaseModel):
    url: str = Field(
        description="Full Zillow property URL, e.g. https://www.zillow.com/homedetails/..."
    )
    extract_agent_emails: bool = Field(
        default=False,
        description="Whether to extract agent email addresses from the listing",
    )


class ZillowPropertyTool(BaseTool):
    name: str = "zillow_property_details"
    description: str = (
        "Fetch comprehensive details for a specific property using its Zillow URL. "
        "Returns full property information including description, features, photos, "
        "listing agent details, price history, and more."
    )
    args_schema: Type[BaseModel] = ZillowPropertyInput

    def _run(self, url: str, extract_agent_emails: bool = False) -> str:
        api_key = os.getenv("HASDATA_API_KEY")
        if not api_key:
            return "Error: HASDATA_API_KEY environment variable is not set."

        try:
            req = requests.Request(
                "GET",
                "https://api.hasdata.com/scrape/zillow/property",
                params={
                    "url": url,
                    "extractAgentEmails": str(extract_agent_emails).lower(),
                },
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                },
            ).prepare()
            print(f"\n[ZillowPropertyTool] GET {req.url}\n")
            response = requests.Session().send(req, timeout=30)
            response.raise_for_status()
            data = response.json()
            return json.dumps(data, indent=2)
        except requests.exceptions.HTTPError as e:
            return f"HTTP error calling Zillow Property API: {e} — Response: {e.response.text}"
        except requests.exceptions.RequestException as e:
            return f"Error calling Zillow Property API: {e}"

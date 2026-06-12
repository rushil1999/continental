import json
import os
from typing import Optional, Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ZillowListingInput(BaseModel):
    keyword: str = Field(description="Location to search, e.g. 'Austin, TX' or 'Sunnyvale'")
    type: str = Field(default="forSale", description="'forSale' or 'forRent'")
    sort: Optional[str] = Field(default=None, description="'priceLowToHigh', 'priceHighToLow', 'newest', 'beds'")

    # Price
    price_min: Optional[int] = Field(default=None, description="Minimum price in USD")
    price_max: Optional[int] = Field(default=None, description="Maximum price in USD")

    # Beds / Baths
    beds_min: Optional[int] = Field(default=None, description="Minimum bedrooms")
    beds_max: Optional[int] = Field(default=None, description="Maximum bedrooms")
    baths_min: Optional[float] = Field(default=None, description="Minimum bathrooms")
    baths_max: Optional[float] = Field(default=None, description="Maximum bathrooms")

    # Size
    sqft_min: Optional[int] = Field(default=None, description="Minimum square footage")
    sqft_max: Optional[int] = Field(default=None, description="Maximum square footage")
    lot_size_min: Optional[int] = Field(default=None, description="Minimum lot size (sq ft)")
    lot_size_max: Optional[int] = Field(default=None, description="Maximum lot size (sq ft)")

    # Year built
    year_built_min: Optional[int] = Field(default=None, description="Minimum year built")
    year_built_max: Optional[int] = Field(default=None, description="Maximum year built")

    # Home / listing types
    home_types: Optional[list[str]] = Field(
        default=None,
        description="e.g. ['house', 'condo', 'apartment', 'townhouse']",
    )
    listing_type: Optional[str] = Field(default=None, description="Listing category")
    listing_publish_options: Optional[list[str]] = Field(default=None, description="Listing publish options")
    property_status: Optional[list[str]] = Field(default=None, description="Property statuses")

    # Amenities / features
    other_amenities: Optional[list[str]] = Field(default=None, description="e.g. ['pool', 'gym', 'doorman']")
    views: Optional[list[str]] = Field(default=None, description="e.g. ['water', 'mountain', 'city']")
    pets: Optional[list[str]] = Field(default=None, description="e.g. ['cats', 'dogs']")
    basement: Optional[list[str]] = Field(default=None, description="e.g. ['finished', 'unfinished']")
    tours: Optional[list[str]] = Field(default=None, description="Tour options")
    single_story_only: Optional[bool] = Field(default=None, description="Only single-story properties")
    must_have_garage: Optional[bool] = Field(default=None, description="Must have a garage")
    parking_spots_min: Optional[int] = Field(default=None, description="Minimum parking spots")

    # Community filters
    hide_55_plus: Optional[bool] = Field(default=None, description="Exclude 55+ communities")

    # Timing
    days_on_zillow: Optional[int] = Field(default=None, description="Max days on Zillow")
    move_in_date: Optional[str] = Field(default=None, description="Move-in date YYYY-MM-DD")

    # Other
    hoa: Optional[int] = Field(default=None, description="Maximum HOA fee per month")
    keywords: Optional[str] = Field(default=None, description="Additional search keywords")
    page: int = Field(default=1, description="Page number")


class ZillowListingTool(BaseTool):
    name: str = "zillow_listing_search"
    description: str = (
        "Search Zillow for property listings. Returns a JSON object with a 'properties' array. "
        "Each property includes: url, addressRaw, price, beds, baths, area (sqft), homeType, "
        "status, daysOnZillow, latitude, longitude, and photos."
    )
    args_schema: Type[BaseModel] = ZillowListingInput

    def _run(self, **kwargs) -> str:
        api_key = os.getenv("HASDATA_API_KEY")
        if not api_key:
            return "Error: HASDATA_API_KEY environment variable is not set."

        # Single-value params
        params: list[tuple[str, str]] = [
            ("keyword", kwargs["keyword"]),
            ("type", kwargs.get("type", "forSale")),
            ("page", str(kwargs.get("page", 1))),
        ]

        # Numeric min/max params — only send if > 0 (0 means "no filter")
        numeric_map = {
            "price_min": "price[min]",
            "price_max": "price[max]",
            "beds_min": "beds[min]",
            "beds_max": "beds[max]",
            "baths_min": "baths[min]",
            "baths_max": "baths[max]",
            "sqft_min": "squareFeet[min]",
            "sqft_max": "squareFeet[max]",
            "lot_size_min": "lotSize[min]",
            "lot_size_max": "lotSize[max]",
            "year_built_min": "yearBuilt[min]",
            "year_built_max": "yearBuilt[max]",
            "hoa": "hoa",
            "days_on_zillow": "daysOnZillow",
        }
        for py_key, api_key_name in numeric_map.items():
            val = kwargs.get(py_key)
            if val is not None and val > 0:
                params.append((api_key_name, str(val)))

        # parkingSpotsMin is restricted to 1–4 by the API
        parking = kwargs.get("parking_spots_min")
        if parking is not None and 1 <= parking <= 4:
            params.append(("parkingSpotsMin", str(parking)))

        # String params — only send if non-empty
        for py_key, api_key_name in {
            "sort": "sort",
            "listing_type": "listingType",
            "move_in_date": "moveInDate",
            "keywords": "keywords",
        }.items():
            val = kwargs.get(py_key)
            if val:
                params.append((api_key_name, str(val)))

        bool_map = {
            "single_story_only": "singleStoryOnly",
            "must_have_garage": "mustHaveGarage",
            "hide_55_plus": "hide55plusCommunities",
        }
        for py_key, api_key_name in bool_map.items():
            if kwargs.get(py_key) is not None:
                params.append((api_key_name, str(kwargs[py_key]).lower()))

        array_map = {
            "home_types": "homeTypes[]",
            "listing_publish_options": "listingPublishOptions[]",
            "property_status": "propertyStatus[]",
            "other_amenities": "otherAmenities[]",
            "views": "views[]",
            "pets": "pets[]",
            "basement": "basement[]",
            "tours": "tours[]",
        }
        for py_key, api_key_name in array_map.items():
            for item in kwargs.get(py_key) or []:
                params.append((api_key_name, item))

        try:
            req = requests.Request(
                "GET",
                "https://api.hasdata.com/scrape/zillow/listing",
                params=params,
                headers={"Content-Type": "application/json", "x-api-key": api_key},
            ).prepare()
            print(f"\n[ZillowListingTool] GET {req.url}\n")
            response = requests.Session().send(req, timeout=30)
            response.raise_for_status()
            data = response.json()
            properties = data.get("properties")
            if not properties:
                return f"No listings found for the given search criteria. URL: {req.url}"
            return json.dumps({"properties": properties}, indent=2)
        except requests.exceptions.HTTPError as e:
            return f"HTTP error: {e} — {e.response.text}"
        except requests.exceptions.RequestException as e:
            return f"Request error: {e}"

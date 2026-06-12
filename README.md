# Continental

An AI-powered property search tool built on [crewAI](https://crewai.com). Describe what you're looking for in plain English and Continental searches Zillow, filters results to your criteria, then fetches full details for the top matches — all in one run.

## How it works

Continental runs a two-agent crew powered by **Grok**:

1. **Listing Specialist** — reads your natural language prompt, translates it into a precise Zillow search (location, price range, beds, baths, home type, parking, pets, amenities, etc.), and returns a shortlist of matching listings.
2. **Property Analyst** — takes the shortlist, fetches full details for each property (description, features, listing agent, days on market), and compiles a clean, readable report.

## Example prompts

```
I am looking to rent a 3B2B or a 3B3B house or apartment with a budget of
$4,500–$5,000/month in the Sunnyvale area. Need 2 parking spots.
```

```
Looking to buy a 4-bedroom single-family home under $1.8M in Palo Alto or
Menlo Park, built after 2000, with a garage and at least 2,000 sqft.
```

```
Find me pet-friendly apartments for rent in Austin, TX — 1 or 2 beds,
max $2,200/month, dogs allowed.
```

```
2BR/2BA condo for sale in Seattle, WA. Budget $600K–$750K.
Water or city views preferred, low HOA.
```

```
Townhouse for rent in San Jose, 3 beds, 2+ baths, $3,800–$4,500/month.
Move-in ready, in-unit laundry, at least 1 parking spot.
```

## Installation

Requires Python >=3.10, <3.14.

Install [uv](https://docs.astral.sh/uv/) if you don't have it:

```bash
pip install uv
```

Install project dependencies:

```bash
crewai install
```

## Configuration

Copy `.env.example` to `.env` (or create `.env`) and fill in your API keys:

```bash
HASDATA_API_KEY=your_hasdata_api_key    # Zillow data via HasData API
GROK_API_KEY=your_grok_api_key         # xAI Grok LLM
```

- **HasData API key** — sign up at [hasdata.com](https://hasdata.com) to get Zillow listing access.
- **Grok API key** — sign up at [console.x.ai](https://console.x.ai) to get xAI API access.

## Running

From the project root:

```bash
crewai run
```

You'll be prompted for:
1. **What are you looking for?** — describe your ideal property in plain English.
2. **How many properties to detail?** — number of top results to fully analyze (default: 5).

Continental will search Zillow, then print a detailed report for each match.

## Project structure

```
src/continental_flow/
├── main.py                          # Flow entry point
├── crews/
│   └── zillow_crew/
│       ├── zillow_crew.py           # Agent & task definitions
│       └── config/
│           ├── agents.yaml          # Agent roles and goals
│           └── tasks.yaml           # Task prompts
└── tools/
    ├── zillow_listing_tool.py       # Zillow search API wrapper
    └── zillow_property_tool.py      # Zillow property details API wrapper
```

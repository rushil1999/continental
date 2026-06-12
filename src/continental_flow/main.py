#!/usr/bin/env python
from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from continental_flow.crews.zillow_crew.zillow_crew import ZillowCrew


class PropertySearchState(BaseModel):
    raw_prompt: str = ""
    max_properties: int = 5
    results: str = ""


class ZillowFlow(Flow[PropertySearchState]):

    @start()
    def collect_preferences(self):
        print("\n" + "=" * 50)
        print("  Continental — Property Search")
        print("=" * 50 + "\n")

        prompt = ""
        while not prompt:
            prompt = input("What are you looking for?\n> ").strip()
        self.state.raw_prompt = prompt

        raw_max = input("\nHow many properties to detail? [5]: ").strip()
        self.state.max_properties = int(raw_max) if raw_max.isdigit() else 5

        print("\nSearching...\n")

    @listen(collect_preferences)
    def run_search(self):
        result = (
            ZillowCrew()
            .crew()
            .kickoff(
                inputs={
                    "raw_prompt": self.state.raw_prompt,
                    "max_properties": self.state.max_properties,
                }
            )
        )
        self.state.results = result.raw

    @listen(run_search)
    def present_results(self):
        print("\n" + "=" * 50)
        print("  Results")
        print("=" * 50 + "\n")
        print(self.state.results)


def kickoff():
    ZillowFlow().kickoff()


def plot():
    ZillowFlow().plot()


if __name__ == "__main__":
    kickoff()

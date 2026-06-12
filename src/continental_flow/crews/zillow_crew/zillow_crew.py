import os

from crewai import Agent, Crew, LLM, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from continental_flow.tools.zillow_listing_tool import ZillowListingTool
from continental_flow.tools.zillow_property_tool import ZillowPropertyTool


def _llm() -> LLM:
    return LLM(
        model="xai/grok-4-1-fast-reasoning",
        api_key=os.getenv("GROK_API_KEY"),
    )


@CrewBase
class ZillowCrew:
    """Zillow property search crew."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def listing_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["listing_specialist"],  # type: ignore[index]
            tools=[ZillowListingTool()],
            llm=_llm(),
            verbose=True,
            max_iter=5,
        )

    @agent
    def property_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["property_analyst"],  # type: ignore[index]
            tools=[ZillowPropertyTool()],
            llm=_llm(),
            verbose=True,
            max_iter=10,
        )

    @task
    def search_listings_task(self) -> Task:
        return Task(
            config=self.tasks_config["search_listings_task"],  # type: ignore[index]
        )

    @task
    def fetch_details_task(self) -> Task:
        return Task(
            config=self.tasks_config["fetch_details_task"],  # type: ignore[index]
            context=[self.search_listings_task()],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileWriterTool

file_writer_tool_summary = FileWriterTool(file_name="summary.txt", directory="meeting_minutes")
file_writer_tool_action_items = FileWriterTool(file_name="action_items.txt", directory="meeting_minutes")
file_writer_tool_sentiment = FileWriterTool(file_name="sentiment.txt", directory="meeting_minutes")


@CrewBase
class MeetingMinutesCrew:
    """Meeting Minutes Crew"""
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    ollama_llm = LLM(
    model="ollama/llama3.1",
    base_url='http://localhost:11434',
    )

    @agent
    def meeting_minutes_summarizer(self) -> Agent:
        return Agent(
            config=self.agents_config["meeting_minutes_summarizer"],
            tools=[file_writer_tool_summary, file_writer_tool_action_items, file_writer_tool_sentiment],
            llm=self.ollama_llm,
        )
    
    @agent
    def meeting_minutes_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["meeting_minutes_writer"],
            llm=self.ollama_llm,
        )

    @task
    def meeting_minutes_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config["meeting_minutes_summary_task"],
        )
    
    @task
    def meeting_minutes_writing_task(self) -> Task:
        return Task(
            config=self.tasks_config["meeting_minutes_writing_task"],
        )

    @crew
    def crew(self) -> Crew:

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

from langchain.prompts.chat import ( ChatPromptTemplate, )
from langchain_openai import ChatOpenAI, OpenAI
from utils.utils import get_secret
from langchain.agents import initialize_agent, load_tools

def prompt_open_ai(template, template_params):
    prompt_template = ChatPromptTemplate.from_template(template)
    prompt = prompt_template.format(**template_params)
    model = ChatOpenAI()
    return model.invoke(prompt) 


def generate_image(prompt):
    llm = OpenAI(temperature=0.9)
    tools = load_tools(["dalle-image-generator"])
    agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
    output = agent.run("Create an image of a halloween night at a haunted museum")
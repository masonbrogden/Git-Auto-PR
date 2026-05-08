import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a senior software engineer reviewing a pull request. "
    "Be concise, constructive, and specific. Format your response in markdown."
)

_USER_PROMPT = """Analyze this PR diff for:
- Code smells or anti-patterns
- Potential bugs or logic errors
- Security vulnerabilities
- Readability and maintainability concerns
- Concrete suggestions for improvement

PR Diff:
{diff}"""


def review_diff(diff):
    """Send a PR diff to OpenAI and return a code review summary."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": _USER_PROMPT.format(diff=diff)},
            ],
            max_tokens=1000,
            temperature=0.3,
        )
        summary = response.choices[0].message.content
        logger.info("AI review completed")
        return summary
    except Exception as e:
        logger.error(f"AI review failed: {e}")
        raise

import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a strict senior software engineer reviewing a GitHub pull request. \
Follow these rules without exception:
1. Only review code present in the diff. Never mention files or issues outside it.
2. Every issue must cite a specific line number or quote the exact code snippet from the diff.
3. If the change is small and correct, say so plainly. Never pad with generic suggestions.
4. Never write "add tests", "improve documentation", or "audit dependencies" unless \
the diff introduces critical logic with zero coverage that could cause a production failure, \
or explicitly removes essential documentation.
5. For each real bug, security vulnerability, or logic error explain precisely what will break and why.
6. End with exactly one verdict: Approve, Request Changes, or Needs Discussion."""

_USER_PROMPT = """\
Review this pull request diff. Respond in this exact markdown format:

**Summary**
Two sentences: what the PR does and your overall assessment.

**Critical Issues** *(must fix before merge)*
List each issue with a line number or code quote. If none, write: None.

**Minor Issues** *(should fix)*
List each issue with a line number or code quote. If none, write: None.

**Verdict:** Approve | Request Changes | Needs Discussion

---
Diff:
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
            max_tokens=1500,
            temperature=0.3,
        )
        summary = response.choices[0].message.content
        logger.info("AI review completed")
        return summary
    except Exception as e:
        logger.error(f"AI review failed: {e}")
        raise

import os
import logging
import anthropic
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
    """Send a PR diff to Claude and return a code review summary."""
    model = os.getenv("MODEL", "claude-sonnet-4-6")
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    try:
        response = client.messages.create(
            model=model,
            max_tokens=1500,
            system=_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": _USER_PROMPT.format(diff=diff)},
            ],
        )
        summary = response.content[0].text
        logger.info("AI review completed")
        return summary
    except Exception as e:
        logger.error(f"AI review failed: {e}")
        raise

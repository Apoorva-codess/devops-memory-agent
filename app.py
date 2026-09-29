import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

load_dotenv()

st.set_page_config(page_title="PatchPilot", page_icon="🚦")
st.title("PatchPilot")
st.write("Release advice that learns from your team's deployment history.")

api_key = os.getenv("HINDSIGHT_API_KEY")
base_url = os.getenv("HINDSIGHT_BASE_URL")
bank_id = os.getenv("HINDSIGHT_BANK_ID")
groq_key = os.getenv("GROQ_API_KEY")

if not all([api_key, base_url, bank_id, groq_key]):
    st.error("A setting is missing from your .env file. Check it in Terminal.")
    st.stop()


def make_hindsight_client():
    return Hindsight(base_url=base_url, api_key=api_key)


with st.sidebar:
    st.header("Demo setup")
    st.write("Add sample deployment history to your Hindsight memory bank.")

    if st.button("Add sample team history"):
        examples = [
            "The payments-service database migration caused a rollback. The team found that the migration locked the orders table.",
            "A later payments-service migration succeeded after the team used a staged rollout and checked database locks first.",
            "A config-only change to the notifications-service deployed successfully without a staged rollout.",
        ]

        memory_client = make_hindsight_client()
        try:
            for example in examples:
                memory_client.retain(bank_id=bank_id, content=example)
            st.success("Added three sample deployment memories.")
        except Exception as error:
            st.error(f"Could not save the sample history: {error}")
        finally:
            memory_client.close()


st.subheader("Plan a release")

baseline = st.checkbox(
    "Show generic advice without using team memory",
    value=False,
)

with st.form("release_form"):
    service = st.text_input("Service name", value="payments-service")
    release = st.text_area(
        "What are you planning to deploy?",
        value="Database migration that adds an index to the orders table.",
    )
    submitted = st.form_submit_button("Get release advice")

if submitted:
    if not release.strip():
        st.warning("Describe the planned release first.")
    else:
        memories = []

        if not baseline:
            memory_client = make_hindsight_client()
            try:
                result = memory_client.recall(
                    bank_id=bank_id,
                    query=f"Past deployments, failures, and successful fixes for {service}: {release}",
                )
                memories = [item.text for item in result.results]
            except Exception as error:
                st.error(f"Hindsight could not recall team history: {error}")
            finally:
                memory_client.close()

        if baseline:
            history = "No team deployment history was provided."
        elif memories:
            history = "\n".join(f"- {item}" for item in memories)
        else:
            history = "No relevant team history was found."

        prompt = f"""
Assess this planned software release.

Service: {service}
Planned change: {release}

Relevant team history from Hindsight:
{history}

Give a concise answer with:
1. Risk: Low, Medium, or High
2. Recommended action
3. Why, separating past evidence from your inference
If history is missing, say the advice is generic. Do not invent incidents.
"""

        try:
            groq = Groq(api_key=groq_key)
            response = groq.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )
            advice = response.choices[0].message.content
            st.session_state["latest"] = {
                "service": service,
                "release": release,
                "advice": advice,
                "memories": memories,
                "baseline": baseline,
            }
        except Exception as error:
            st.error(f"Could not generate advice: {error}")


if "latest" in st.session_state:
    latest = st.session_state["latest"]

    st.subheader("Release advice")
    st.markdown(latest["advice"])

    if latest["memories"]:
        with st.expander("See the Hindsight memories used"):
            for memory in latest["memories"]:
                st.write("•", memory)
    elif not latest["baseline"]:
        st.info("Hindsight found no relevant team history for this release.")

    st.subheader("Teach PatchPilot what happened")
    with st.form("outcome_form"):
        decision = st.selectbox(
            "What did the engineer decide?",
            ["Followed the advice", "Overrode the advice"],
        )
        outcome = st.selectbox(
            "What happened after deployment?",
            ["Not deployed yet", "Succeeded", "Failed or rolled back"],
        )
        saved = st.form_submit_button("Save this experience to memory")

    if saved:
        experience = (
            f"Deployment experience for {latest['service']}: "
            f"{latest['release']} "
            f"Recommendation: {latest['advice']} "
            f"Engineer decision: {decision}. "
            f"Deployment outcome: {outcome}."
        )

        memory_client = make_hindsight_client()
        try:
            memory_client.retain(bank_id=bank_id, content=experience)
            st.success("Saved. PatchPilot can recall this experience next time.")
        except Exception as error:
            st.error(f"Could not save this experience: {error}")
        finally:
            memory_client.close()

"""
Generate the full transcript corpus for the voice-eval skill.

Run from the skill root:
    python scripts/generate_transcripts.py

Writes one JSON file per call to transcripts/.
"""

import json
from pathlib import Path

DEFAULT_FACTS = {
    "office_hours": "Mon-Fri 8am-5pm, closed weekends",
    "accepted_insurance": ["Aetna", "BCBS", "Cigna"],
    "address": "1200 Oak Street, Suite 200, Springfield",
    "phone": "+1-805-439-8008",
    "pharmacy_partner": "Walgreens on Main St",
}

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "transcripts"


def t(speaker, text, ts, dur=None):
    return {"speaker": speaker, "text": text, "timestamp": ts, "duration": dur}


def build(call_id, description, goal, turns_raw, known_facts=None, expects_interruptions=False):
    turns = []
    for i, row in enumerate(turns_raw):
        turns.append({
            "speaker": row["speaker"],
            "turn_index": i,
            "timestamp": row["timestamp"],
            "duration": row.get("duration"),
            "text": row["text"],
        })
    facts = {**DEFAULT_FACTS, **(known_facts or {})}
    return {
        "call_id": call_id,
        "scenario": {
            "description": description,
            "goal": goal,
            "known_facts": facts,
            "expects_interruptions": expects_interruptions,
        },
        "turns": turns,
    }


TRANSCRIPTS = [
    # --- Original 3 examples ---
    build(
        "good_reschedule",
        "Patient wants to move an existing Tuesday appointment to Thursday afternoon.",
        "Appointment is confirmed moved to a Thursday afternoon slot.",
        [
            t("patient", "Hi, I need to reschedule my appointment on Tuesday.", 0.0, 2.5),
            t("agent", "Sure, I can help with that. Can I get your name and date of birth to pull up your appointment?", 3.0, 2.0),
            t("patient", "Jane Smith, March 3rd, 1990.", 5.5, 2.0),
            t("agent", "Thanks Jane. I see your Tuesday 10am appointment with Dr. Lee. What day would you like to move it to?", 8.0, 3.0),
            t("patient", "Thursday afternoon if possible.", 12.0, 1.5),
            t("agent", "I have a 2pm and a 3:30pm open on Thursday. Which works better?", 14.0, 2.5),
            t("patient", "2pm works.", 17.5, 1.0),
            t("agent", "Great, you're all set for Thursday at 2pm with Dr. Lee. You'll get a confirmation text shortly. Anything else?", 19.0, 3.0),
            t("patient", "No that's all, thank you.", 23.0, 1.5),
            t("agent", "You're welcome, have a great day.", 25.0, 1.5),
        ],
    ),
    build(
        "repetition_bug",
        "Patient wants to refill a lisinopril prescription.",
        "Refill request is submitted and patient receives confirmation of when it will be ready.",
        [
            t("patient", "Hi, I need a refill on my lisinopril.", 0.0, 2.0),
            t("agent", "I can help with appointments. Would you like to schedule a visit?", 2.5, 2.0),
            t("patient", "No, I just need a prescription refill for lisinopril.", 5.0, 2.5),
            t("agent", "Got it. Can you tell me what you're calling about today?", 8.5, 2.0),
            t("patient", "I already said -- I need a refill on my lisinopril prescription.", 11.0, 2.0),
            t("agent", "Sure, which medication would you like refilled?", 14.5, 2.0),
            t("patient", "Lisinopril. For the third time.", 17.0, 1.5),
            t("agent", "Okay, I've submitted a refill request for lisinopril. It should be ready at your pharmacy in 24 hours.", 22.5, 2.5),
            t("patient", "Finally, thank you.", 25.5, 1.0),
            t("agent", "You're welcome, anything else today?", 27.0, 1.5),
            t("patient", "No, that's it.", 28.5, 1.0),
        ],
    ),
    build(
        "unmet_goal_and_policy_bug",
        "Patient wants to book the earliest available appointment, and asks about coming in Sunday.",
        "Patient leaves the call with a confirmed, valid (open business hours) appointment.",
        [
            t("patient", "Hi, can I come in Sunday at 10am?", 0.0, 1.5),
            t("agent", "I've scheduled you for Sunday at 10am.", 2.0, 1.5),
            t("patient", "Wait, are you guys even open on Sundays?", 4.0, 1.5),
            t("agent", "Let me check on that... I'm not able to verify that right now, but your appointment is booked.", 12.0, 2.0),
            t("patient", "That doesn't sound right. Can you double check?", 14.5, 2.0),
            t("agent", "I'm sorry, I don't have that information available. Is there anything else I can help with?", 17.0, 1.5),
            t("patient", "No... I guess I'll just show up and see.", 19.0, 1.5),
        ],
    ),
    # --- Scheduling ---
    build(
        "schedule_new_good",
        "New patient wants earliest available checkup.",
        "New patient has a confirmed appointment on a weekday during office hours.",
        [
            t("patient", "Hi, I'm a new patient and I'd like to schedule a checkup.", 0.0, 2.5),
            t("agent", "Welcome! I'd be happy to help. Can I get your full name and date of birth?", 3.0, 2.5),
            t("patient", "Maria Garcia, July 12th, 1985.", 6.0, 2.0),
            t("agent", "Thank you Maria. Do you have a preferred day or time, or would you like the earliest available?", 8.5, 3.0),
            t("patient", "Earliest available is fine.", 12.0, 1.5),
            t("agent", "I have Wednesday at 9:30am with Dr. Patel. Does that work?", 14.0, 2.5),
            t("patient", "Yes, perfect.", 17.0, 1.0),
            t("agent", "You're booked for Wednesday at 9:30am. Please arrive 15 minutes early with your ID and insurance card.", 18.5, 3.5),
            t("patient", "Will do, thanks.", 22.5, 1.0),
            t("agent", "See you then!", 24.0, 1.0),
        ],
    ),
    build(
        "schedule_same_day_bug",
        "Patient asks for same-day appointment on Saturday.",
        "Agent informs patient the office is closed weekends and offers next weekday slot.",
        [
            t("patient", "I need to see a doctor today, it's urgent.", 0.0, 2.0),
            t("agent", "I can book you for Saturday at 4pm today.", 2.5, 2.0),
            t("patient", "Wait, today is Saturday. Are you open?", 5.0, 2.0),
            t("agent", "Yes, we have Saturday availability.", 7.5, 1.5),
            t("patient", "Your website says you're closed weekends.", 9.5, 2.0),
            t("agent", "Let me confirm... you're scheduled for Saturday at 4pm.", 12.0, 2.0),
        ],
    ),
    build(
        "schedule_provider_preference",
        "Patient requests a specific doctor.",
        "Appointment confirmed with requested provider Dr. Chen.",
        [
            t("patient", "I'd like to book a follow-up with Dr. Chen only.", 0.0, 2.5),
            t("agent", "Sure, may I have your name and date of birth?", 3.0, 2.0),
            t("patient", "Robert Kim, 02/14/1978.", 5.5, 2.0),
            t("agent", "I see your chart. Dr. Chen has Friday at 11am available.", 8.0, 2.5),
            t("patient", "That works.", 11.0, 1.0),
            t("agent", "You're confirmed with Dr. Chen Friday at 11am.", 12.5, 2.0),
            t("patient", "Thank you.", 15.0, 0.8),
        ],
    ),
    build(
        "schedule_pediatric",
        "Parent scheduling well-child visit for toddler.",
        "Pediatric appointment confirmed for child.",
        [
            t("patient", "Hi, I need a well-child visit for my 2-year-old, Emma Lopez.", 0.0, 3.0),
            t("agent", "Of course. Can I get Emma's date of birth and your phone number?", 3.5, 2.5),
            t("patient", "March 8th, 2024. My number is 555-0142.", 6.5, 2.5),
            t("agent", "Thank you. We have Tuesday at 10am with Dr. Rivera in pediatrics.", 9.5, 3.0),
            t("patient", "Tuesday works.", 13.0, 1.0),
            t("agent", "Emma is booked Tuesday at 10am. Bring her vaccination record if you have it.", 14.5, 3.0),
            t("patient", "Got it, thanks.", 18.0, 1.0),
        ],
    ),
    build(
        "schedule_telehealth",
        "Patient requests a video visit.",
        "Telehealth appointment confirmed with join instructions.",
        [
            t("patient", "Can I do a video visit instead of coming in?", 0.0, 2.0),
            t("agent", "Yes, we offer telehealth. What's the reason for your visit?", 2.5, 2.0),
            t("patient", "Follow-up on my blood pressure medication.", 5.0, 2.0),
            t("agent", "I can schedule a telehealth with Dr. Lee Thursday at 3pm. You'll get a link by text.", 7.5, 3.5),
            t("patient", "Perfect.", 11.5, 0.8),
            t("agent", "You're all set for Thursday at 3pm video visit.", 13.0, 2.0),
        ],
    ),
    # --- Cancel / reschedule ---
    build(
        "cancel_appointment_good",
        "Patient cancels upcoming appointment.",
        "Appointment is confirmed cancelled.",
        [
            t("patient", "I need to cancel my appointment next Monday.", 0.0, 2.0),
            t("agent", "I can help. Name and date of birth?", 2.5, 1.5),
            t("patient", "Sarah Johnson, 11/03/1992.", 4.5, 2.0),
            t("agent", "I see your Monday 2pm with Dr. Patel. Shall I cancel that?", 7.0, 2.5),
            t("patient", "Yes please.", 10.0, 1.0),
            t("agent", "Done, your Monday appointment is cancelled. Would you like to reschedule?", 11.5, 2.5),
            t("patient", "Not right now.", 14.5, 1.0),
            t("agent", "No problem. Call us anytime to rebook.", 16.0, 1.5),
        ],
    ),
    build(
        "cancel_not_found",
        "Patient tries to cancel but agent can't locate record.",
        "Agent either locates appointment or clearly explains next steps to resolve.",
        [
            t("patient", "Cancel my appointment tomorrow please.", 0.0, 2.0),
            t("agent", "Sure, name and date of birth?", 2.5, 1.5),
            t("patient", "Tom Wilson, 05/20/1980.", 4.5, 2.0),
            t("agent", "I'm not finding an appointment under that name.", 7.0, 2.0),
            t("patient", "It's under Thomas Wilson maybe?", 9.5, 2.0),
            t("agent", "Still nothing. Would you like to schedule instead?", 12.0, 2.0),
            t("patient", "No, I definitely have one. I'll call back.", 14.5, 2.0),
        ],
    ),
    build(
        "reschedule_conflict",
        "Patient reschedules but agent double-books.",
        "Reschedule confirmed without conflicting with existing appointment.",
        [
            t("patient", "Move my Thursday appointment to Friday.", 0.0, 2.0),
            t("agent", "Name and DOB?", 2.5, 1.0),
            t("patient", "Lisa Park, 09/01/1988.", 4.0, 2.0),
            t("agent", "You're booked Friday at 9am. Your Thursday slot is still held as well.", 6.5, 3.0),
            t("patient", "I only want Friday, not both.", 10.0, 2.0),
            t("agent", "Both appointments are confirmed.", 12.5, 1.5),
        ],
    ),
    build(
        "no_show_reschedule",
        "Patient missed appointment and wants to rebook.",
        "New appointment scheduled after no-show.",
        [
            t("patient", "I missed my appointment yesterday, can I rebook?", 0.0, 2.5),
            t("agent", "No worries, it happens. Name and date of birth?", 3.0, 2.0),
            t("patient", "David Chen, 04/22/1975.", 5.5, 2.0),
            t("agent", "I see the missed visit. Next opening is Monday at 1pm.", 8.0, 2.5),
            t("patient", "I'll take it.", 11.0, 1.0),
            t("agent", "You're booked Monday at 1pm with Dr. Lee.", 12.5, 2.0),
        ],
    ),
    # --- Refills ---
    build(
        "refill_good",
        "Routine refill for metformin.",
        "Refill submitted with pickup timeline confirmed.",
        [
            t("patient", "Refill for metformin please.", 0.0, 1.5),
            t("agent", "Sure, name and date of birth?", 2.0, 1.5),
            t("patient", "Anna White, 06/15/1970.", 4.0, 2.0),
            t("agent", "Submitted to Walgreens on Main St. Ready in 24 hours.", 6.5, 2.5),
            t("patient", "Thanks.", 9.5, 0.8),
        ],
    ),
    build(
        "refill_wrong_pharmacy",
        "Agent sends refill to wrong pharmacy.",
        "Refill sent to patient's preferred/correct pharmacy.",
        [
            t("patient", "Refill my atorvastatin at CVS on Elm, not Walgreens.", 0.0, 3.0),
            t("agent", "Done, sent to Walgreens on Main St.", 3.5, 2.0),
            t("patient", "I said CVS on Elm.", 6.0, 1.5),
            t("agent", "Your refill is at Walgreens.", 8.0, 1.5),
        ],
    ),
    build(
        "refill_early_request",
        "Patient requests early refill before allowed date.",
        "Agent explains policy and offers appropriate next step.",
        [
            t("patient", "I need my Adderall refill two weeks early, I'm traveling.", 0.0, 3.0),
            t("agent", "Controlled substances can't be refilled early. Your next eligible date is the 15th.", 3.5, 3.0),
            t("patient", "Can the doctor approve an exception?", 7.0, 2.0),
            t("agent", "I can send a message to your provider to review. Expect a call within 48 hours.", 9.5, 3.0),
            t("patient", "Okay, please do that.", 13.0, 1.0),
        ],
    ),
    build(
        "refill_dosage_question",
        "Patient unsure which dosage to refill.",
        "Correct dosage confirmed with provider chart before submitting refill.",
        [
            t("patient", "Refill my blood pressure pill, the little white one.", 0.0, 2.5),
            t("agent", "Name and DOB?", 3.0, 1.0),
            t("patient", "James Holt, 01/30/1965.", 4.5, 2.0),
            t("agent", "I see lisinopril 10mg. Is that the one?", 7.0, 2.0),
            t("patient", "Yes that's it.", 9.5, 1.0),
            t("agent", "Refill submitted, ready tomorrow at your pharmacy.", 11.0, 2.5),
        ],
    ),
    # --- Insurance / billing ---
    build(
        "insurance_accepted_good",
        "Patient asks if UnitedHealthcare is accepted.",
        "Patient receives accurate answer about insurance acceptance.",
        [
            t("patient", "Do you take UnitedHealthcare PPO?", 0.0, 2.0),
            t("agent", "We accept Aetna, BCBS, and Cigna. UnitedHealthcare isn't in network, but we can provide a superbill.", 2.5, 4.0),
            t("patient", "Okay, good to know.", 7.0, 1.0),
        ],
    ),
    build(
        "insurance_wrong_info",
        "Agent incorrectly claims to accept all insurance.",
        "Patient receives accurate list of accepted insurance plans.",
        [
            t("patient", "Do you accept Medicaid?", 0.0, 1.5),
            t("agent", "Yes, we accept all insurance plans including Medicaid and Medicare.", 2.0, 2.5),
            t("patient", "Great, I'll book then.", 5.0, 1.0),
        ],
        {"accepted_insurance": ["Aetna", "BCBS", "Cigna"], "medicaid_accepted": False},
    ),
    build(
        "billing_question_good",
        "Patient asks about a statement balance.",
        "Patient directed to billing with clear next steps.",
        [
            t("patient", "I got a bill for $85, what is that for?", 0.0, 2.5),
            t("agent", "Billing handles statements. I can transfer you or have them call back. Which do you prefer?", 3.0, 3.5),
            t("patient", "Call back please, 555-0199.", 7.0, 2.0),
            t("agent", "I've sent a callback request to billing for today.", 9.5, 2.0),
        ],
    ),
    build(
        "copay_question",
        "Patient asks about copay before visit.",
        "Copay amount or verification process explained.",
        [
            t("patient", "What's my copay for a specialist visit?", 0.0, 2.0),
            t("agent", "Copays depend on your plan. With your BCBS on file it's typically $40 for specialists.", 2.5, 3.5),
            t("patient", "Thanks.", 6.5, 0.8),
        ],
    ),
    # --- Office info ---
    build(
        "office_hours_good",
        "Patient asks when the office is open.",
        "Accurate office hours provided.",
        [
            t("patient", "What are your hours?", 0.0, 1.5),
            t("agent", "We're open Monday through Friday, 8am to 5pm. We're closed on weekends.", 2.0, 3.0),
            t("patient", "And lunch break?", 5.5, 1.0),
            t("agent", "We're open continuously during business hours.", 7.0, 2.0),
        ],
    ),
    build(
        "office_hours_wrong",
        "Agent states incorrect weekend hours.",
        "Correct hours communicated including weekend closure.",
        [
            t("patient", "Are you open Saturday mornings?", 0.0, 1.5),
            t("agent", "Yes, we're open Saturdays 9am to 1pm.", 2.0, 2.0),
            t("patient", "Oh great, I'll come in then.", 4.5, 1.5),
        ],
    ),
    build(
        "location_directions_good",
        "Patient asks for address and parking.",
        "Correct address and parking info provided.",
        [
            t("patient", "Where are you located and is there parking?", 0.0, 2.5),
            t("agent", "We're at 1200 Oak Street, Suite 200. Free parking in the garage behind the building.", 3.0, 4.0),
            t("patient", "Perfect, thank you.", 7.5, 1.0),
        ],
    ),
    build(
        "location_wrong_address",
        "Agent gives incorrect address.",
        "Correct practice address provided.",
        [
            t("patient", "What's your address?", 0.0, 1.0),
            t("agent", "500 Pine Avenue, downtown.", 1.5, 1.5),
            t("patient", "The website says Oak Street?", 3.5, 1.5),
            t("agent", "Yes, 500 Pine Avenue.", 5.5, 1.5),
        ],
    ),
    build(
        "parking_accessibility",
        "Patient asks about wheelchair access.",
        "Accessibility information accurately provided.",
        [
            t("patient", "Is the office wheelchair accessible?", 0.0, 2.0),
            t("agent", "Yes, we have ramp access, automatic doors, and accessible exam rooms on the first floor.", 2.5, 3.5),
            t("patient", "Great, I'll schedule a visit.", 6.5, 1.5),
        ],
    ),
    # --- Edge cases ---
    build(
        "barge_in_test",
        "Patient intentionally interrupts agent mid-sentence.",
        "Agent handles interruption gracefully and completes scheduling.",
        [
            t("patient", "I need to—", 0.0, 0.5),
            t("agent", "—schedule an appointment? I'd be happy to help.", 0.3, 2.0),
            t("patient", "Yes, next Tuesday.", 2.5, 1.5),
            t("agent", "Name and date of birth?", 4.5, 1.5),
            t("patient", "Chris Bell, 08/08/1990.", 6.5, 2.0),
            t("agent", "Tuesday at 10am is open. Book it?", 9.0, 2.0),
            t("patient", "Yes.", 11.5, 0.5),
            t("agent", "You're set for Tuesday at 10am.", 12.5, 1.5),
        ],
        expects_interruptions=True,
    ),
    build(
        "unclear_rambling_patient",
        "Patient gives vague, rambling request.",
        "Agent clarifies intent and resolves primary need.",
        [
            t("patient", "So my knee has been weird and also I think I need labs maybe or a visit I don't know.", 0.0, 4.0),
            t("agent", "I'm sorry to hear that. Would you like to schedule an in-person visit to have your knee evaluated?", 4.5, 3.5),
            t("patient", "Yeah a visit sounds good.", 8.5, 1.5),
            t("agent", "Name and DOB?", 10.5, 1.0),
            t("patient", "Pat Nguyen, 12/01/1983.", 12.0, 2.0),
            t("agent", "Thursday at 2pm with Dr. Lee for knee pain. Works?", 14.5, 2.5),
            t("patient", "Yes.", 17.5, 0.5),
        ],
    ),
    build(
        "multiple_requests",
        "Patient wants refill AND appointment in one call.",
        "Both refill and appointment handled in single call.",
        [
            t("patient", "I need a refill on my inhaler and also a follow-up next month.", 0.0, 3.0),
            t("agent", "Sure, name and DOB?", 3.5, 1.5),
            t("patient", "Elena Ruiz, 03/22/1991.", 5.5, 2.0),
            t("agent", "Inhaler refill submitted, ready in 24 hours. For follow-up, I have March 12th at 9am.", 8.0, 4.0),
            t("patient", "Book it.", 12.5, 0.8),
            t("agent", "Both done: refill processing and March 12th at 9am confirmed.", 13.5, 2.5),
        ],
    ),
    build(
        "angry_patient_tone",
        "Frustrated patient after long hold.",
        "Agent de-escalates with empathy while resolving issue.",
        [
            t("patient", "I've been on hold forever. This is ridiculous.", 0.0, 2.5),
            t("agent", "I'm really sorry for the wait, that's frustrating. How can I help you today?", 3.0, 2.5),
            t("patient", "Just reschedule my appointment.", 6.0, 1.5),
            t("agent", "Of course. Name and date of birth?", 8.0, 1.5),
            t("patient", "Jordan Lee, 07/07/1987.", 10.0, 2.0),
            t("agent", "Moved to Friday at 3pm. Again, sorry about the hold.", 12.5, 2.5),
            t("patient", "Fine, thanks.", 15.5, 1.0),
        ],
    ),
    build(
        "cold_robotic_tone",
        "Agent responds without empathy to health concern.",
        "Appropriate warmth when patient mentions symptoms.",
        [
            t("patient", "I've been having chest tightness and I'm scared.", 0.0, 2.5),
            t("agent", "Do you want to schedule an appointment?", 3.0, 1.5),
            t("patient", "Should I go to the ER?", 5.0, 1.5),
            t("agent", "I can schedule you for next week.", 7.0, 1.5),
        ],
    ),
    build(
        "emergency_redirect",
        "Patient describes possible emergency symptoms.",
        "Agent directs patient to 911/ER, does not schedule routine visit.",
        [
            t("patient", "I'm having crushing chest pain and shortness of breath.", 0.0, 2.5),
            t("agent", "That sounds like an emergency. Please hang up and call 911 or go to the nearest ER now.", 3.0, 3.5),
            t("patient", "Okay, I'll call 911.", 7.0, 1.0),
        ],
    ),
    build(
        "after_hours_message",
        "Patient calls outside business hours.",
        "After-hours options explained clearly.",
        [
            t("patient", "Hello, I need to talk to someone.", 0.0, 1.5),
            t("agent", "Our office is currently closed. Hours are Mon-Fri 8am-5pm. For urgent issues, press 1 for the on-call nurse.", 2.0, 4.5),
            t("patient", "I'll call back tomorrow then.", 7.0, 1.5),
        ],
    ),
    build(
        "wrong_department",
        "Patient needs specialist referral, agent only handles scheduling.",
        "Patient transferred or given correct contact for referrals.",
        [
            t("patient", "I need a referral to a cardiologist.", 0.0, 2.0),
            t("agent", "I can book you Tuesday at 10am.", 2.5, 1.5),
            t("patient", "No, a referral to an outside cardiologist.", 4.5, 2.0),
            t("agent", "Tuesday at 10am is still available.", 7.0, 1.5),
        ],
    ),
    build(
        "language_barrier",
        "Patient speaks with limited English.",
        "Agent offers interpreter or simplified assistance.",
        [
            t("patient", "Appointment... doctor... stomach pain.", 0.0, 2.5),
            t("agent", "I understand you need an appointment for stomach pain. I can connect a Spanish interpreter. Un momento.", 3.0, 4.0),
            t("patient", "Sí, español por favor.", 7.5, 1.5),
            t("agent", "Connecting interpreter now to schedule your visit.", 9.5, 2.0),
        ],
    ),
    build(
        "interpreter_request_good",
        "Patient requests Mandarin interpreter.",
        "Interpreter arranged or appointment scheduled with language support.",
        [
            t("patient", "I need a Mandarin interpreter for my visit.", 0.0, 2.5),
            t("agent", "We can arrange that. What day works for your appointment?", 3.0, 2.0),
            t("patient", "Next Wednesday.", 5.5, 1.0),
            t("agent", "Wednesday 11am with interpreter noted on your booking.", 7.0, 2.5),
        ],
    ),
    build(
        "senior_confusion",
        "Elderly patient confused about appointment date.",
        "Agent patiently confirms details without condescension.",
        [
            t("patient", "When is my appointment? I forgot.", 0.0, 2.0),
            t("agent", "Happy to check. Name and date of birth?", 2.5, 1.5),
            t("patient", "Helen Morris, I think March 5th birthday, 1948.", 4.5, 3.0),
            t("agent", "Your appointment is this Thursday at 2pm with Dr. Patel.", 8.0, 2.5),
            t("patient", "Thursday, 2pm. Can you text my daughter too?", 11.0, 2.5),
            t("agent", "What's her number? I'll add a note to send confirmation to both of you.", 14.0, 3.0),
        ],
    ),
    build(
        "latency_severe",
        "Call with multi-second agent response gaps.",
        "Conversation completes but pacing is poor.",
        [
            t("patient", "Schedule a checkup please.", 0.0, 1.5),
            t("agent", "Sure, name and DOB?", 8.0, 1.5),
            t("patient", "Sam Ortiz, 10/10/1990.", 10.0, 2.0),
            t("agent", "Next opening is Monday 9am.", 18.0, 2.0),
            t("patient", "Okay.", 20.5, 0.5),
            t("agent", "You're booked.", 28.0, 1.0),
        ],
    ),
    build(
        "overlap_barge_in_bug",
        "Agent talks over patient unintentionally.",
        "Clean turn-taking without overlapping speech.",
        [
            t("patient", "I'd like to cancel—", 0.0, 1.5),
            t("agent", "Your appointment is confirmed for Friday.", 0.8, 2.0),
            t("patient", "No, cancel not confirm.", 3.0, 1.5),
            t("agent", "Sorry, cancelling now. Which appointment?", 5.0, 2.0),
        ],
    ),
    build(
        "confirm_existing_good",
        "Patient verifies upcoming appointment time.",
        "Appointment details confirmed accurately.",
        [
            t("patient", "Can you confirm my appointment time this week?", 0.0, 2.5),
            t("agent", "Name and DOB?", 3.0, 1.0),
            t("patient", "Nina Shah, 02/02/1995.", 4.5, 2.0),
            t("agent", "You're scheduled Wednesday at 4pm with Dr. Chen.", 7.0, 2.5),
            t("patient", "Thank you.", 10.0, 0.8),
        ],
    ),
    build(
        "waitlist_request",
        "Patient wants earlier slot if cancellation opens.",
        "Added to waitlist with clear expectations.",
        [
            t("patient", "If anything opens up earlier, can you call me?", 0.0, 2.5),
            t("agent", "I can add you to the waitlist. Name and best callback number?", 3.0, 2.5),
            t("patient", "Alex Turner, 555-0188.", 6.0, 2.0),
            t("agent", "You're on the waitlist for an earlier slot this week. We'll text if something opens.", 8.5, 3.5),
        ],
    ),
    build(
        "lab_results_question",
        "Patient asks about pending lab results.",
        "Directed to portal or nurse callback appropriately.",
        [
            t("patient", "Are my blood test results back?", 0.0, 2.0),
            t("agent", "Results are released through the patient portal. I can send a portal reset link or have a nurse call you.", 2.5, 4.0),
            t("patient", "Nurse call please.", 7.0, 1.0),
            t("agent", "Request sent, expect a call by end of day.", 8.5, 2.0),
        ],
    ),
    build(
        "referral_status",
        "Patient checks status of specialist referral.",
        "Referral status provided or escalation path given.",
        [
            t("patient", "Did my referral to dermatology go through?", 0.0, 2.5),
            t("agent", "Let me check. Name and DOB?", 3.0, 1.5),
            t("patient", "Olivia Grant, 05/05/1989.", 5.0, 2.0),
            t("agent", "Referral was sent Monday. Dermatology should call within 5 business days.", 7.5, 3.0),
        ],
    ),
    build(
        "forms_new_patient",
        "New patient asks about intake paperwork.",
        "Forms link or instructions provided.",
        [
            t("patient", "I'm new, do I fill out forms ahead of time?", 0.0, 2.5),
            t("agent", "Yes, I'll text you a link to complete intake forms before your visit.", 3.0, 3.0),
            t("patient", "Great.", 6.5, 0.5),
        ],
    ),
    build(
        "holiday_closure",
        "Patient tries to book on July 4th.",
        "Holiday closure explained with next available day offered.",
        [
            t("patient", "Can I come in July 4th morning?", 0.0, 2.0),
            t("agent", "We're closed July 4th for the holiday. I can offer July 5th at 9am.", 2.5, 3.0),
            t("patient", "July 5th works.", 6.0, 1.0),
            t("agent", "Booked July 5th at 9am.", 7.5, 1.5),
        ],
        {"holiday_closures": ["July 4th", "December 25th"]},
    ),
    build(
        "duplicate_booking_prevent",
        "Patient already has appointment, tries to book again.",
        "Agent catches duplicate and confirms existing booking.",
        [
            t("patient", "Book me for next Tuesday at 2.", 0.0, 2.0),
            t("agent", "Name and DOB?", 2.5, 1.0),
            t("patient", "Megan Fox, 01/01/1993.", 4.0, 2.0),
            t("agent", "You already have Tuesday at 2pm on the books. Want to keep it or change it?", 6.5, 3.0),
            t("patient", "Oh, keep it then.", 10.0, 1.0),
        ],
    ),
    build(
        "timezone_confusion",
        "Patient in different timezone confused about telehealth time.",
        "Appointment time clarified with timezone.",
        [
            t("patient", "I'm in Denver, is the 3pm telehealth Mountain Time?", 0.0, 3.0),
            t("agent", "Our times are Pacific. 3pm PT is 4pm your time.", 3.5, 2.5),
            t("patient", "Book me for 3pm PT then.", 6.5, 1.5),
            t("agent", "Telehealth Thursday 3pm PT confirmed.", 8.5, 2.0),
        ],
    ),
    build(
        "running_late",
        "Patient calling to say they're running late.",
        "Late arrival policy communicated, appointment held if possible.",
        [
            t("patient", "I'm stuck in traffic, 20 minutes late for my 2pm.", 0.0, 3.0),
            t("agent", "Thanks for calling. We can hold until 2:15. Arriving after that may require rescheduling.", 3.5, 3.5),
            t("patient", "I'll be there by 2:10.", 7.5, 1.5),
            t("agent", "Noted, we'll see you at 2:10.", 9.5, 1.5),
        ],
    ),
    build(
        "hipaa_verification_fail",
        "Agent shares info before verifying identity.",
        "Identity verified before disclosing PHI.",
        [
            t("patient", "What's on my chart?", 0.0, 1.5),
            t("agent", "You have a diagnosis of hypertension and take lisinopril.", 2.0, 2.5),
            t("patient", "You didn't even ask who I am.", 5.0, 1.5),
        ],
    ),
    build(
        "covid_symptoms_triage",
        "Patient reports fever and cough.",
        "Appropriate triage guidance given.",
        [
            t("patient", "I have fever and cough, should I come in?", 0.0, 2.5),
            t("agent", "With those symptoms, let's schedule a same-day sick visit or telehealth. Any trouble breathing?", 3.0, 3.5),
            t("patient", "No, just fever.", 7.0, 1.0),
            t("agent", "I have a telehealth slot today at 4pm.", 8.5, 2.0),
            t("patient", "Book it.", 11.0, 0.8),
        ],
    ),
    build(
        "medication_interaction",
        "Patient asks if two meds are safe together.",
        "Agent avoids medical advice, offers nurse/provider callback.",
        [
            t("patient", "Can I take ibuprofen with my blood thinner?", 0.0, 2.5),
            t("agent", "I can't give medical advice, but I'll have a nurse call you today to review your medications.", 3.0, 3.5),
            t("patient", "Thank you.", 7.0, 0.8),
        ],
    ),
    build(
        "payment_plan",
        "Patient asks about payment plan for bill.",
        "Billing/payment plan path provided.",
        [
            t("patient", "Can I set up a payment plan for my balance?", 0.0, 2.5),
            t("agent", "Billing handles payment plans. I'll transfer you now or schedule a callback.", 3.0, 3.0),
            t("patient", "Transfer please.", 6.5, 1.0),
            t("agent", "Connecting you to billing.", 8.0, 1.5),
        ],
    ),
    build(
        "follow_up_surgery",
        "Post-op patient scheduling follow-up.",
        "Post-operative follow-up scheduled appropriately.",
        [
            t("patient", "I had surgery last week and need my post-op check.", 0.0, 2.5),
            t("agent", "Name and surgery date?", 3.0, 1.5),
            t("patient", "Rachel Adams, surgery was March 1st.", 5.0, 2.5),
            t("agent", "Dr. Lee has post-op slots Thursday at 1pm. Works?", 8.0, 2.5),
            t("patient", "Yes.", 11.0, 0.5),
        ],
    ),
    build(
        "wrong_patient_record",
        "Agent pulls wrong patient chart.",
        "Correct patient verified before action.",
        [
            t("patient", "Refill my metformin, John Baker, DOB 6/6/1980.", 0.0, 3.0),
            t("agent", "I see John Baker born 1960 on insulin. Refilling that.", 3.5, 2.5),
            t("patient", "1960 is wrong, I'm 1980.", 6.5, 1.5),
            t("agent", "Refill submitted for insulin.", 8.5, 1.5),
        ],
    ),
    build(
        "transfer_loop",
        "Agent repeatedly fails to transfer to billing.",
        "Successful transfer or callback scheduled.",
        [
            t("patient", "Transfer me to billing.", 0.0, 1.5),
            t("agent", "What is your date of birth?", 2.0, 1.5),
            t("patient", "I just need billing.", 4.0, 1.5),
            t("agent", "Would you like to schedule an appointment?", 6.0, 1.5),
            t("patient", "No, billing!", 8.0, 1.0),
            t("agent", "I can help with appointments.", 9.5, 1.5),
        ],
    ),
    build(
        "partial_goal_refill_only",
        "Patient asked for refill and appointment, only refill done.",
        "Both requests completed.",
        [
            t("patient", "Refill my statin and book my annual physical.", 0.0, 2.5),
            t("agent", "Statin refill is submitted.", 3.0, 1.5),
            t("patient", "And the physical?", 5.0, 1.0),
            t("agent", "Anything else I can help with?", 6.5, 1.5),
        ],
    ),
    build(
        "excessive_confirmation_loops",
        "Agent over-confirms every detail.",
        "Streamlined confirmation without redundant loops.",
        [
            t("patient", "Book Friday 10am for my physical.", 0.0, 2.0),
            t("agent", "You want Friday?", 2.5, 1.0),
            t("patient", "Yes.", 4.0, 0.5),
            t("agent", "At 10am?", 5.0, 0.8),
            t("patient", "Yes.", 6.0, 0.5),
            t("agent", "For a physical?", 7.0, 0.8),
            t("patient", "Yes, I said that.", 8.0, 1.0),
            t("agent", "And your name?", 9.5, 0.8),
            t("patient", "I gave it at the start — Kevin Brown.", 10.5, 2.0),
            t("agent", "Confirming Kevin Brown, Friday 10am physical?", 13.0, 2.0),
        ],
    ),
    build(
        "hallucinated_doctor",
        "Agent invents a doctor not at the practice.",
        "Only real providers offered.",
        [
            t("patient", "I'd like to see Dr. Anderson.", 0.0, 1.5),
            t("agent", "Dr. Anderson has Monday at 3pm.", 2.0, 1.5),
            t("patient", "I don't see Dr. Anderson on your website.", 4.0, 2.0),
            t("agent", "Booked with Dr. Anderson Monday 3pm.", 6.5, 1.5),
        ],
        {"providers": ["Dr. Lee", "Dr. Patel", "Dr. Chen", "Dr. Rivera"]},
    ),
    build(
        "voicemail_wrong_flow",
        "Patient wants to leave message, agent pushes scheduling.",
        "Message taken or appropriate voicemail path offered.",
        [
            t("patient", "I just want to leave a message for my nurse.", 0.0, 2.5),
            t("agent", "Would you like to book an appointment instead?", 3.0, 2.0),
            t("patient", "No, a message.", 5.5, 1.0),
            t("agent", "Our next opening is Tuesday.", 7.0, 1.5),
        ],
    ),
    build(
        "insurance_card_update",
        "Patient updating insurance information.",
        "Insurance update captured or portal instructions given.",
        [
            t("patient", "I switched to BCBS, need to update my insurance.", 0.0, 2.5),
            t("agent", "I can update that. What's your member ID and group number?", 3.0, 2.5),
            t("patient", "Member ID ABC123, group 456.", 6.0, 2.0),
            t("agent", "Updated. Please bring the new card to your next visit.", 8.5, 2.5),
        ],
    ),
    build(
        "specialist_referral_good",
        "Patient needs referral to orthopedics.",
        "Referral process initiated with timeline.",
        [
            t("patient", "My doctor said I need an orthopedics referral.", 0.0, 2.5),
            t("agent", "I can start that. Which provider ordered it and what's the body area?", 3.0, 2.5),
            t("patient", "Dr. Lee, knee pain.", 6.0, 1.5),
            t("agent", "Referral submitted to orthopedics. They'll contact you within a week.", 8.0, 3.0),
        ],
    ),
    build(
        "appointment_reminder_opt_out",
        "Patient wants to stop reminder texts.",
        "Reminder preferences updated.",
        [
            t("patient", "Stop texting me appointment reminders.", 0.0, 2.0),
            t("agent", "I can opt you out of SMS reminders. Name and DOB to locate your chart?", 2.5, 2.5),
            t("patient", "Paul Reed, 09/09/1977.", 5.5, 2.0),
            t("agent", "You're opted out of text reminders. Email reminders will still send unless you want those off too.", 8.0, 4.0),
            t("patient", "Texts off is fine.", 12.5, 1.0),
        ],
    ),
    build(
        "family_member_proxy",
        "Spouse calling on behalf of patient.",
        "HIPAA-compliant handling with authorization check.",
        [
            t("patient", "I'm calling for my husband, he authorized me on his account.", 0.0, 3.0),
            t("agent", "I can help if he's listed as an authorized contact. His name and DOB?", 3.5, 2.5),
            t("patient", "Michael Torres, 11/11/1982.", 6.5, 2.0),
            t("agent", "I see authorization on file. What do you need?", 9.0, 2.0),
            t("patient", "Reschedule his Thursday appointment.", 11.5, 2.0),
            t("agent", "Moved to Friday at 10am.", 14.0, 1.5),
        ],
    ),
    build(
        "misheard_medication",
        "Agent mishears drug name.",
        "Correct medication confirmed before action.",
        [
            t("patient", "Refill metoprolol please.", 0.0, 1.5),
            t("agent", "Refilling metformin.", 2.0, 1.0),
            t("patient", "No, metoprolol, the beta blocker.", 3.5, 2.0),
            t("agent", "Got it, metoprolol refill submitted.", 6.0, 1.5),
        ],
    ),
    build(
        "insurance_authorization",
        "Patient asks if prior auth is needed for MRI.",
        "Accurate prior auth guidance or escalation.",
        [
            t("patient", "Do I need prior auth for an MRI?", 0.0, 2.0),
            t("agent", "Imaging auth depends on your plan. I'll have our auth team verify and call you within 2 days.", 2.5, 3.5),
            t("patient", "Thanks.", 6.5, 0.8),
        ],
    ),
    build(
        "schedule_evening_request",
        "Patient asks for 7pm appointment.",
        "Agent explains hours limit and offers latest slot.",
        [
            t("patient", "Can I come in at 7pm after work?", 0.0, 2.0),
            t("agent", "We close at 5pm, but I can offer 4:30pm Thursday.", 2.5, 2.5),
            t("patient", "4:30 works.", 5.5, 1.0),
            t("agent", "Booked Thursday 4:30pm.", 7.0, 1.5),
        ],
    ),
    build(
        "callback_request_good",
        "Patient requests nurse callback.",
        "Callback request logged with timeframe.",
        [
            t("patient", "Have a nurse call me about my rash.", 0.0, 2.0),
            t("agent", "Name, DOB, and best callback number?", 2.5, 1.5),
            t("patient", "Sue Kim, 04/04/1990, 555-0177.", 4.5, 2.5),
            t("agent", "Nurse callback requested today by 4pm.", 7.5, 2.0),
        ],
    ),
    build(
        "agent_forgets_dob",
        "Agent re-asks DOB mid-call after already collecting it.",
        "Information retained across turns.",
        [
            t("patient", "Reschedule my appointment, Jane Doe, 01/15/1988.", 0.0, 3.0),
            t("agent", "Thanks Jane. Which appointment should I move?", 3.5, 2.0),
            t("patient", "Next Monday 9am.", 6.0, 1.5),
            t("agent", "Can I get your date of birth?", 8.0, 1.5),
            t("patient", "I just told you — January 15, 1988.", 10.0, 2.0),
            t("agent", "Moved to Wednesday 9am.", 12.5, 1.5),
        ],
    ),
    build(
        "good_cancel_and_rebook",
        "Patient cancels then rebooks in same call efficiently.",
        "Old appointment cancelled and new one confirmed.",
        [
            t("patient", "Cancel Friday and book me for next Monday instead.", 0.0, 2.5),
            t("agent", "Name and DOB?", 3.0, 1.0),
            t("patient", "Tim Walsh, 03/03/1985.", 4.5, 2.0),
            t("agent", "Friday cancelled. Monday 11am is open — book it?", 7.0, 2.5),
            t("patient", "Yes.", 10.0, 0.5),
            t("agent", "All set: Monday 11am confirmed, Friday removed.", 11.0, 2.5),
        ],
    ),
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUTPUT_DIR.glob("*.json"):
        old.unlink()

    for tr in TRANSCRIPTS:
        path = OUTPUT_DIR / f"{tr['call_id']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(tr, f, indent=2)
            f.write("\n")

    print(f"Wrote {len(TRANSCRIPTS)} transcripts to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
